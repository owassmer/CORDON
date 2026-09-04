#!/usr/bin/env python3
"""Generate the CORDON isometric landscape HTML. Only nodes that exist on disk or in verified session facts."""
from pathlib import Path

OUT = Path("/Users/owenwassmer/Desktop/Connor/olive-xylella/briefs/cordon-landscape-isometric.html")

# isometric: gx right, gy down-right, gz up
OX, OY = 780, 120


def iso(gx, gy, gz=0):
    x = OX + (gx - gy) * 46
    y = OY + (gx + gy) * 23 - gz * 18
    return x, y


def prism(gx, gy, gz, w, d, h, fill, stroke, title, lines, status=None):
    """w,d,h in grid units. Returns SVG group."""
    # 8 corners of a box sitting on (gx,gy) with height h
    def c(dx, dy, dz):
        return iso(gx + dx, gy + dy, gz + dz)

    t0, t1, t2, t3 = c(0, 0, h), c(w, 0, h), c(w, d, h), c(0, d, h)
    b0, b1, b2, b3 = c(0, 0, 0), c(w, 0, 0), c(w, d, 0), c(0, d, 0)
    def pts(*ps):
        return " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in ps)

    # darker left, mid right, light top
    left = f"rgba(0,0,0,0.25)"
    right = f"rgba(0,0,0,0.12)"
    parts = [
        f'<polygon points="{pts(t3, t2, b2, b3)}" fill="{fill}" stroke="{stroke}" stroke-width="1"/>',
        f'<polygon points="{pts(t3, t2, b2, b3)}" fill="{left}" />',
        f'<polygon points="{pts(t1, t2, b2, b1)}" fill="{fill}" stroke="{stroke}" stroke-width="1"/>',
        f'<polygon points="{pts(t1, t2, b2, b1)}" fill="{right}" />',
        f'<polygon points="{pts(t0, t1, t2, t3)}" fill="{fill}" stroke="{stroke}" stroke-width="1.4"/>',
    ]
    cx, cy = (t0[0] + t2[0]) / 2, (t0[1] + t2[1]) / 2 - 2
    parts.append(f'<text x="{cx:.1f}" y="{cy:.1f}" fill="#f8fafc" font-size="10" font-weight="600" text-anchor="middle">{title}</text>')
    for i, line in enumerate(lines):
        parts.append(
            f'<text x="{cx:.1f}" y="{cy + 12 + i * 10:.1f}" fill="#94a3b8" font-size="8" text-anchor="middle">{line}</text>'
        )
    if status:
        sc = {
            "LIVE": "#34d399",
            "BLOCKED": "#fb7185",
            "IN-FLIGHT": "#fbbf24",
            "UNVERIFIED": "#fb923c",
            "NOT BUILT": "#64748b",
            "ORACLE": "#a78bfa",
        }.get(status, "#94a3b8")
        parts.append(
            f'<text x="{cx:.1f}" y="{cy - 13:.1f}" fill="{sc}" font-size="7" font-weight="700" text-anchor="middle" letter-spacing="0.8">{status}</text>'
        )
    return "<g>" + "".join(parts) + "</g>"


def slab(gx, gy, w, d, label, stroke):
    p0, p1, p2, p3 = iso(gx, gy, 0), iso(gx + w, gy, 0), iso(gx + w, gy + d, 0), iso(gx, gy + d, 0)
    p0u, p1u, p2u, p3u = iso(gx, gy, 0.35), iso(gx + w, gy, 0.35), iso(gx + w, gy + d, 0.35), iso(gx, gy + d, 0.35)
    def pts(*ps):
        return " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in ps)
    lx, ly = iso(gx + 0.15, gy + 0.15, 0.55)
    return f'''<g>
      <polygon points="{pts(p3,p2,p2u,p3u)}" fill="rgba(15,23,42,0.9)" stroke="{stroke}" stroke-width="1"/>
      <polygon points="{pts(p1,p2,p2u,p1u)}" fill="rgba(15,23,42,0.85)" stroke="{stroke}" stroke-width="1"/>
      <polygon points="{pts(p0u,p1u,p2u,p3u)}" fill="rgba(15,23,42,0.55)" stroke="{stroke}" stroke-width="1.2" stroke-dasharray="6,4"/>
      <text x="{lx:.1f}" y="{ly:.1f}" fill="{stroke}" font-size="10" font-weight="700">{label}</text>
    </g>'''


def arrow(g1, g2, color="#64748b", dash=False):
    x1, y1 = iso(*g1)
    x2, y2 = iso(*g2)
    ds = ' stroke-dasharray="5,4"' if dash else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="1.3"{ds} marker-end="url(#ah)"/>'


# layout: gy increases toward camera
slabs = [
    slab(-1.2, -0.4, 8.2, 3.0, "L0  FIELD / BIOLOGY   Puglia · not Lecce on our labels", "#fb7185"),
    slab(7.6, -0.4, 7.6, 3.0, "L0b  CULTIVARS / RESISTANCE", "#34d399"),
    slab(-1.2, 3.1, 8.2, 2.8, "L1  OFFICIAL LABELS + LAW", "#a78bfa"),
    slab(7.6, 3.1, 7.6, 2.8, "L1b  SENSING", "#fbbf24"),
    slab(-1.2, 6.5, 8.2, 3.0, "L2  CORDON COMPUTE   ~/Desktop/Connor/olive-xylella", "#22d3ee"),
    slab(7.6, 6.5, 7.6, 3.0, "L2b  KNOWLEDGE + PARTNERS", "#94a3b8"),
    slab(-1.2, 10.1, 16.4, 2.6, "L3  ARTIFACTS · IN-FLIGHT · NOT YET", "#fb923c"),
]

boxes = [
    # L0 field
    prism(0.0, 0.3, 0.4, 2.2, 1.5, 1.4, "rgba(136,19,55,0.45)", "#fb7185",
          "Xfp ST53", ["pauca · CoDiRO", "xylem biofilm", "ST1/ST26 nearby"], "LIVE"),
    prism(2.5, 0.3, 0.4, 2.2, 1.5, 1.3, "rgba(136,19,55,0.4)", "#fb7185",
          "P. spumarius", ["meadow spittlebug", "tillage + spray", "Boscia: fewer?"], "LIVE"),
    prism(5.0, 0.3, 0.4, 1.8, 1.5, 1.1, "rgba(30,41,59,0.55)", "#94a3b8",
          "Hosts", ["olive + 36 spp", "almond cherry", "in same CAMP"], "ORACLE"),
    # cultivars
    prism(7.9, 0.3, 0.4, 2.3, 1.5, 1.2, "rgba(136,19,55,0.35)", "#fb7185",
          "Ogliarola / Cellina", ["native Salento", "high load", "dieback"], "LIVE"),
    prism(10.5, 0.3, 0.4, 2.3, 1.5, 1.5, "rgba(6,78,59,0.5)", "#34d399",
          "Leccino / FS-17", ["not immune", "67% progeny R/T", "S105 quiet"], "LIVE"),
    prism(13.1, 0.3, 0.4, 1.8, 1.5, 1.4, "rgba(6,78,59,0.45)", "#34d399",
          "S105 / S215", ["Leccino × Cipressino", "0 desiccation 24 mo", "not released"], "LIVE"),
    # L1 official
    prism(0.0, 3.6, 0.4, 2.6, 1.7, 1.8, "rgba(76,29,149,0.5)", "#a78bfa",
          "CAMP CSV", ["688,631 rows", "605k olives WGS84", "Lecce ABSENT"], "ORACLE"),
    prism(2.9, 3.6, 0.4, 2.0, 1.7, 1.4, "rgba(76,29,149,0.4)", "#a78bfa",
          "Class mix", ["pos 5,195", "0.86%", "2021:2861 → 2022:235"], "ORACLE"),
    prism(5.2, 3.6, 0.4, 1.6, 1.7, 1.2, "rgba(136,19,55,0.45)", "#fb7185",
          "emergenza", ["JOSSO SSO", "no polygons", "not needed"], "BLOCKED"),
    # sensing
    prism(7.9, 3.6, 0.4, 2.4, 1.7, 1.6, "rgba(120,53,15,0.4)", "#fbbf24",
          "Sentinel-2 L2A", ["Earth Search COGs", "tile 34TBL", "no CDSE key"], "LIVE"),
    prism(10.6, 3.6, 0.4, 2.2, 1.7, 1.5, "rgba(120,53,15,0.4)", "#fbbf24",
          "Scenes used", ["12 Aug 2021", "22 Aug +10d", "cloud 0.01 / 0.26%"], "LIVE"),
    prism(13.1, 3.6, 0.4, 1.8, 1.7, 1.3, "rgba(30,41,59,0.5)", "#94a3b8",
          "Zarco + REDoX", ["HS+T >80% qPCR", "REDoX 2022/25 OA≤86%", "not our plane"], "LIVE"),
    # L2 compute
    prism(0.0, 7.0, 0.4, 2.3, 1.8, 1.6, "rgba(8,51,68,0.5)", "#22d3ee",
          "join_one_scene", ["50/50 SCL-ok", "NDMI δ −0.31 p.008", "NDVI fail"], "LIVE"),
    prism(2.5, 7.0, 0.4, 2.2, 1.8, 1.5, "rgba(8,51,68,0.5)", "#22d3ee",
          "controls", ["NDMI|NDVI δ −0.38", "match p.006", "Aug22 δ −0.33"], "LIVE"),
    prism(4.9, 7.0, 0.4, 1.9, 1.8, 1.5, "rgba(6,78,59,0.45)", "#34d399",
          "decoder v0", ["OE9A013998T1", "FLA/PME/PL", "S105 quiet tx"], "LIVE"),
    # knowledge
    prism(7.9, 7.0, 0.4, 2.2, 1.8, 1.5, "rgba(30,41,59,0.55)", "#94a3b8",
          "Wiki", ["SCHEMA + index", "4 entities", "7 concepts"], "LIVE"),
    prism(10.3, 7.0, 0.4, 2.2, 1.8, 1.4, "rgba(30,41,59,0.55)", "#94a3b8",
          "Paper library", ["8 PDFs frozen", "2018 + EFSA in", "Montilon missing"], "LIVE"),
    prism(12.7, 7.0, 0.4, 2.2, 1.8, 1.5, "rgba(6,78,59,0.35)", "#34d399",
          "CNR-IPSP Bari", ["Saponari Boscia", "Giampetruzzi", "email NOT sent"], "NOT BUILT"),
    # L3 artifacts — all three challenge briefs on disk 15 Aug 13:03–13:13
    prism(0.0, 10.5, 0.4, 2.4, 1.6, 1.4, "rgba(6,78,59,0.4)", "#34d399",
          "interv. brief", ["305 lines", "C≠S≠T", "Dentamet / Kalex"], "LIVE"),
    prism(2.6, 10.5, 0.4, 2.4, 1.6, 1.4, "rgba(6,78,59,0.4)", "#34d399",
          "resist. brief", ["339 lines", "S105/S215 beat parent", "MATE2 in vitro"], "LIVE"),
    prism(5.2, 10.5, 0.4, 2.4, 1.6, 1.4, "rgba(6,78,59,0.4)", "#34d399",
          "detect. brief", ["404 lines", "F7 = Assente only", "Hornero incidence"], "LIVE"),
    prism(7.8, 10.5, 0.4, 2.4, 1.6, 1.1, "rgba(30,41,59,0.5)", "#64748b",
          "Nowcast v0", ["no EVAL.md", "F7 not run", "not a model"], "NOT BUILT"),
    prism(10.4, 10.5, 0.4, 2.4, 1.6, 1.1, "rgba(30,41,59,0.5)", "#64748b",
          "Bari letter", ["IT skeleton only", "empty hands rule"], "NOT BUILT"),
    prism(13.0, 10.5, 0.4, 2.0, 1.6, 1.2, "rgba(136,19,55,0.35)", "#fb7185",
          "SSO maps", ["human login", "optional"], "BLOCKED"),
]

# flow arrows in iso space (mid-tops)
arrows = [
    arrow((1.1, 1.8, 1.6), (1.3, 3.6, 1.6), "#fb7185"),
    arrow((8.9, 1.8, 1.6), (9.1, 3.6, 1.6), "#34d399"),
    arrow((1.3, 5.3, 1.8), (1.1, 7.0, 1.6), "#a78bfa"),
    arrow((9.1, 5.3, 1.6), (1.2, 7.0, 1.6), "#fbbf24"),
    arrow((1.1, 8.8, 1.6), (1.2, 10.5, 1.3), "#22d3ee"),
    arrow((5.8, 8.8, 1.4), (8.9, 10.5, 1.1), "#22d3ee", dash=True),
    arrow((13.8, 8.8, 1.5), (14.0, 10.5, 1.1), "#fb7185", dash=True),
]

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>CORDON — isometric research landscape</title>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet"/>
  <style>
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ font-family:'JetBrains Mono',monospace; background:#020617; color:#fff; min-height:100vh; padding:1.5rem; }}
    .container {{ max-width:1480px; margin:0 auto; }}
    .header-row {{ display:flex; align-items:center; gap:0.75rem; margin-bottom:0.35rem; }}
    .pulse-dot {{ width:11px; height:11px; background:#22d3ee; border-radius:50%; animation:pulse 2s infinite; }}
    @keyframes pulse {{ 0%,100%{{opacity:1}} 50%{{opacity:.4}} }}
    h1 {{ font-size:1.35rem; font-weight:700; letter-spacing:-0.03em; }}
    .subtitle {{ color:#94a3b8; font-size:0.78rem; margin:0 0 1.1rem 1.7rem; }}
    .diagram-container {{ background:rgba(15,23,42,.55); border:1px solid #1e293b; border-radius:1rem; padding:0.75rem; overflow-x:auto; }}
    svg {{ width:100%; min-width:1100px; display:block; }}
    .cards {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:0.85rem; margin-top:1.25rem; }}
    .card {{ background:rgba(15,23,42,.55); border:1px solid #1e293b; border-radius:.75rem; padding:1rem 1.1rem; }}
    .card-header {{ display:flex; align-items:center; gap:.45rem; margin-bottom:.55rem; }}
    .card-dot {{ width:8px; height:8px; border-radius:50%; }}
    .card-dot.cyan {{ background:#22d3ee; }}
    .card-dot.emerald {{ background:#34d399; }}
    .card-dot.violet {{ background:#a78bfa; }}
    .card-dot.amber {{ background:#fbbf24; }}
    .card-dot.rose {{ background:#fb7185; }}
    .card h3 {{ font-size:.8rem; font-weight:600; }}
    .card ul {{ list-style:none; color:#94a3b8; font-size:.7rem; }}
    .card li {{ margin-bottom:.28rem; }}
    .footer {{ text-align:center; margin-top:1.1rem; color:#475569; font-size:.7rem; }}
    .note {{ color:#64748b; font-size:.68rem; margin:0 0 .8rem 1.7rem; max-width:70rem; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header-row"><div class="pulse-dot"></div><h1>CORDON · isometric research landscape</h1></div>
    <p class="subtitle">Project CORDON — Apulian Xylella / olive front · snapshot 15 Aug 2026 · only nodes that exist on disk or were measured this session</p>
    <p class="note">Isometric stack, back → front: biology → official labels → sensing → our compute → artifacts. Three challenge briefs landed 13:03–13:13. Slate = contract artifact not built. Camera is south-east; Lecce is off the map on purpose (absent from CAMP).</p>
    <div class="diagram-container">
      <svg viewBox="0 0 1600 980">
        <defs>
          <marker id="ah" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
            <polygon points="0 0, 8 3, 0 6" fill="#64748b"/>
          </marker>
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.5"/>
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)"/>
        {''.join(arrows)}
        {''.join(slabs)}
        {''.join(boxes)}
        <g>
          <text x="48" y="40" fill="#e2e8f0" font-size="11" font-weight="700">STATUS</text>
          <text x="48" y="56" fill="#34d399" font-size="9">LIVE — measured or on disk</text>
          <text x="48" y="70" fill="#a78bfa" font-size="9">ORACLE — official PCR / law</text>
          <text x="48" y="84" fill="#fbbf24" font-size="9">IN-FLIGHT — delegate, no file</text>
          <text x="48" y="98" fill="#fb923c" font-size="9">UNVERIFIED — file exists, unread</text>
          <text x="48" y="112" fill="#64748b" font-size="9">NOT BUILT — contract remaining</text>
          <text x="48" y="126" fill="#fb7185" font-size="9">BLOCKED — SSO / human gate</text>
        </g>
      </svg>
    </div>
    <div class="cards">
      <div class="card">
        <div class="card-header"><div class="card-dot violet"></div><h3>What the labels actually are</h3></div>
        <ul>
          <li>• CAMP 688,631 rows · 20 Jan 2020–30 Jun 2023</li>
          <li>• 605,617 olives with lat/lon + PCR · tree-level</li>
          <li>• Lecce absent — this is the northern buffer</li>
          <li>• Olive + : 1976 / 2861 / 235 / 123 by year</li>
          <li>• Brindisi holds 4,018 of 5,195 olive positives</li>
        </ul>
      </div>
      <div class="card">
        <div class="card-header"><div class="card-dot cyan"></div><h3>What we measured</h3></div>
        <ul>
          <li>• 50/50 join on S2A_34TBL 12 Aug 2021</li>
          <li>• NDMI moves (δ −0.31, p=0.008); NDVI does not</li>
          <li>• NDMI|NDVI residual stronger (δ −0.38, p=0.0005)</li>
          <li>• Same points +10d: NDMI δ −0.33, p=0.004</li>
          <li>• Sample is Brindisi susceptibles, not Leccino</li>
        </ul>
      </div>
      <div class="card">
        <div class="card-header"><div class="card-dot emerald"></div><h3>What the papers already broke</h3></div>
        <ul>
          <li>• Ceiling: no commercial cultivar beats Leccino/FS-17</li>
          <li>• S105/S215 (unreleased) beat parent canopy at 24 mo</li>
          <li>• EFSA 2016 kills clearance (C), not S or T</li>
          <li>• Dentamet / Kalex / vector / replant are in the ground</li>
          <li>• F7: NDMI must hold on SINTOMO=Assente or it is incidence</li>
        </ul>
      </div>
      <div class="card">
        <div class="card-header"><div class="card-dot rose"></div><h3>Still open</h3></div>
        <ul>
          <li>• No nowcast model · no EVAL.md · no Bari send</li>
          <li>• F7 (Assente-only NDMI) not run</li>
          <li>• emergenza polygons: SSO human gate</li>
          <li>• Three briefs landed · relaunch deleg_fc8d40c3 may overwrite resistance (snapshot saved)</li>
          <li>• Montilon / Sabella / Suppl. S4 IDs not frozen</li>
        </ul>
      </div>
    </div>
    <p class="footer">CORDON · ~/Desktop/Connor/olive-xylella · generated from repo state 2026-08-15 · no invented nodes</p>
  </div>
</body>
</html>
"""

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(html)
print("wrote", OUT, "bytes", OUT.stat().st_size)
