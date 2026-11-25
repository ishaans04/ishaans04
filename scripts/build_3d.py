"""Add the 3D layer to the static profile panels. Standard library only.

  * hero      extruded tagline (TAGLINE), sized down only if a line would overrun
  * fort      Square One's 20 rooms as an isometric fort (rooms still unlock in order)
  * orb       a rotating dot-matrix sphere in the Play panel

Every patch sits between <!--3D:name--> markers, so the script is safe to rerun.

Why it stays smooth: everything is precomputed geometry animated with CSS
transform and opacity only. No filters, blur, masks or JavaScript. The sphere
spins whole rings rather than single dots, build-in animations play once and
stop, and prefers-reduced-motion (already in every panel) freezes it all.
"""
import json
import math
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
RED, INK = '#ff3b14', '#120200'
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
DISP = "IS,'Arial Black',Impact,sans-serif"
ADV = json.loads((ASSETS / 'fonts/display-metrics.json').read_text(encoding='utf-8'))['advance']
SINE = 'cubic-bezier(.37,0,.63,1)'  # easeInOutSine: alternate runs trace a true sine wave
THEMES = ('night', 'day')


def mix(a, b, t):
    """Blend hex colour a toward b by t (0 = a, 1 = b)."""
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return '#' + ''.join(f'{round(x + (y - x) * t):02x}' for x, y in zip(ca, cb))


def colours(svg):
    """Panel background is the first full-size rect; the foreground is the other brand colour."""
    bg = re.search(r'<rect width="\d+" height="\d+" fill="(#[0-9a-f]{6})"', svg).group(1)
    return bg, (INK if bg == RED else RED)


def measure(s, size):
    return sum(ADV.get(c, 60.0) for c in s) * size / 100


def pts(points):
    return ' '.join(f'{x:.1f},{y:.1f}' for x, y in points)


def put(svg, name, body, fallback):
    """Replace the marked block, or on first run the region matched by `fallback`."""
    block = f'<!--3D:{name}-->{body}<!--/3D:{name}-->'
    marked = re.compile(rf'<!--3D:{name}-->.*?<!--/3D:{name}-->', re.S)
    if marked.search(svg):
        return marked.sub(lambda _: block, svg)
    new, n = re.subn(fallback, lambda _: block, svg, count=1, flags=re.S)
    if not n:
        raise ValueError(f'cannot place {name}: anchor not found')
    return new


def add_css(svg, css):
    if css in svg:
        return svg
    return svg.replace('@media (prefers-reduced-motion', css + '@media (prefers-reduced-motion', 1)


# ---------------------------------------------------------------- hero tagline

TAGLINE = ('I BUILD AI, THEN BEND IT', 'TILL IT SHOWS ITS WORK.')
TAGLINE_WIDTH = 1130  # widest the face may run from x=36 and still hold the right margin
HERO_TITLE = ('Ishaan Sharma, multi-agent orchestrator. The name denoises out of a field of binary digits. '
              'I build AI, then bend it till it shows its work. Open to internships, remote or on-site in India.')


def hero(svg):
    bg, fg = colours(svg)
    depth = 7
    size = min(85, int(TAGLINE_WIDTH * 85 / max(measure(line, 85) for line in TAGLINE)))
    out = []
    for i, line in enumerate(TAGLINE):
        top, base, delay = 682 + i * 83, 750 + i * 83, 2.7 + i * .12
        out.append(f'<clipPath id="tg{i}"><rect x="0" y="{top}" width="1200" height="{73 + depth + 2}"/></clipPath>'
                   f'<g clip-path="url(#tg{i})" font-family="{DISP}" font-size="{size}" font-weight="900">')
        # Extrusion: stacked copies stepping back from the face, darkest at the back.
        for k in range(depth, 0, -1):
            shade = mix(fg, bg, .42 + .05 * k)
            out.append(f'<text x="{36 + k * .9:.1f}" y="{base + k:.0f}" fill="{shade}" class="rv" '
                       f'style="animation-delay:{delay:.2f}s">{escape(line)}</text>')
        out.append(f'<text x="36" y="{base}" fill="{fg}" class="rv" style="animation-delay:{delay:.2f}s">{escape(line)}</text></g>')
    svg = put(svg, 'tagline', ''.join(out), r'<clipPath id="tg0">.*(?=</svg>)')
    svg = re.sub(r'aria-label="[^"]*"', f'aria-label="{escape(HERO_TITLE)}"', svg, count=1)
    return re.sub(r'<title>[^<]*</title>', f'<title>{escape(HERO_TITLE, quote=False)}</title>', svg, count=1)


# ---------------------------------------------------------------- Square One fort

def fort(svg):
    bg, fg = colours(svg)
    rooms = re.findall(r'<rect x="(\d+)" y="([\d.]+)" width="48" height="48"[^>]*animation:(rm\d+)', svg)
    if rooms:  # first run: read the unlock order from the flat grid
        order = {(round((float(y) - 285.9) / 60), (int(x) - 861) // 60): rm for x, y, rm in rooms}
    else:
        order = json.loads(re.search(r'<!--rooms:(.*?)-->', svg).group(1))
        order = {tuple(map(int, k.split(','))): v for k, v in order.items()}
    cols, rows = 5, 4
    e = 35
    a, b = e * math.cos(math.pi / 6), e * .5
    gap = .14  # inset per room so every room reads as its own block
    cx, cy = 1004, 410
    ox = cx - a / 2
    oy = cy - (9 * b + 40) / 2 + 26
    towers = {(0, 0), (0, cols - 1), (rows - 1, 0), (rows - 1, cols - 1)}
    lit = (fg, mix(fg, bg, .3), mix(fg, bg, .52))
    dark = (bg, mix(bg, fg, .16), mix(bg, fg, .32))
    stroke = f'stroke="{fg}" stroke-width="1.5" stroke-linejoin="round"'
    out = [f'<!--rooms:{json.dumps({f"{r},{c}": v for (r, c), v in order.items()})}-->']
    cells = sorted(((r, c) for r in range(rows) for c in range(cols)), key=lambda rc: (rc[0] + rc[1], rc[1]))
    for n, (r, c) in enumerate(cells):
        inner = 0 < r < rows - 1 and 0 < c < cols - 1
        h = 62 if (r, c) in towers else 16 if inner else 34
        x, y = ox + (c - r) * a, oy + (c + r) * b
        k = 1 - 2 * gap
        T = (x, y + 2 * b * gap)
        R, B, L = (T[0] + a * k, T[1] + b * k), (T[0], T[1] + 2 * b * k), (T[0] - a * k, T[1] + b * k)
        up = lambda p: (p[0], p[1] - h)
        faces = ([up(T), up(R), up(B), up(L)], [up(L), up(B), B, L], [up(B), up(R), R, B])

        def draw(fill):
            return ''.join(f'<polygon points="{pts(f)}" fill="{col}" {stroke}/>' for f, col in zip(faces, fill))

        crown = ''
        if (r, c) in towers:  # a flag on each corner tower
            mx, my = up(T)[0], up(T)[1] + b * k
            crown = (f'<path d="M{mx:.1f} {my:.1f}V{my - 26:.1f}" stroke="{fg}" stroke-width="2"/>'
                     f'<polygon points="{pts([(mx, my - 26), (mx + 15, my - 21), (mx, my - 16)])}" fill="{fg}"/>')
        rm = order.get((r, c))
        glow = (f'<g style="fill-opacity:0;animation:{rm} 10s steps(1,end) infinite">{draw(lit)}</g>' if rm else '')
        out.append(f'<g class="dr" style="animation-delay:{1.25 + n * .045:.2f}s">{draw(dark)}{glow}{crown}</g>')
    svg = add_css(svg, '@keyframes dr{from{opacity:0;transform:translateY(-40px)}}'
                       '.dr{animation:dr .7s cubic-bezier(.16,1,.3,1) both}')
    return put(svg, 'fort', ''.join(out), r'<rect x="861" y="285\.9".*(?=</svg>)')


# ---------------------------------------------------------------- rotating model orb

def orb_layer(fg, bg, cx, cy, R=106, period=26, tilt=.45):
    """A dot-matrix sphere turning about a tilted axis, with an orbiting satellite.

    Each latitude ring is ONE dotted circle (round caps on zero-length dashes), spun by
    a CSS rotation and squashed by sin(tilt) into its ellipse. non-scaling-stroke keeps
    the dots round. The sphere is 22 animated elements in total; animating each dot
    separately cost about 4x more main-thread time. A static clip shows the front half
    of every ring at full strength and leaves the back half dim, which reads as depth.
    """
    squash = math.sin(tilt)
    dim, front = [], []
    for v in range(-75, 76, 15):
        lat = math.radians(v)
        r = R * math.cos(lat)
        y0 = -R * math.sin(lat) * math.cos(tilt)
        n = max(5, round(24 * math.cos(lat)))
        gap = 2 * math.pi * r * squash / n  # ~even dot spacing along the projected ring
        ring = (f'<g transform="scale(1 {squash:.3f})"><circle r="{r:.1f}" class="rt" '
                f'stroke-dasharray="0 {gap:.2f}" style="animation-delay:{v * .05:.2f}s"/></g>')
        dim.append(f'<g transform="translate({cx} {cy + y0:.1f})">{ring}</g>')
        front.append(f'<g transform="translate({cx} {cy + y0:.1f})" clip-path="url(#orbfront)">{ring}</g>')
    ring_r, sat = R * 1.42, 8.0
    ry = ring_r * squash
    # Round caps on zero-length dashes draw dots; non-scaling-stroke keeps them round after the squash.
    dots = (f'fill="none" stroke="{fg}" stroke-width="5.5" stroke-linecap="round" '
            'vector-effect="non-scaling-stroke"')
    css = (f'@keyframes rt{{to{{transform:rotate(360deg)}}}}.rt{{animation:rt {period}s linear infinite}}'
           f'@keyframes sx{{from{{transform:translateX({-ring_r:.1f}px)}}to{{transform:translateX({ring_r:.1f}px)}}}}'
           f'@keyframes sz{{from{{transform:translateY({-ry:.1f}px)}}to{{transform:translateY({ry:.1f}px)}}}}'
           f'.sx{{animation:sx {sat / 2}s {SINE} infinite alternate;animation-delay:{-sat / 4}s}}'
           f'.sz{{animation:sz {sat / 2}s {SINE} infinite alternate}}')
    body = (f'<clipPath id="orbfront"><rect x="-{R * 2}" y="0" width="{R * 4}" height="{R * 2}"/></clipPath>'
            f'<g class="fi" style="animation-delay:.9s">'
            f'<circle cx="{cx}" cy="{cy}" r="{R + 6}" fill="none" stroke="{fg}" stroke-opacity=".28" stroke-width="1.2"/>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{ring_r:.1f}" ry="{ry:.1f}" fill="none" stroke="{fg}" '
            f'stroke-opacity=".4" stroke-width="1.2" stroke-dasharray="2 5"/>'
            f'<g {dots} stroke-opacity=".22">{"".join(dim)}</g><g {dots}>{"".join(front)}</g>'
            f'<g class="sx"><rect x="{cx - 5}" y="{cy - 5}" width="10" height="10" fill="{fg}" class="sz"/></g>'
            f'<text x="{cx}" y="{cy + R + 50:.0f}" font-family="{MONO}" font-size="11" font-weight="700" fill="{fg}" '
            f'text-anchor="middle" letter-spacing="2">FIG. 01 · THE MODEL, LIVE</text></g>')
    return css, body


PLAY_EXTRA = 70


def play(svg):
    bg, fg = colours(svg)
    if '<!--3D:orb-->' not in svg:  # first run: make room under the description
        h = int(re.search(r'height="(\d+)"', svg).group(1))
        svg = svg.replace(f'height="{h}" viewBox="0 0 1200 {h}"', f'height="{h + PLAY_EXTRA}" viewBox="0 0 1200 {h + PLAY_EXTRA}"', 1)
        svg = svg.replace(f'<rect width="1200" height="{h}"', f'<rect width="1200" height="{h + PLAY_EXTRA}"', 1)
        svg = re.sub(r'(<text x="40" y=")(\d+(?:\.\d+)?)("[^>]*>2 → 16)', lambda m: f'{m.group(1)}{float(m.group(2)) + PLAY_EXTRA:g}{m.group(3)}', svg)
    css, body = orb_layer(fg, bg, 990, 306)
    svg = re.sub(r'<style id="orb">.*?</style>', '', svg, flags=re.S)
    svg = svg.replace('</style>', f'</style><style id="orb">{css}</style>', 1)
    return put(svg, 'orb', body, r'(?=</svg>)')


def main():
    jobs = {'hero': hero, 'work-square-one': fort, 'play': play}
    for stem, fn in jobs.items():
        for theme in THEMES:
            path = ASSETS / f'{stem}-{theme}.svg'
            path.write_text(fn(path.read_text(encoding='utf-8')), encoding='utf-8')
            print('built', path.name)


if __name__ == '__main__':
    main()
