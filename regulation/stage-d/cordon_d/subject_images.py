"""Reproducible source-image measurements; a predicted crown is not a plant ID.

The fixed public DeepForest model reads only RGB pixels. No observation labels,
results, resampling notes or expected correspondences enter inference.
"""
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import json

from .store import blob_path, store_root


@dataclass(frozen=True)
class CrownCandidate:
    image: str
    ordinal: int
    edition: int
    crs: str
    bounds: tuple[float, float, float, float]
    score: float
    reader: str

    @property
    def identity(self):
        return self.image, self.reader, self.ordinal


def _verified(store, digest):
    path = blob_path(store, digest)
    if sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError('Subject image/model source hash mismatch')
    return path


def reader_version(root):
    model = (Path(root)/'corpus/sources/subject-imagery/model.json').read_bytes()
    packages = (Path(root)/'regulation/stage-d/subject-images-requirements.txt').read_bytes()
    return sha256(Path(__file__).read_bytes()+b'\0'+model+b'\0'+packages).hexdigest()[:20]


def reading_path(root, frame):
    metadata = json.dumps(frame,sort_keys=True,separators=(',',':')).encode()
    key = sha256(metadata).hexdigest()
    return store_root(root)/'derived/subject-images'/reader_version(root)/(key+'.json')


class CrownReader:
    """Run the published tree detector on CPU with its published configuration.

    Scores are detector outputs, not calibrated identity probabilities. The
    resulting rectangles retrieve possible depicted subjects; downstream evidence
    must establish what observation, grain and time actually belong to a subject.
    """
    def __init__(self, root):
        import torch
        import torchvision
        from importlib.metadata import version
        from safetensors.torch import load_file
        self.root = Path(root)
        self.packages = {}
        for line in (self.root/'regulation/stage-d/subject-images-requirements.txt').read_text().splitlines():
            if not line.strip() or line.startswith('#'):
                continue
            name, expected = line.split('==')
            actual = version(name)
            if actual != expected:
                raise ValueError(f'Image reader requires {name}=={expected}, found {actual}')
            self.packages[name] = actual
        self.store = store_root(root)
        record = json.loads((self.root/'corpus/sources/subject-imagery/model.json').read_text())
        paths = {f['name']:_verified(self.store,f['sha256']) for f in record['files']}
        # These are the published DeepForest prediction settings, verified from
        # the retained configuration, not fitted to a verification scene.
        config = paths['reader-config.yaml'].read_text()
        settings = {}
        for line in config.splitlines():
            if line and not line[0].isspace() and ':' in line:
                key, value = line.split(':',1)
                if key in {'nms_thresh','score_thresh','detections_per_img','topk_candidates'}:
                    settings[key] = float(value.strip()) if 'thresh' in key else int(value.strip())
        if set(settings) != {'nms_thresh','score_thresh','detections_per_img','topk_candidates'}:
            raise ValueError('Published detector configuration is incomplete')
        torch.set_num_threads(1)
        self.model = torchvision.models.detection.retinanet_resnet50_fpn(
            weights=None, weights_backbone=None, num_classes=1, **settings)
        state = load_file(str(paths['model.safetensors']))
        # The authors' documented legacy checkpoint-prefix migration.
        self.model.load_state_dict({k.removeprefix('model.'):v for k,v in state.items()},strict=True)
        self.model.to('cpu').eval()
        self.version = reader_version(root)

    def read(self, frame):
        import numpy as np
        from PIL import Image
        import torch
        source = _verified(self.store,frame['sha256'])
        with Image.open(source) as image:
            if image.size != (frame['width'],frame['height']):
                raise ValueError('Retained frame dimensions disagree with source pixels')
            pixels = np.array(image.convert('RGB'),dtype=np.float32)/255
        with torch.inference_mode():
            result = self.model([torch.from_numpy(pixels).permute(2,0,1)])[0]
        boxes = result['boxes'].tolist()
        scores = result['scores'].tolist()
        labels = result['labels'].tolist()
        if any(label != 0 for label in labels):
            raise ValueError('Unexpected class in the single-class tree model')
        output = dict(image=frame['sha256'],reader=self.version,packages=self.packages,
                      boxes=boxes,scores=scores,labels=labels)
        target = reading_path(self.root,frame)
        target.parent.mkdir(parents=True,exist_ok=True)
        temporary = target.with_suffix('.tmp')
        temporary.write_text(json.dumps(output,separators=(',',':'))+'\n')
        temporary.replace(target)
        return output


def crown_candidates(root, frame):
    """Consume a reproducible pixel reading, retaining its source and edition."""
    _verified(store_root(root),frame['sha256'])
    reading = json.loads(reading_path(root,frame).read_text())
    if reading['reader'] != reader_version(root) or reading['image'] != frame['sha256']:
        raise ValueError('Image reading provenance mismatch')
    if len(reading['boxes']) != len(reading['scores']):
        raise ValueError('Incomplete image-candidate reading')
    xmin,ymin,xmax,ymax = frame['extent']
    dx,dy = (xmax-xmin)/frame['width'],(ymax-ymin)/frame['height']
    for index,(box,score) in enumerate(zip(reading['boxes'],reading['scores'])):
        left,top,right,bottom = box
        if not (0 <= left < right <= frame['width'] and 0 <= top < bottom <= frame['height']):
            raise ValueError('Predicted rectangle is outside its source frame')
        yield CrownCandidate(frame['sha256'],index,frame['edition'],frame['crs'],
            (xmin+left*dx,ymax-bottom*dy,xmin+right*dx,ymax-top*dy),score,reading['reader'])
