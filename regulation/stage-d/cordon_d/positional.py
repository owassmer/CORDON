"""Positional error of monitoring positives, measured from the removed crown.

Identity comes from the removal, never from the nearest crown. For a positive under a
single-plant removal rule that falls between two regional orthophotos, the candidates
are every crown present in the earlier image and absent from the later one within
`SEARCH_RADIUS_M` of the recorded point. They are fixed before any distance is taken.
The positive's error is the distance from the recorded point to the far edge of the
farthest candidate, in ground coordinates corrected for the earlier image's own
systematic shift, plus that image's residual after the correction. A positive with no
candidate is unmeasured and stays in the counts.

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

SEARCH_RADIUS_M = 50.0          # the legal distance; candidates are sought within it
PIXEL_M = 0.2                   # requested chip resolution for every image year
CHIP_HALF_M = 62.0              # removal chip: radius plus a crown beyond it
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

# Regional orthophotos on the SIT Puglia ImageServers reached without the VPN. The flight
# window is stated where RNDT states it; otherwise the image year alone places it.
IMAGE_SERVICE = 'https://webapps.sit.puglia.it/arcgis/rest/services/BaseMaps/Ortofoto{year}/ImageServer'
IMAGES = {
    2011: {'window': (date(2011, 1, 1), date(2011, 6, 30)), 'extent': (492052.9, 4406925.6, 803373.4, 4678086.6),
           'window_source': 'RNDT r_puglia:9e81c5fe-e9ca-4bf2-aff8-25fc50f4fcda'},
    2013: {'window': None, 'extent': (492843.9, 4409269.1, 803373.4, 4675489.6)},
    2015: {'window': (date(2015, 5, 14), date(2015, 11, 7)), 'extent': (642429.5, 4409258.7, 801902.2, 4530406.3),
           'window_source': 'RNDT r_puglia:1de1e983-7933-4e2e-8865-b6128ac05e08'},
    2016: {'window': None, 'extent': (317373.0, 4380945.5, 969142.2, 4709386.9)},
    2019: {'window': None, 'extent': (407479.6, 4396493.4, 887014.0, 4688466.4)},
    2022: {'window': None, 'extent': (412252.2, 4394416.6, 882587.8, 4689070.4)},
    2023: {'window': None, 'extent': (321650.6, 4394376.4, 973189.4, 4689913.6)},
}


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

def _before(year: int, event: date) -> bool:
    window = IMAGES[year]['window']
    return window[1] < event if window else year < event.year


def _after(year: int, event: date) -> bool:
    window = IMAGES[year]['window']
    return window[0] > event if window else year > event.year


def _covers(year: int, east: float, north: float) -> bool:
    x0, y0, x1, y1 = IMAGES[year]['extent']
    return x0 + CHIP_HALF_M <= east <= x1 - CHIP_HALF_M and y0 + CHIP_HALF_M <= north <= y1 - CHIP_HALF_M


def held(event: date, east: float, north: float):
    """(before, after): every image year covering the point flown wholly before / after the event.
    An image whose flight window contains the event is in neither."""
    before = [y for y in IMAGES if _before(y, event) and _covers(y, east, north)]
    after = [y for y in IMAGES if _after(y, event) and _covers(y, east, north)]
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


def single_removal_rule(zone_labels, views) -> bool:
    """A positive whose publisher places it under removal of the infected plant alone:
    a containment-zone label, or publication in a removed-plant layer."""
    return (any('conten' in (z or '').lower() for z in zone_labels)
            or any('estirpat' in (v or '').lower() for v in views))


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
    near_m: float          # nearest crown pixel to the corrected point
    far_m: float           # farthest crown pixel to the corrected point
    area_m2: float
    before: float          # crown/ring brightness ratio in the earlier image
    after: float           # the same ratio in the co-registered later image
    edge: bool             # the crown touches the chip edge


def _layer(image: np.ndarray, shift: tuple[int, int]):
    """An image's smoothed brightness, fine texture and canopy, placed on the earlier chip."""
    from scipy import ndimage
    dy, dx = shift
    return (shifted(ndimage.gaussian_filter(image.mean(axis=2), 1.5), dy, dx),
            shifted(_texture(image), dy, dx),
            shifted(canopy(image).astype(np.float64), dy, dx, fill=0.0) > 0.5)


def _state(layer, crown, dilated, grown, box):
    """(brightness ratio, texture ratio) of one crown's pixels against its ring in `layer`, or None."""
    v, texture, mask = layer
    y0, y1, x0, x1 = box
    ring = dilated & ~grown & ~mask[y0:y1, x0:x1]
    brightness = _contrast(v[y0:y1, x0:x1], crown, ring)
    fine = _contrast(texture[y0:y1, x0:x1], crown, ring)
    return None if brightness is None or fine is None else (brightness, fine)


def _present(state) -> bool:
    return state[0] < CHANGE['present_below']


def _absent(state) -> bool:
    return state[0] > CHANGE['absent_above'] and state[1] <= CHANGE['texture_ratio_max']


def vanished_crowns(earlier: np.ndarray, later: np.ndarray, shift: tuple[int, int],
                    point_px: tuple[float, float], others=()):
    """Crowns carrying removal's signature, nearest pixel within the radius of `point_px`
    (row, column in the earlier chip): present in `earlier` and absent from `later`, and in
    each of `others` — (relation, year, image, shift) with relation 'before' or 'after' the
    finding — present if before and absent if after.

    Returns (candidates, rejected, undetermined): a crown that reappears or was absent
    earlier is rejected; one whose state cannot be read in some image is undetermined.
    """
    from scipy import ndimage
    primary = (_layer(earlier, (0, 0)), _layer(later, shift))
    layers = [(relation, year, _layer(image, s)) for relation, year, image, s in others]
    before_mask = primary[0][2]
    labels = crowns(before_mask)
    inner, outer = (int(round(r / PIXEL_M)) for r in CHANGE['ring_m'])
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
        if d.min() > SEARCH_RADIUS_M:
            continue
        dilated = ndimage.binary_dilation(crown, iterations=outer)
        grown_box = grown[y0:y1, x0:x1]
        # the primary ring also excludes the later image's canopy, as a removal leaves open ground
        ring_mask = primary[1][2]
        v_a, t_a, _ = primary[0]
        before = _state((v_a, t_a, ring_mask), crown, dilated, grown_box, box)
        after = _state(primary[1], crown, dilated, grown_box, box)
        if before is None or after is None:
            continue
        width = 2 * float(ndimage.distance_transform_edt(np.pad(crown, 1)).max()) * PIXEL_M
        if not (_present(before) and _absent(after) and width >= CHANGE['min_width_m']):
            continue
        edge = bool(rows.min() == 0 or cols.min() == 0 or rows.max() == h - 1 or cols.max() == w - 1)
        record = Crown(round(float(d.min()), 2), round(float(d.max()) + PIXEL_M / 2, 2),
                       round(area, 1), round(before[0], 3), round(after[0], 3), edge)
        verdict = 'candidate'
        for relation, year, layer in layers:
            state = _state(layer, crown, dilated, grown_box, box)
            if state is None:
                verdict = 'undetermined' if verdict == 'candidate' else verdict
                continue
            if not (_present(state) if relation == 'before' else _absent(state)):
                verdict = 'rejected'
                break
        {'candidate': found, 'rejected': rejected, 'undetermined': undetermined}[verdict].append(record)
    order = lambda c: c.near_m  # noqa: E731
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


# --- per-positive measurement and release bounds --------------------------------

def measure(earlier: np.ndarray, later: np.ndarray, point_px: tuple[float, float],
            correction: tuple[float, float], others=()):
    """One positive's measurement from its bracketing chips, every other held image, and the
    earlier image's correction.

    `point_px` is the recorded point in the earlier chip; `correction` is that image's
    fitted (east, north) shift of image content from ground. The point is moved by the
    shift so distances to crowns in the image are ground distances. `others` are
    (relation, year, image) for every other image held at the point, relation 'before' or
    'after' the finding. The candidate set is fixed by removal's signature before any
    candidate's distance is used. Returns (status, detail).
    """
    for image in (earlier, later):
        if nodata_share(image) > NODATA_LIMIT:
            return 'unmeasured', {'cause': 'image has no data at the point'}
    reference = _band_pass(earlier)
    ncc, dy, dx = coregister(earlier, later, reference=reference)
    if ncc < COREGISTRATION['min_ncc']:
        return 'unmeasured', {'cause': 'co-registration below threshold', 'ncc': round(ncc, 3)}
    registered, not_held = [], []
    for relation, year, image in others:
        if nodata_share(image) > NODATA_LIMIT:
            not_held.append(year)
            continue
        score, oy, ox = coregister(earlier, image, reference=reference)
        if score < COREGISTRATION['min_ncc']:
            return 'unmeasured', {'cause': f'co-registration below threshold in {year}', 'ncc': round(score, 3)}
        registered.append((relation, year, image, (oy, ox)))
    corrected = (point_px[0] - correction[1] / PIXEL_M, point_px[1] + correction[0] / PIXEL_M)
    found, rejected, undetermined = vanished_crowns(earlier, later, (dy, dx), corrected, registered)
    detail = {'ncc': round(ncc, 3), 'shift_px': [dy, dx], 'candidates': [c.__dict__ for c in found],
              'rejected': len(rejected), 'undetermined': len(undetermined),
              'years_before': sorted(y for r, y, *_ in registered if r == 'before'),
              'years_after': sorted(y for r, y, *_ in registered if r == 'after'), 'not_held': sorted(not_held)}
    if undetermined:
        return 'unmeasured', {**detail, 'cause': "a candidate's state is unreadable in a held image"}
    if not found:
        return 'unmeasured', {**detail, 'cause': "no crown carries removal's signature within the radius"}
    if any(c.edge for c in found):
        return 'unmeasured', {**detail, 'cause': 'a candidate crown crosses the chip edge'}
    detail['distance_m'] = max(c.far_m for c in found)
    return 'measured', detail


def release_bounds(rows):
    """Per (source, release): counts and the bound = max measured distance + imagery term.

    `rows` are per-positive dicts with source, release, status and, when measured,
    distance_m, imagery_m and grid_m. The imagery term is the largest carried by a
    measured positive of that release.
    """
    table = {}
    for row in rows:
        entry = table.setdefault((row['source'], row['release']),
                                 {'measured': 0, 'unmeasured': 0, 'out_of_reach': 0,
                                  'max_distance_m': None, 'imagery_m': None, 'grid_m': None})
        entry[row['status']] += 1
        if row['status'] == 'measured':
            for key, field in (('max_distance_m', 'distance_m'), ('imagery_m', 'imagery_m'), ('grid_m', 'grid_m')):
                entry[key] = max(entry[key] or 0.0, row[field])
    for entry in table.values():
        entry['bound_m'] = (round(entry['max_distance_m'] + entry['imagery_m'] + entry['grid_m'], 2)
                            if entry['measured'] else None)
    return table


def qualify(observation, result: dict, bounds: dict, *, context: str, event_date: date, sources):
    """The `SpatialQualification` for one located positive.

    A measured positive carries its own error: the farthest candidate's far edge, the
    earlier image's residual after its control-point correction, and grid-to-ground.
    An unmeasured positive carries its release's bound (Owen's ruling, 22 Sep 2026),
    stated with the measured n. An out-of-reach positive, or a release with no measured
    positive, has no qualification. `sources` are store-relative records of the chips,
    control points or bound document the reading rests on.
    """
    from cordon_c.core import MissingInput
    from .evidence import Support
    from .spatial import SpatialQualification
    key = (result['source'], result['release'])
    if result['status'] == 'measured':
        error = result['distance_m'] + result['imagery_m'] + result['grid_m']
        reading = (f"Removal identity: {len(result['candidates'])} crown(s) present in {result['pre']} and absent in "
                   f"{result['post']} within {SEARCH_RADIUS_M:g} m; farthest far edge {result['distance_m']:.2f} m after "
                   f"the {result['pre']} local control correction; imagery residual {result['imagery_m']:.2f} m; "
                   f"grid-to-ground {result['grid_m']:.3f} m.")
    elif result['status'] == 'unmeasured':
        entry = bounds.get(key)
        if entry is None or entry.get('bound_m') is None:
            raise MissingInput(f'a measured positional bound for release {key[1]}')
        error = entry['bound_m']
        reading = (f"Release bound of {key[1]} ({key[0]}): largest measured error {entry['max_distance_m']:.2f} m over "
                   f"n={entry['measured']} measured positives, plus imagery {entry['imagery_m']:.2f} m and grid "
                   f"{entry['grid_m']:.3f} m; applied to this unmeasured positive ({result.get('cause')}) by Owen's "
                   f"ruling of 22 Sep 2026. It is the release's largest measured error, not a guaranteed maximum.")
    else:
        raise MissingInput('bracketing regional orthophotos under a single-plant removal rule')
    sources = tuple(sources)
    return SpatialQualification(observation.occurrence, context, event_date, observation.crs, 'EPSG:32633',
                                round(float(error), 2), sources,
                                tuple(Support(s.identity, 'whole record', reading) for s in sources))
