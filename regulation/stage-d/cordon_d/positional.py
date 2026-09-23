"""Positional error of monitoring positives, measured as a population excess of removed crowns.

No crown is chosen as the recorded tree. For each positive that two regional orthophotos
bracket, every crown with removal's signature is found
across the whole chip: present in every held image before the finding and absent from
every held image after it. The same rule runs everywhere in the chip. Each such crown's
centre is placed relative to the recorded point, which is first corrected for the earlier
image's own shift from the ground.

Per source and release, the vanished crowns of all its positives are pooled into a radial
density (crowns per m2 in 1 m rings). Removals unrelated to the recorded tree make a
background density, read from an outer band of the same chips. The recorded trees show as
an excess over that background near the point. The release bound is the distance that
contains the excess: beyond it the remaining excess is indistinguishable from zero, and at
least `coverage` of the excess lies within it, both at the stated confidence under
resampling of positives. The release's largest imagery residual and the grid-to-ground
difference are added.

The image steps are deterministic functions of the stored chip bytes and the constants
below. The imagery term comes from the region's surveyed control points: each image
year's shift is fitted locally from the nearest ground-level control features, and only
the leave-one-out residual after that correction is carried.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import hypot
import statistics

import numpy as np

# --- fixed before measuring -----------------------------------------------------

PIXEL_M = 0.2                   # requested chip resolution for every image year
CHIP_HALF_M = 62.0              # removal chip: half its side
# The radial measurement. Crowns are counted, and ring areas taken, only in the chip interior
# (at least `interior_margin_m` inside every edge: the co-registration search plus a margin), so a
# ring's count and its area cover the same ground. The background band ends at the largest ring
# wholly inside every interior. `coverage` and `confidence` are the stated choice, not tuned.
RADIAL = {'ring_m': 1.0, 'interior_margin_m': 8.0, 'background_m': (30.0, 54.0),
          'coverage': 0.95, 'confidence': 0.95, 'resamples': 2000, 'seed': 20260922}
CONTROL_HALF_M = 15.0           # control chip
IMAGE_PARAMETERS = {
    'format': 'jpg', 'compressionQuality': 90, 'interpolation': 'RSP_BilinearInterpolation',
}
COREGISTRATION = {'band_pass_sigma_m': (0.4, 3.0), 'search_m': 6.0, 'margin_m': 8.0, 'min_ncc': 0.2}
CANOPY = {'smooth_m': 0.3, 'background_percentile': 75, 'background_window_m': 15.0,
          'background_grid_m': 1.0, 'dark_ratio': 0.72, 'opening_px': 2}
CROWNS = {'core_separation_m': 3.0, 'core_depth_m': 1.0, 'min_area_m2': 3.0}
CHANGE = {'ring_m': (1.0, 3.0), 'present_below': 0.8, 'absent_above': 0.9, 'min_pixels': 20,
          # absent also means no branch structure left: the crown's fine texture (|DoG 0.2 m -
          # 0.8 m| of brightness, median) at most this multiple of its ring's; a leafless or
          # pruned tree keeps branches and fails it, cleared ground passes
          'texture_sigma_m': (0.2, 0.8), 'texture_ratio_max': 1.2,
          # absent also means no canopy left on the crown's footprint, widened by the margin: a
          # pruned tree's regrowth or a tree the images place a little apart keeps canopy there
          'absent_margin_m': 0.6, 'absent_canopy_max': 0.1,
          # absent also means the earlier crown-in-ring pattern is gone: its best correlation with
          # the image within this residual shift stays below `persist_max`; standing trees the
          # images place 1-2 m apart are the commonest false removal
          'persist_search_m': 2.0, 'persist_max': 0.4,
          'min_width_m': 1.2}   # candidate crown's inscribed diameter; thinner objects are slivers
CONTROL = {'harris_sigma_m': 0.4, 'harris_k': 0.05, 'search_m': 5.0, 'neighbours': 8, 'min_years': 3,
           # every year's control chip is co-registered to the sharpest year's before the corner is sought
           'coregister_search_m': 5.0, 'coregister_margin_m': 5.4, 'response_percentile': 99,
           # a year whose control chip co-registers below this is not located at that vertex: below it
           # the year's offset departs from the vertex's other years by a median 1.7-4 m
           'min_ncc': 0.5,
           'ground_level': ('RECINZ', 'MURO', 'MURETTO', 'POZZO', 'CISTERNA', 'CONFINE', 'CANCELL',
                            'PILASTR', 'CORDOL', 'MARCIAPIED', 'CUNETTA', 'CANALE', 'PONTE')}
# Removal's signature: a candidate crown is present in every held image before the finding and
# absent from every held image after it. Where more than one image pair brackets the finding, the
# pair whose stated flight windows fall in the same season (window midpoints within this many days
# of the year) is preferred; otherwise the tightest bracket.
SAME_SEASON_DAYS = 45
NODATA_LIMIT = 0.02             # share of pure-black or pure-white chip pixels tolerated

# Regional orthophotos on the SIT Puglia ImageServers reached without the VPN. An image is
# placed before or after a finding by the flight days its publisher states for the ground
# under the chip (per tile, where the tile index states them), else by its stated flight
# window, else by the interval its acquisition documents fix, else by its year alone.
# Same-season preference reads the stated window only.
IMAGE_SERVICE = 'https://webapps.sit.puglia.it/arcgis/rest/services/BaseMaps/Ortofoto{year}/ImageServer'
IMAGES = {
    2011: {'window': (date(2011, 1, 1), date(2011, 6, 30)), 'extent': (492052.9, 4406925.6, 803373.4, 4678086.6),
           'window_source': 'RNDT r_puglia:9e81c5fe-e9ca-4bf2-aff8-25fc50f4fcda'},
    2013: {'window': None, 'extent': (492843.9, 4409269.1, 803373.4, 4675489.6)},
    2015: {'window': (date(2015, 5, 14), date(2015, 11, 7)), 'extent': (642429.5, 4409258.7, 801902.2, 4530406.3),
           'window_source': 'RNDT r_puglia:1de1e983-7933-4e2e-8865-b6128ac05e08'},
    2016: {'window': None, 'extent': (317373.0, 4380945.5, 969142.2, 4709386.9)},
    2019: {'window': None, 'extent': (407479.6, 4396493.4, 887014.0, 4688466.4)},
    # SIT metadata: AGEA's 2022 flight, reused by the Region; AGEA's tile index dates each tile
    2022: {'window': None, 'extent': (412252.2, 4394416.6, 882587.8, 4689070.4)},
    # No published flight days (SIT metadata and RNDT state none). InnovaPuglia awarded the
    # acquisition on 7 Jan 2023 (DIT/005/2023, CIG 9428158A1A) and the image is named 2023.
    2023: {'window': None, 'extent': (321650.6, 4394376.4, 973189.4, 4689913.6),
           'dated': (date(2023, 1, 7), date(2023, 12, 31)),
           'dated_source': 'InnovaPuglia DIT/005/2023 of 7 Jan 2023 (award, CIG 9428158A1A); image named 2023'},
}
# Tile indexes that state each tile's flight days (EPSG:32633 on query).
FLIGHT_TILES = {
    2022: 'https://geoportale.agea.gov.it/server/rest/services/AgEA/Quadro_Unione_2022/FeatureServer/42',
}
_TILE_CELL_M = 10000.0
_TILES: dict[int, dict] = {}    # year -> {cell: [(x0, y0, x1, y1, first, last)]}


def use_flight_tiles(year: int, tiles) -> None:
    """Install one year's tiles, (x0, y0, x1, y1, first_day, last_day), for `flown`."""
    index = {}
    for tile in tiles:
        x0, y0, x1, y1 = tile[:4]
        for i in range(int(x0 // _TILE_CELL_M), int(x1 // _TILE_CELL_M) + 1):
            for j in range(int(y0 // _TILE_CELL_M), int(y1 // _TILE_CELL_M) + 1):
                index.setdefault((i, j), []).append(tuple(tile))
    _TILES[year] = index


def flight_tiles(features) -> list:
    """Tiles from a tile index's features: each ring's box and its first and last flight day."""
    tiles = []
    for feature in features:
        days = sorted(date(int(d[:4]), int(d[4:6]), int(d[6:8]))
                      for d in (feature['attributes'].get('date_volo') or '').replace(' ', '').split(',') if d)
        points = [p for ring in feature['geometry']['rings'] for p in ring]
        if days and points:
            xs, ys = [p[0] for p in points], [p[1] for p in points]
            tiles.append((min(xs), min(ys), max(xs), max(ys), days[0], days[-1]))
    return tiles


def load_flight_tiles(root) -> None:
    """Install every retained tile index (corpus/sources/positional-reference/flights.json)."""
    import json
    from pathlib import Path
    from .store import blob_path, store_root
    path = Path(root) / 'corpus/sources/positional-reference/flights.json'
    store = store_root(Path(root))
    for year, entry in json.loads(path.read_text()).items():
        features = [f for page in entry['pages'] for f in json.loads(blob_path(store, page['sha256']).read_bytes())['features']]
        use_flight_tiles(int(year), flight_tiles(features))


def flown(year: int, east: float, north: float):
    """(first, last) flight day of an image over the chip at a point, or None where only the
    year is known. Where tiles are indexed, every tile the chip touches counts."""
    if year in _TILES:
        x0, y0, x1, y1 = east - CHIP_HALF_M, north - CHIP_HALF_M, east + CHIP_HALF_M, north + CHIP_HALF_M
        cell = (int(east // _TILE_CELL_M), int(north // _TILE_CELL_M))
        near = {t for di in (-1, 0, 1) for dj in (-1, 0, 1) for t in _TILES[year].get((cell[0] + di, cell[1] + dj), ())}
        touched = [t for t in near if t[0] <= x1 and t[2] >= x0 and t[1] <= y1 and t[3] >= y0]
        if touched:
            return min(t[4] for t in touched), max(t[5] for t in touched)
    return IMAGES[year]['window'] or IMAGES[year].get('dated')


def chip_request(year: int, east: float, north: float, half: float) -> dict:
    """The exact export a chip is acquired by; its parameters are its identity."""
    bbox = tuple(round(v, 2) for v in (east - half, north - half, east + half, north + half))
    size = int(round(2 * half / PIXEL_M))
    params = {'bbox': ','.join(f'{v:.2f}' for v in bbox), 'bboxSR': 32633, 'imageSR': 32633,
              'size': f'{size},{size}', **IMAGE_PARAMETERS, 'f': 'image'}
    return {'year': year, 'bbox': bbox, 'size': size, 'service': IMAGE_SERVICE.format(year=year), 'params': params}


def chip_key(request: dict) -> str:
    return f"{request['year']}|{','.join(f'{v:.2f}' for v in request['bbox'])}|{request['size']}"


# --- which positives the method reaches -----------------------------------------

def _before(year: int, event: date, east: float, north: float) -> bool:
    days = flown(year, east, north)
    return days[1] < event if days else year < event.year


def _after(year: int, event: date, east: float, north: float) -> bool:
    days = flown(year, east, north)
    return days[0] > event if days else year > event.year


def _covers(year: int, east: float, north: float) -> bool:
    x0, y0, x1, y1 = IMAGES[year]['extent']
    return x0 + CHIP_HALF_M <= east <= x1 - CHIP_HALF_M and y0 + CHIP_HALF_M <= north <= y1 - CHIP_HALF_M


def held(event: date, east: float, north: float):
    """(before, after): every image year covering the point flown wholly before / after the event.
    An image whose flight window contains the event is in neither."""
    before = [y for y in IMAGES if _covers(y, east, north) and _before(y, event, east, north)]
    after = [y for y in IMAGES if _covers(y, east, north) and _after(y, event, east, north)]
    return before, after


def same_season(a: int, b: int) -> bool:
    """Both images state a flight window and the windows' midpoints fall within
    `SAME_SEASON_DAYS` of each other in the year."""
    wa, wb = IMAGES[a]['window'], IMAGES[b]['window']
    if not wa or not wb:
        return False
    mid = [(w[0].timetuple().tm_yday + (w[1] - w[0]).days / 2) % 365 for w in (wa, wb)]
    gap = abs(mid[0] - mid[1])
    return min(gap, 365 - gap) <= SAME_SEASON_DAYS


def bracket(event: date, east: float, north: float):
    """The image pair candidates are detected in: among pairs bracketing the event, those of one
    season first, then the tightest bracket (latest before, earliest after)."""
    before, after = held(event, east, north)
    if not before or not after:
        return None
    pairs = [(b, a) for b in before for a in after]
    pool = [p for p in pairs if same_season(*p)] or pairs
    return min(pool, key=lambda p: (p[1] - p[0], -p[0]))


def release_of(releases, views, day: date | None) -> tuple[str, str]:
    """(source, release): the campaign release publishing the observation, else the SIT view year."""
    campaign = sorted(r for r in releases if r.lower().startswith('camp'))
    if campaign:
        name = campaign[0]
        return ('campaign-csv' if name.lower().endswith('.csv') else 'campaign-workbook'), name
    return 'sit', f'SIT {day.year if day else "undated"}'


# --- deterministic image steps --------------------------------------------------

def decode(data: bytes) -> np.ndarray:
    import pymupdf
    pixmap = pymupdf.Pixmap(data)
    array = np.frombuffer(pixmap.samples, np.uint8).reshape(pixmap.height, pixmap.width, pixmap.n)
    return array[..., :3].astype(np.float32)


def nodata_share(image: np.ndarray) -> float:
    return float(((image.max(axis=2) <= 1) | (image.min(axis=2) >= 254)).mean())


def _band_pass(image):
    from scipy import ndimage
    fine, coarse = COREGISTRATION['band_pass_sigma_m']
    v = image.mean(axis=2)
    return ndimage.gaussian_filter(v, fine / PIXEL_M) - ndimage.gaussian_filter(v, coarse / PIXEL_M)


def _ncc_search(a, b, margin, candidates):
    core = a[margin:-margin, margin:-margin]
    core = (core - core.mean()) / (core.std() + 1e-9)
    best = (-2.0, 0, 0)
    for dy, dx in candidates:
        window = b[margin - dy:b.shape[0] - margin - dy, margin - dx:b.shape[1] - margin - dx]
        window = (window - window.mean()) / (window.std() + 1e-9)
        score = float((core * window).mean())
        if score > best[0]:
            best = (score, dy, dx)
    return best


def coregister(earlier: np.ndarray, later: np.ndarray, coarse: int = 4, *, search_m: float | None = None,
               margin_m: float | None = None, reference=None):
    """Integer pixel shift (dy, dx) placing `later` on `earlier`, maximising the normalised
    cross-correlation of band-passed brightness over the chip interior.

    Exhaustive over the search window at `coarse` times the pixel, then exhaustive over
    the neighbouring coarse cell at full resolution.
    """
    a = _band_pass(earlier) if reference is None else reference   # `reference`: band-passed `earlier`
    b = _band_pass(later)
    s = int(round((search_m or COREGISTRATION['search_m']) / PIXEL_M))
    m = int(round((margin_m or COREGISTRATION['margin_m']) / PIXEL_M))
    h, w = (x - x % coarse for x in a.shape)
    small = [x[:h, :w].reshape(h // coarse, coarse, w // coarse, coarse).mean(axis=(1, 3)) for x in (a, b)]
    sc = -(-s // coarse)
    _, cy, cx = _ncc_search(*small, -(-m // coarse), [(y, x) for y in range(-sc, sc + 1) for x in range(-sc, sc + 1)])
    fine = [(y, x) for y in range(cy * coarse - coarse, cy * coarse + coarse + 1)
            for x in range(cx * coarse - coarse, cx * coarse + coarse + 1) if abs(y) <= s and abs(x) <= s]
    return _ncc_search(a, b, m, fine)


def shifted(array: np.ndarray, dy: int, dx: int, fill=np.nan) -> np.ndarray:
    out = np.full(array.shape, fill, dtype=np.float64 if fill is np.nan else array.dtype)
    h, w = array.shape[:2]
    out[max(0, dy):h + min(0, dy), max(0, dx):w + min(0, dx)] = \
        array[max(0, -dy):h + min(0, -dy), max(0, -dx):w + min(0, -dx)]
    return out


def canopy(image: np.ndarray) -> np.ndarray:
    """Pixels darker than their local open-ground background: crowns and their shadows."""
    from scipy import ndimage
    v = ndimage.gaussian_filter(image.mean(axis=2), CANOPY['smooth_m'] / PIXEL_M)
    step = int(round(CANOPY['background_grid_m'] / PIXEL_M))
    background = ndimage.percentile_filter(v[::step, ::step], CANOPY['background_percentile'],
                                           size=int(round(CANOPY['background_window_m'] / CANOPY['background_grid_m'])))
    background = ndimage.zoom(background, step, order=1)
    background = np.pad(background, ((0, max(0, v.shape[0] - background.shape[0])),
                                     (0, max(0, v.shape[1] - background.shape[1]))), mode='edge')
    mask = v < CANOPY['dark_ratio'] * background[:v.shape[0], :v.shape[1]]
    mask = ndimage.binary_opening(mask, iterations=CANOPY['opening_px'])
    return ndimage.binary_fill_holes(mask)


def crowns(mask: np.ndarray) -> np.ndarray:
    """Split canopy into crowns: each pixel joins the nearest crown core of its own patch."""
    from scipy import ndimage
    depth = ndimage.distance_transform_edt(mask)
    size = int(round(CROWNS['core_separation_m'] / PIXEL_M)) | 1
    cores = (ndimage.maximum_filter(depth, size=size) == depth) & (depth >= CROWNS['core_depth_m'] / PIXEL_M)
    patches, _ = ndimage.label(mask)
    markers, n = ndimage.label(ndimage.binary_dilation(cores) & mask)
    if n == 0:
        return patches
    _, (iy, ix) = ndimage.distance_transform_edt(markers == 0, return_indices=True)
    same = patches[iy, ix] == patches
    labels = np.where(mask & same, markers[iy, ix], 0)
    orphan = mask & ~same
    labels[orphan] = n + patches[orphan]
    _, labels = np.unique(labels, return_inverse=True)
    return labels.reshape(mask.shape)


def _contrast(v, inside, ring):
    """Median crown/ring ratio of `v`, or None where either holds too few valid pixels."""
    a, b = v[inside], v[ring]
    a, b = a[np.isfinite(a)], b[np.isfinite(b)]
    if a.size < CHANGE['min_pixels'] or b.size < CHANGE['min_pixels']:
        return None
    return float(np.median(a) / (np.median(b) + 1e-9))


def _texture(image):
    from scipy import ndimage
    fine, coarse = CHANGE['texture_sigma_m']
    v = image.mean(axis=2)
    return np.abs(ndimage.gaussian_filter(v, fine / PIXEL_M) - ndimage.gaussian_filter(v, coarse / PIXEL_M))


@dataclass(frozen=True)
class Crown:
    centre_m: float        # crown centroid to the corrected point
    near_m: float          # nearest crown pixel to the corrected point
    far_m: float           # farthest crown pixel to the corrected point
    area_m2: float
    before: float          # crown/ring brightness ratio in the earlier image
    after: float           # the same ratio in the co-registered later image
    edge: bool             # the crown touches the chip edge
    interior: bool         # the centroid lies in the chip interior, where crowns are counted
    row: float = 0.0       # crown centroid in the earlier chip (pixels), for inspection
    col: float = 0.0


def _layer(image: np.ndarray, shift: tuple[int, int]):
    """An image's smoothed brightness, fine texture and canopy, placed on the earlier chip."""
    from scipy import ndimage
    dy, dx = shift
    return (shifted(ndimage.gaussian_filter(image.mean(axis=2), 1.5), dy, dx),
            shifted(_texture(image), dy, dx),
            shifted(canopy(image).astype(np.float64), dy, dx, fill=0.0) > 0.5)


def _state(layer, crown, dilated, grown, box, footprint, canopy_mask=None):
    """(brightness ratio, texture ratio, canopy share) of one crown in `layer`, or None: the
    crown's pixels against its ring, and the share of its widened footprint that is canopy
    in `canopy_mask` (default: the layer's own)."""
    v, texture, mask = layer
    y0, y1, x0, x1 = box
    ring = dilated & ~grown & ~mask[y0:y1, x0:x1]
    brightness = _contrast(v[y0:y1, x0:x1], crown, ring)
    fine = _contrast(texture[y0:y1, x0:x1], crown, ring)
    share = float((mask if canopy_mask is None else canopy_mask)[y0:y1, x0:x1][footprint].mean())
    return None if brightness is None or fine is None else (brightness, fine, share)


def _persistence(v_before, v_other, rr, cc) -> float:
    """Largest correlation of the earlier image's brightness over one crown and its own ring
    (pixels `rr`, `cc`) with another image's, over small residual shifts. A standing tree keeps
    its dark-crown-in-bright-ring pattern whatever the radiometry; cleared ground loses it."""
    from scipy import fft
    a = v_before[rr, cc]
    a = (a - a.mean()) / (a.std() + 1e-9)
    h, w = v_other.shape
    s = int(round(CHANGE['persist_search_m'] / PIXEL_M))
    r0, c0 = int(rr.min()), int(cc.min())
    hh, ww = int(rr.max()) - r0 + 1, int(cc.max()) - c0 + 1
    region, x = np.zeros((hh, ww)), np.zeros((hh, ww))
    region[rr - r0, cc - c0] = 1.0
    x[rr - r0, cc - c0] = a
    # the other image over the region's box widened by the search; outside the chip is not held
    window = np.full((hh + 2 * s, ww + 2 * s), np.nan)
    in_chip = np.zeros(window.shape)
    ys, xs = max(0, r0 - s), max(0, c0 - s)
    ye, xe = min(h, r0 + hh + s), min(w, c0 + ww + s)
    window[ys - r0 + s:ye - r0 + s, xs - c0 + s:xe - c0 + s] = v_other[ys:ye, xs:xe]
    in_chip[ys - r0 + s:ye - r0 + s, xs - c0 + s:xe - c0 + s] = 1.0
    valid = np.isfinite(window)
    b = np.where(valid, window, 0.0)
    # every shift at once: out[i, j] sums template[p, q] * image[p + i, q + j] for shift (i - s, j - s).
    # The template is padded to the window's size; for i, j <= 2s no index wraps, so the circular
    # correlation equals the direct sum.
    shape = window.shape
    spectrum = {name: np.conj(fft.rfft2(t, shape)) for name, t in (('region', region), ('x', x))}
    over = lambda image, template: fft.irfft2(fft.rfft2(image) * spectrum[template], shape)[:2 * s + 1, :2 * s + 1]  # noqa: E731
    valid = valid.astype(float)
    inside = np.rint(over(in_chip, 'region'))
    count = np.rint(over(valid, 'region'))
    with np.errstate(divide='ignore', invalid='ignore'):
        mean_x = over(valid, 'x') / count
        mean_y = over(b, 'region') / count
        covariance = over(b, 'x') / count - mean_x * mean_y
        spread = np.sqrt(np.clip(over(b * b, 'region') / count - mean_y ** 2, 0, None))
        score = covariance / (spread + 1e-9)
    usable = (inside >= 0.9 * region.sum()) & (count >= CHANGE['min_pixels'])
    return float(score[usable].max()) if usable.any() else -1.0


def _present(state) -> bool:
    return state[0] < CHANGE['present_below']


def _absent(state) -> bool:
    return (state[0] > CHANGE['absent_above'] and state[1] <= CHANGE['texture_ratio_max']
            and state[2] <= CHANGE['absent_canopy_max'] and state[3] < CHANGE['persist_max'])


def vanished_crowns(earlier: np.ndarray, later: np.ndarray, shift: tuple[int, int],
                    point_px: tuple[float, float], others=()):
    """Every crown of the chip carrying removal's signature: present in `earlier` and absent
    from `later`, and in each of `others` — (relation, year, image, shift) with relation
    'before' or 'after' the finding — present if before and absent if after. Distances are
    taken from `point_px` (row, column in the earlier chip); they select nothing.

    Returns (vanished, rejected, undetermined): a crown that reappears or was absent
    earlier is rejected; one whose state cannot be read in some image is undetermined.
    """
    from scipy import ndimage
    primary = (_layer(earlier, (0, 0)), _layer(later, shift))
    layers = [(relation, year, _layer(image, s)) for relation, year, image, s in others]
    before_mask = primary[0][2]
    labels = crowns(before_mask)
    inner, outer = (int(round(r / PIXEL_M)) for r in CHANGE['ring_m'])
    margin = int(round(CHANGE['absent_margin_m'] / PIXEL_M))
    grown = ndimage.binary_dilation(before_mask, iterations=inner)
    h, w = before_mask.shape
    found, rejected, undetermined = [], [], []
    for index, window in enumerate(ndimage.find_objects(labels), 1):
        if window is None:
            continue
        # Work inside the crown's box padded by the ring; results equal the whole-chip ones.
        y0, y1 = max(0, window[0].start - outer - 1), min(h, window[0].stop + outer + 1)
        x0, x1 = max(0, window[1].start - outer - 1), min(w, window[1].stop + outer + 1)
        box = (y0, y1, x0, x1)
        crown = labels[y0:y1, x0:x1] == index
        area = float(crown.sum()) * PIXEL_M ** 2
        if area < CROWNS['min_area_m2']:
            continue
        rows, cols = np.nonzero(crown)
        rows, cols = rows + y0, cols + x0
        d = np.hypot(rows + 0.5 - point_px[0], cols + 0.5 - point_px[1]) * PIXEL_M
        dilated = ndimage.binary_dilation(crown, iterations=outer)
        footprint = ndimage.binary_dilation(crown, iterations=margin)
        grown_box = grown[y0:y1, x0:x1]
        # the primary ring also excludes the later image's canopy, as a removal leaves open ground
        ring_mask = primary[1][2]
        v_a, t_a, _ = primary[0]
        before = _state((v_a, t_a, ring_mask), crown, dilated, grown_box, box, footprint)
        after = _state(primary[1], crown, dilated, grown_box, box, footprint)
        if before is None or after is None:
            continue
        width = 2 * float(ndimage.distance_transform_edt(np.pad(crown, 1)).max()) * PIXEL_M
        if not (_present(before) and width >= CHANGE['min_width_m']):
            continue
        # the crown and its own ring, other crowns excluded, for the persistence correlation
        rr, cc = np.nonzero(dilated & ~(before_mask[y0:y1, x0:x1] & ~crown))
        rr, cc = rr + y0, cc + x0

        def absent(layer, state):
            # the correlation is computed only where the cheaper tests already read absence
            if state is None or not _absent(state + (-1.0,)):
                return False
            return _absent(state + (_persistence(v_a, layer[0], rr, cc),))

        if not absent(primary[1], after):
            continue
        edge = bool(rows.min() == 0 or cols.min() == 0 or rows.max() == h - 1 or cols.max() == w - 1)
        cy, cx = float(rows.mean()) + 0.5, float(cols.mean()) + 0.5
        inset = RADIAL['interior_margin_m'] / PIXEL_M
        record = Crown(round(float(np.hypot(cy - point_px[0], cx - point_px[1])) * PIXEL_M, 2),
                       round(float(d.min()), 2), round(float(d.max()) + PIXEL_M / 2, 2),
                       round(area, 1), round(before[0], 3), round(after[0], 3), edge,
                       bool(inset <= cy <= h - inset and inset <= cx <= w - inset),
                       round(cy - 0.5, 1), round(cx - 0.5, 1))
        verdict = 'candidate'
        for relation, year, layer in layers:
            state = _state(layer, crown, dilated, grown_box, box, footprint)
            if state is None:
                verdict = 'undetermined' if verdict == 'candidate' else verdict
                continue
            if not (_present(state) if relation == 'before' else absent(layer, state)):
                verdict = 'rejected'
                break
        {'candidate': found, 'rejected': rejected, 'undetermined': undetermined}[verdict].append(record)
    order = lambda c: c.centre_m  # noqa: E731
    return sorted(found, key=order), sorted(rejected, key=order), sorted(undetermined, key=order)


# --- the imagery term from surveyed control points ------------------------------

def ground_level(description: str) -> bool:
    text = (description or '').upper()
    return 'FABBRICAT' not in text and any(word in text for word in CONTROL['ground_level'])


def _harris(image: np.ndarray) -> np.ndarray:
    from scipy import ndimage
    v = image.mean(axis=2)
    sigma = CONTROL['harris_sigma_m'] / PIXEL_M
    gy, gx = np.gradient(ndimage.gaussian_filter(v, 1.0))
    sxx = ndimage.gaussian_filter(gx * gx, sigma)
    syy = ndimage.gaussian_filter(gy * gy, sigma)
    sxy = ndimage.gaussian_filter(gx * gy, sigma)
    return sxx * syy - sxy ** 2 - CONTROL['harris_k'] * (sxx + syy) ** 2


def locate_vertex(chips: dict) -> dict:
    """{year: (dx_m, dy_m)}: east/north from a surveyed vertex (each chip's centre) to the
    physical corner as each image year shows it.

    The corner is identified once for all years, not per year: every year's chip is
    co-registered to the sharpest year's, each year's corner response is normalised and
    placed on that chip, and the corner is the strongest point of the median response
    within the search radius. Each year's offset follows from its co-registration. A
    vertex with fewer than `min_years` usable years is not located.
    """
    import warnings
    usable = {y: im for y, im in chips.items() if nodata_share(im) <= NODATA_LIMIT}
    if len(usable) < CONTROL['min_years']:
        return {}
    reference = max(usable, key=lambda y: (float(np.var(_band_pass(usable[y]))), y))
    shifts = {reference: (0, 0)}
    for year, image in usable.items():
        if year != reference:
            score, dy, dx = coregister(usable[reference], image, search_m=CONTROL['coregister_search_m'],
                                       margin_m=CONTROL['coregister_margin_m'])
            if score >= CONTROL['min_ncc']:
                shifts[year] = (dy, dx)
    if len(shifts) < CONTROL['min_years']:
        return {}
    stack = []
    for year, (dy, dx) in shifts.items():
        response = np.clip(_harris(usable[year]), 0, None)
        response = response / (np.percentile(response, CONTROL['response_percentile']) + 1e-12)
        stack.append(shifted(response, dy, dx))
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning)
        consensus = np.nanmedian(np.stack(stack), axis=0)
    h, w = consensus.shape
    rows, cols = np.mgrid[:h, :w]
    inside = np.hypot(rows + 0.5 - h / 2, cols + 0.5 - w / 2) * PIXEL_M <= CONTROL['search_m']
    flat = np.where(inside & np.isfinite(consensus), consensus, -np.inf)
    if not np.isfinite(flat.max()) or flat.max() <= 0:
        return {}
    r, c = np.unravel_index(int(np.argmax(flat)), flat.shape)
    return {year: (round((c - dx + 0.5 - w / 2) * PIXEL_M, 3), round(-(r - dy + 0.5 - h / 2) * PIXEL_M, 3))
            for year, (dy, dx) in shifts.items()}


@dataclass(frozen=True)
class ControlOffset:
    vertex: str
    east: float
    north: float
    dx: float
    dy: float


def _neighbours(offsets, east, north, k, exclude=None):
    ranked = sorted((hypot(o.east - east, o.north - north), o.vertex, o) for o in offsets if o.vertex != exclude)
    return [o for _, _, o in ranked[:k]]


def local_shift(offsets, east: float, north: float, *, exclude=None):
    """Median shift of the k nearest located control features: the local correction."""
    near = _neighbours(offsets, east, north, CONTROL['neighbours'], exclude)
    if len(near) < 3:
        return None
    return statistics.median(o.dx for o in near), statistics.median(o.dy for o in near), near


def residuals(offsets) -> dict[str, float]:
    """Each control feature's leave-one-out residual after the local correction."""
    out = {}
    for o in offsets:
        fit = local_shift(offsets, o.east, o.north, exclude=o.vertex)
        if fit is not None:
            out[o.vertex] = round(hypot(o.dx - fit[0], o.dy - fit[1]), 3)
    return out


def imagery_term(offsets, loo: dict[str, float], east: float, north: float):
    """(dx, dy, residual, vertices): the local correction at a point and the largest
    leave-one-out residual among the control features that fitted it."""
    fit = local_shift(offsets, east, north)
    if fit is None:
        return None
    dx, dy, near = fit
    used = [o.vertex for o in near if o.vertex in loo]
    if not used:
        return None
    return dx, dy, max(loo[v] for v in used), tuple(o.vertex for o in near)


def grid_to_ground_m(east: float, north: float, distance_m: float) -> float:
    """The largest difference between a grid distance and its ground length at this point."""
    from pyproj import CRS, Proj
    lon, lat = Proj(CRS.from_epsg(32633))(east, north, inverse=True)
    factors = Proj(CRS.from_epsg(32633)).get_factors(lon, lat)
    return abs(factors.meridional_scale - 1) * distance_m if factors.meridional_scale else 0.0


# --- the monumental register as a falsifier -------------------------------------

REGISTER_REACH_M = 80.0         # register trees are read this far from a flagged positive


def register_refutes(east: float, north: float, error_m: float, trees) -> bool | None:
    """Whether the monumental register refutes a bound at a positive its publisher flags as a
    monumental olive. The flag says the plant is a registered tree; the bound says the plant
    stands within `error_m` of the point. No registered tree within `error_m` refutes the bound.
    A registered tree within it confirms nothing: proximity is not identity. None where the
    bound exceeds the register's reach."""
    if error_m > REGISTER_REACH_M:
        return None
    return not any(hypot(x - east, y - north) <= error_m for x, y in trees)


# --- per-positive reading -------------------------------------------------------

def ring_areas(point_px: tuple[float, float], shape: tuple[int, int]) -> list[float]:
    """Interior area (m2) of each `RADIAL` ring about `point_px`, out to the background band's
    outer edge. A crown is counted in a ring only where its centre lies in the same interior."""
    ring, inset = RADIAL['ring_m'], RADIAL['interior_margin_m'] / PIXEL_M
    rings = int(round(RADIAL['background_m'][1] / ring))
    h, w = shape
    rows, cols = np.mgrid[:h, :w] + 0.5
    inside = (rows >= inset) & (rows <= h - inset) & (cols >= inset) & (cols <= w - inset)
    index = (np.hypot(rows - point_px[0], cols - point_px[1])[inside] * PIXEL_M / ring).astype(int)
    area = np.bincount(index[index < rings], minlength=rings) * PIXEL_M ** 2
    return [round(float(a), 2) for a in area]


def measure(earlier: np.ndarray, later: np.ndarray, point_px: tuple[float, float],
            correction: tuple[float, float], others=()):
    """One positive's reading from its bracketing chips, every other held image, and the
    earlier image's correction.

    `point_px` is the recorded point in the earlier chip; `correction` is that image's
    fitted (east, north) shift of image content from ground. The point is moved by the
    shift so distances to crowns in the image are ground distances. `others` are
    (relation, year, image) for every other image held at the point, relation 'before' or
    'after' the finding. Returns ('counted', detail) with every crown of the chip carrying
    removal's signature and the interior ring areas about the corrected point, or
    ('unread', detail) with the cause. No crown is chosen as the recorded tree.
    """
    for image in (earlier, later):
        if nodata_share(image) > NODATA_LIMIT:
            return 'unread', {'cause': 'image has no data at the point'}
    reference = _band_pass(earlier)
    ncc, dy, dx = coregister(earlier, later, reference=reference)
    if ncc < COREGISTRATION['min_ncc']:
        return 'unread', {'cause': 'co-registration below threshold', 'ncc': round(ncc, 3)}
    registered, not_held = [], []
    for relation, year, image in others:
        if nodata_share(image) > NODATA_LIMIT:
            not_held.append(year)
            continue
        score, oy, ox = coregister(earlier, image, reference=reference)
        if score < COREGISTRATION['min_ncc']:
            return 'unread', {'cause': f'co-registration below threshold in {year}', 'ncc': round(score, 3)}
        registered.append((relation, year, image, (oy, ox)))
    corrected = (point_px[0] - correction[1] / PIXEL_M, point_px[1] + correction[0] / PIXEL_M)
    found, rejected, undetermined = vanished_crowns(earlier, later, (dy, dx), corrected, registered)
    return 'counted', {
        'ncc': round(ncc, 3), 'shift_px': [dy, dx], 'point_px': [round(v, 2) for v in corrected],
        'vanished': [c.__dict__ for c in found], 'rejected': len(rejected), 'undetermined': len(undetermined),
        'undetermined_interior': sum(c.interior for c in undetermined),
        'years_before': sorted(y for r, y, *_ in registered if r == 'before'),
        'years_after': sorted(y for r, y, *_ in registered if r == 'after'), 'not_held': sorted(not_held),
        'ring_area_m2': ring_areas(corrected, earlier.shape[:2])}


def radial_profile(detail: dict):
    """(counts, areas) per ring: interior vanished-crown centres and interior area."""
    areas = np.asarray(detail['ring_area_m2'], dtype=float)
    counts = np.zeros(len(areas))
    for crown in detail['vanished']:
        index = int(crown['centre_m'] / RADIAL['ring_m'])
        if crown['interior'] and index < len(areas):
            counts[index] += 1
    return counts, areas


# --- the release bound: signal over background -----------------------------------

def radial_bound(counts, areas) -> dict:
    """The distance that contains a release's excess of vanished crowns over background.

    `counts` and `areas` are (positives x rings). The background density is the pooled
    density in the background band. The excess in each inner ring is its count less the
    background density times its area; T(r) is the excess beyond distance r, up to the band.
    The bound is the smallest ring edge r beyond which T is indistinguishable from zero: no
    edge at or beyond r has T above zero under a one-sided simultaneous band over all ring
    edges at the stated confidence. The band comes from resampling positives with
    replacement (`resamples`, fixed seed), so crowns shared by one chip move together, and
    the background is re-estimated in each resample. With the bound come the upper limit of
    the excess left beyond it, in crowns and as a share of the excess: how much a release
    of this n could still hide there.

    No bound where the band's density is not flat (its inner and outer halves differ at the
    stated confidence), where the excess over background is not established, or where it
    reaches the band.
    """
    counts, areas = np.asarray(counts, dtype=float), np.asarray(areas, dtype=float)
    n = counts.shape[0]
    ring = RADIAL['ring_m']
    b0, b1 = (int(round(x / ring)) for x in RADIAL['background_m'])
    alpha = 1 - RADIAL['confidence']
    out = {'n': n, 'vanished_counted': int(counts.sum()), 'radius_m': None}
    if n == 0:
        return {**out, 'cause': 'no positive read'}
    rng = np.random.default_rng(RADIAL['seed'])
    weights = np.vstack([np.ones(n), rng.multinomial(n, np.full(n, 1 / n), size=RADIAL['resamples'])])
    C, A = weights @ counts, weights @ areas
    background = C[:, b0:b1].sum(axis=1) / A[:, b0:b1].sum(axis=1)
    excess = C[:, :b0] - background[:, None] * A[:, :b0]
    tail = np.cumsum(excess[:, ::-1], axis=1)[:, ::-1]           # T at ring edges 0 .. b0 - 1
    spread = tail[1:].std(axis=0)
    band = float(np.quantile(((tail[1:] - tail[0]) / spread).max(axis=1), RADIAL['confidence']))
    lower, upper = tail[0] - band * spread, tail[0] + band * spread
    half = (b0 + b1) // 2
    inner = C[:, b0:half].sum(axis=1) / A[:, b0:half].sum(axis=1)
    outer = C[:, half:b1].sum(axis=1) / A[:, half:b1].sum(axis=1)
    flat = inner / outer
    out.update({
        'background_per_m2': float(background[0]),
        'background_ci': [float(np.quantile(background[1:], alpha / 2)), float(np.quantile(background[1:], 1 - alpha / 2))],
        'background_band_m': list(RADIAL['background_m']),
        'flatness_inner_over_outer': float(flat[0]),
        'flatness_ci': [float(np.quantile(flat[1:], alpha / 2)), float(np.quantile(flat[1:], 1 - alpha / 2))],
        'excess': float(tail[0, 0]), 'excess_lower': float(lower[0]), 'band_z': round(band, 3),
        'excess_profile': [round(float(x), 2) for x in excess[0]],
        'ring_counts': [int(x) for x in C[0]], 'ring_areas_m2': [round(float(x), 1) for x in A[0]]})
    if not (out['flatness_ci'][0] <= 1 <= out['flatness_ci'][1]):
        return {**out, 'cause': 'the background band is not flat'}
    if not lower[0] > 0:
        return {**out, 'cause': 'no excess of vanished crowns over background near the points'}
    radius = (int(np.nonzero(lower > 0)[0].max()) + 1) * ring
    out['significance_edge_m'] = radius
    if radius >= RADIAL['background_m'][0]:
        return {**out, 'cause': 'the excess reaches the background band'}
    k = int(round(radius / ring))
    left = max(0.0, float(upper[k]))
    return {**out, 'radius_m': radius, 'within_m': float(tail[0, 0] - tail[0, k]), 'beyond_upper': round(left, 1),
            'beyond_upper_share': round(left / float(tail[0, 0]), 4), 'cause': None}


def containment(counts, areas) -> dict:
    """The distance containing `coverage` of the excess over background, with its band from the
    same resampling of positives as `radial_bound`. Unlike the bound, its expected value does not
    grow with n, so releases of different size can be compared on it."""
    counts, areas = np.asarray(counts, dtype=float), np.asarray(areas, dtype=float)
    n = counts.shape[0]
    ring = RADIAL['ring_m']
    b0, b1 = (int(round(x / ring)) for x in RADIAL['background_m'])
    alpha = 1 - RADIAL['confidence']
    if n == 0:
        return {'containment_m': None, 'containment_band_m': None}
    rng = np.random.default_rng(RADIAL['seed'])
    weights = np.vstack([np.ones(n), rng.multinomial(n, np.full(n, 1 / n), size=RADIAL['resamples'])])
    C, A = weights @ counts, weights @ areas
    background = C[:, b0:b1].sum(axis=1) / A[:, b0:b1].sum(axis=1)
    cumulative = np.cumsum(C[:, :b0] - background[:, None] * A[:, :b0], axis=1)
    total = cumulative[:, -1]
    reached = cumulative >= RADIAL['coverage'] * total[:, None]
    radius = np.where(total > 0, (reached.argmax(axis=1) + 1) * ring, np.nan)
    valid = radius[1:][np.isfinite(radius[1:])]
    if not np.isfinite(radius[0]) or valid.size < 0.9 * RADIAL['resamples']:
        return {'containment_m': None, 'containment_band_m': None}
    return {'containment_m': float(radius[0]),
            'containment_band_m': [float(np.quantile(valid, alpha / 2)), float(np.quantile(valid, 1 - alpha / 2))]}


def stability(entries) -> dict:
    """Whether release containment radii are one process: every release band holds a common
    distance (the largest lower end does not exceed the smallest upper end)."""
    bands = {key: e['containment_band_m'] for key, e in entries.items() if e.get('containment_band_m')}
    if len(bands) < 2:
        return {'releases': len(bands), 'consistent': None, 'common_m': None}
    low, high = max(b[0] for b in bands.values()), min(b[1] for b in bands.values())
    outside = sorted('/'.join(k) for k, b in bands.items() if b[1] < low or b[0] > high) if low > high else []
    return {'releases': len(bands), 'consistent': bool(low <= high), 'common_m': [low, high] if low <= high else None,
            'widest_lower_m': low, 'narrowest_upper_m': high, 'apart': outside}


def program_bound(rows) -> dict:
    """The pooled bound over every counted positive of every release: data for the stability
    ruling. It qualifies no positive; `qualify` reads release bounds only."""
    pooled = [dict(r, source='program', release='all releases') for r in rows]
    return release_bounds(pooled)[('program', 'all releases')]


def release_bounds(rows):
    """Per (source, release): counts by status, the radial bound over its counted positives,
    and the bound = radius + largest imagery residual + grid-to-ground at the radius.

    `rows` are per-positive dicts with source, release, status ('counted', 'unread',
    'out_of_reach') and, when counted, the reading's vanished crowns and ring areas,
    imagery_m and grid_m_per_m.
    """
    groups = {}
    for row in rows:
        groups.setdefault((row['source'], row['release']), []).append(row)
    table = {}
    for key, members in groups.items():
        status = {s: sum(r['status'] == s for r in members) for s in ('counted', 'unread', 'out_of_reach')}
        counted = [r for r in members if r['status'] == 'counted']
        profiles = [radial_profile(r) for r in counted]
        entry = {**status, 'imagery_m': max((r['imagery_m'] for r in counted), default=None),
                 'grid_m_per_m': max((r['grid_m_per_m'] for r in counted), default=None)}
        if profiles:
            counts, areas = np.vstack([p[0] for p in profiles]), np.vstack([p[1] for p in profiles])
            entry.update(radial_bound(counts, areas))
            entry.update(containment(counts, areas))
        else:
            entry.update({'n': 0, 'radius_m': None, 'cause': 'no positive read'})
        entry['bound_m'] = None
        if entry['radius_m'] is not None:
            entry['grid_m'] = round(entry['grid_m_per_m'] * entry['radius_m'], 4)
            entry['bound_m'] = round(entry['radius_m'] + entry['imagery_m'] + entry['grid_m'], 2)
        table[key] = entry
    return table


def qualify(observation, result: dict, bounds: dict, *, context: str, event_date: date, sources):
    """The `SpatialQualification` for one located positive: its release's bound (Owen's
    ruling, 22 Sep 2026), stated with n and the method. A positive of a release with no
    bound has no qualification. `sources` are store-relative
    records of the chips, control points or bound document the reading rests on.
    """
    from cordon_c.core import MissingInput
    from .evidence import Support
    from .spatial import SpatialQualification
    source, release = result['source'], result['release']
    entry = bounds.get((source, release))
    if entry is None or entry.get('bound_m') is None:
        if result['status'] == 'out_of_reach' and 'image' in (result.get('cause') or ''):
            raise MissingInput('bracketing regional orthophotos for the positive')
        raise MissingInput(f"a positional bound for release {release}"
                           + (f": {entry['cause']}" if entry and entry.get('cause') else ''))
    low, high = RADIAL['background_m']
    reading = (f"Release bound of {release} ({source}): vanished crowns (present in every held orthophoto before "
               f"the finding, absent in every later one) around n={entry['n']} positives read, pooled by distance; "
               f"background {entry['background_per_m2']:.2e} per m2 from {low:g}-{high:g} m; excess over background "
               f"{entry['excess']:.0f} crowns, contained within {entry['radius_m']:g} m: beyond it the remaining "
               f"excess is indistinguishable from zero under a one-sided simultaneous {RADIAL['confidence']:.0%} band "
               f"over ring edges from resampling positives, and at most {entry['beyond_upper']:.0f} crowns "
               f"({entry['beyond_upper_share']:.0%} of the excess) at that confidence; plus the release's largest "
               f"imagery residual {entry['imagery_m']:.2f} m after control-point correction and grid-to-ground "
               f"{entry['grid_m']:.3f} m. It states where the release's recorded trees lie relative to their "
               f"points; it is not a guaranteed maximum for this positive.")
    sources = tuple(sources)
    return SpatialQualification(observation.occurrence, context, event_date, observation.crs, 'EPSG:32633',
                                round(float(entry['bound_m']), 2), sources,
                                tuple(Support(s.identity, 'whole record', reading) for s in sources))
