"""Generate assets/hero.svg for the hyperb1iss profile.

Pure SVG: CSS keyframes only (so prefers-reduced-motion gates every
animation), subset JetBrains Mono embedded as base64 woff2, no scripts,
no external resources. GitHub serves README SVGs as <img>, and this is
exactly the feature set that survives there.
"""

from base64 import b64encode
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "assets" / "hero.svg"

bold = b64encode((HERE / "assets/fonts/jetbrains-mono-bold.subset.woff2").read_bytes()).decode()
regular = b64encode((HERE / "assets/fonts/jetbrains-mono-regular.subset.woff2").read_bytes()).decode()

# SilkCircuit Neon
BG = "#0a0612"
MAGENTA = "#e135ff"
CYAN = "#80ffea"
CORAL = "#ff6ac1"
YELLOW = "#f1fa8c"
MUTED = "#9d7fd1"

W, H = 1200, 320

# Circuit traces on the right half. Orthogonal runs with 45-degree jogs,
# the classic PCB look. Each has a pulse that travels along it.
TRACES = [
    ("M 720 62 H 860 L 900 102 H 1040 L 1080 142 H 1200", CYAN, 0.0, 7.0),
    ("M 760 120 H 930 L 970 160 H 1130 L 1170 200 H 1200", MAGENTA, 1.8, 8.5),
    ("M 700 250 H 820 L 860 210 H 990 L 1030 250 H 1200", CORAL, 3.1, 6.5),
    ("M 1200 30 H 1110 L 1070 70 H 960 L 920 30 H 840", MAGENTA, 0.9, 9.0),
    ("M 1200 290 H 1090 L 1050 250 H 900", CYAN, 4.2, 7.5),
]

# Solder pads / vias at trace joints.
PADS = [
    (860, 62, CYAN), (1040, 102, CYAN), (930, 120, MAGENTA), (1130, 160, MAGENTA),
    (820, 250, CORAL), (990, 210, CORAL), (1110, 30, MAGENTA), (960, 70, MAGENTA),
    (840, 30, MAGENTA), (1090, 290, CYAN), (900, 250, CYAN), (720, 62, CYAN),
    (760, 120, MAGENTA), (700, 250, CORAL),
]

trace_svg = []
for i, (d, color, delay, dur) in enumerate(TRACES):
    trace_svg.append(
        f'<path d="{d}" class="trace" stroke="{color}"/>'
        f'<path d="{d}" class="pulse" stroke="{color}" '
        f'style="animation-delay:{delay}s;animation-duration:{dur}s"/>'
    )
pad_svg = []
for i, (x, y, color) in enumerate(PADS):
    pad_svg.append(
        f'<circle cx="{x}" cy="{y}" r="4" fill="{BG}" stroke="{color}" stroke-width="2" '
        f'class="pad" style="animation-delay:{(i * 0.37) % 3:.2f}s"/>'
    )

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="title desc">
<title id="title">hyperb1iss</title>
<desc id="desc">Stefanie Jane, principal engineer and open-source maker. RGB engines, agent memory, terminal UIs, SilkCircuit.</desc>
<defs>
<style>
@font-face{{font-family:"JBM";font-weight:700;src:url(data:font/woff2;base64,{bold}) format("woff2")}}
@font-face{{font-family:"JBM";font-weight:400;src:url(data:font/woff2;base64,{regular}) format("woff2")}}
.mono{{font-family:"JBM","JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}
.wm{{font-weight:700;font-size:96px;letter-spacing:-3px}}
.tag{{font-weight:400;font-size:19px;letter-spacing:5px;fill:{CYAN}}}
.sub{{font-weight:400;font-size:15px;letter-spacing:2.5px;fill:{MUTED}}}
.prompt{{font-weight:400;font-size:19px;fill:{MAGENTA}}}
.trace{{fill:none;stroke-width:1.5;opacity:.22;stroke-linecap:round;stroke-linejoin:round}}
.pulse{{fill:none;stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:56 900;stroke-dashoffset:956;opacity:0}}
.pad{{opacity:.45}}
.cursor{{fill:{CYAN}}}
.blob{{mix-blend-mode:screen}}
@media (prefers-reduced-motion:no-preference){{
  .sweep{{animation:sweep 9s linear infinite}}
  .pulse{{animation-name:pulse;animation-timing-function:linear;animation-iteration-count:infinite;opacity:.9}}
  .pad{{animation:pad 3s ease-in-out infinite}}
  .cursor{{animation:blink 1.1s steps(2,start) infinite}}
  .blob-a{{animation:drift-a 18s ease-in-out infinite alternate}}
  .blob-b{{animation:drift-b 23s ease-in-out infinite alternate}}
  .glow{{animation:breathe 4s ease-in-out infinite}}
}}
@keyframes sweep{{to{{transform:translateX({W}px)}}}}
@keyframes pulse{{from{{stroke-dashoffset:956}}to{{stroke-dashoffset:0}}}}
@keyframes pad{{0%,100%{{opacity:.35}}50%{{opacity:1}}}}
@keyframes blink{{to{{opacity:0}}}}
@keyframes breathe{{0%,100%{{opacity:.7}}50%{{opacity:1}}}}
@keyframes drift-a{{to{{transform:translate(120px,40px)}}}}
@keyframes drift-b{{to{{transform:translate(-90px,-50px)}}}}
</style>
<linearGradient id="neon" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="0" spreadMethod="repeat">
  <stop offset="0" stop-color="{MAGENTA}"/>
  <stop offset=".3" stop-color="{CORAL}"/>
  <stop offset=".55" stop-color="{CYAN}"/>
  <stop offset=".8" stop-color="{YELLOW}"/>
  <stop offset="1" stop-color="{MAGENTA}"/>
</linearGradient>
<radialGradient id="blobA"><stop offset="0" stop-color="{MAGENTA}" stop-opacity=".32"/><stop offset="1" stop-color="{MAGENTA}" stop-opacity="0"/></radialGradient>
<radialGradient id="blobB"><stop offset="0" stop-color="{CYAN}" stop-opacity=".4"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
<linearGradient id="edge" x1="0" x2="1"><stop offset="0" stop-color="{MAGENTA}"/><stop offset=".5" stop-color="{CORAL}"/><stop offset="1" stop-color="{CYAN}"/></linearGradient>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#fff" opacity=".035"/></pattern>
<filter id="glowf" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="14"/></filter>
<filter id="softf" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>
<clipPath id="wm"><text class="mono wm" x="76" y="176">hyperb1iss</text></clipPath>
</defs>

<rect width="{W}" height="{H}" fill="{BG}"/>
<g class="blob"><circle class="blob-a" cx="120" cy="20" r="340" fill="url(#blobA)"/><circle class="blob-b" cx="1000" cy="300" r="300" fill="url(#blobB)"/></g>
<rect width="{W}" height="{H}" fill="url(#scan)"/>

<g>{"".join(trace_svg)}</g>
<g>{"".join(pad_svg)}</g>

<g class="glow" filter="url(#glowf)"><g clip-path="url(#wm)"><rect class="sweep" x="-{W}" y="0" width="{W * 3}" height="{H}" fill="url(#neon)"/></g></g>
<g filter="url(#softf)" opacity=".8"><g clip-path="url(#wm)"><rect class="sweep" x="-{W}" y="0" width="{W * 3}" height="{H}" fill="url(#neon)"/></g></g>
<g clip-path="url(#wm)"><rect class="sweep" x="-{W}" y="0" width="{W * 3}" height="{H}" fill="url(#neon)"/></g>
<rect class="cursor" x="662" y="102" width="30" height="76" rx="2"/>

<text class="mono prompt" x="78" y="226">$</text>
<text class="mono tag" x="104" y="226">principal engineer · open-source maker</text>
<text class="mono sub" x="80" y="266">rgb engines · agent memory · terminal uis · silkcircuit</text>

<rect x="0" y="{H - 3}" width="{W}" height="3" fill="url(#edge)"/>
</svg>
'''

OUT.write_text(svg)
print(f"wrote {OUT} ({OUT.stat().st_size / 1024:.1f} KB)")
