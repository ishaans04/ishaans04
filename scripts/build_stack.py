"""Build the Stack hive: every technology as a hexagonal shield, grouped like the marquee.

The marquee panel stays the closed state. The README wraps it in <details><summary>, so a
click on the panel opens the hive under it and a second click closes it again. This script
also keeps the "tap to expand" hint in the marquee's header and the README block between
the STACK markers in step with the list below.

Logos are Simple Icons path data (CC0) saved in scripts/stack_icons.json. Technologies with
no brand mark get a small line glyph drawn here.

    python scripts/build_stack.py
"""
import json
import math
import re
from html import escape

from render_activity import BASE, FONT, PAL, ROOT, W, label, rule, t

STACK = [  # category, [(label, icon)]; icon is a stack_icons.json key or 'glyph:<name>'
    ('LANGUAGES', [('Python', 'python'), ('TypeScript', 'typescript'), ('JavaScript', 'javascript'), ('Go', 'go'),
                   ('SQL', 'glyph:sql'), ('Java', 'glyph:cup'), ('C++', 'cplusplus')]),
    ('AI', [('Agentic AI', 'glyph:spark'), ('Multi-agent', 'glyph:agents'), ('RAG', 'glyph:rag'),
            ('LangGraph', 'langgraph'), ('LangChain', 'langchain'), ('MCP', 'modelcontextprotocol'),
            ('Pydantic AI', 'pydantic'), ('Claude Code', 'claude'), ('Codex', 'glyph:terminal')]),
    ('DELIVERY', [('FastAPI', 'fastapi'), ('React', 'react'), ('Node.js', 'nodedotjs'), ('PostgreSQL', 'postgresql'),
                  ('pgvector', 'glyph:vector'), ('MongoDB', 'mongodb'), ('SQLite', 'sqlite'), ('Neon', 'neon'),
                  ('Docker', 'docker'), ('GitHub Actions', 'githubactions'), ('Vercel', 'vercel')]),
]

ICONS = json.loads((ROOT / 'scripts/stack_icons.json').read_text(encoding='utf-8'))['icons']

# Line glyphs on the same 24x24 grid as Simple Icons, for technologies without a brand mark.
GLYPHS = {
    'sql': 'M4 5v14M20 5v14M4 12a8 3 0 0 0 16 0M4 19a8 3 0 0 0 16 0M4 5a8 3 0 1 0 16 0a8 3 0 1 0-16 0',
    'spark': None,  # filled, see below
    'agents': 'M12 6.5L5.5 17.5M12 6.5l6.5 11M5.5 17.5h13',
    'rag': 'M4 2.5h9l3 3V11M4 2.5v17h7M7 7.5h6M7 11h4M17.5 18.5a3.5 3.5 0 1 0 0-.01M20 21l2 2',
    'vector': 'M3 3v18h18M3 21L17 7M11 7h6v6',
    'cup': 'M4 10h12v4.5a5.5 5.5 0 0 1-5.5 5.5h-1A5.5 5.5 0 0 1 4 14.5zM16 11.5h1.5a2.8 2.8 0 0 1 0 5.6H15.6M3 22.5h14M8 2.5c-1.2 1.6 1.2 2.6 0 4.5M12 2.5c-1.2 1.6 1.2 2.6 0 4.5',
    'terminal': 'M3 4.5h18v15H3zM7 9.5l3 2.5-3 2.5M12.5 15h5',
}
SPARK = 'M12 1.5C12.9 8.6 15.4 11.1 22.5 12C15.4 12.9 12.9 15.4 12 22.5C11.1 15.4 8.6 12.9 1.5 12C8.6 11.1 11.1 8.6 12 1.5Z'
NODES = ((12, 5), (4.5, 19), (19.5, 19))

R = 64                       # hexagon radius, centre to vertex
HW = math.sqrt(3) * R        # pointy-top hexagon width
X0 = 290                     # left edge of the hive area; category labels sit left of it
TOP, BAND, GAP = 110, 2 * R + 1.5 * R, 34
CSS = ('@keyframes pop{from{opacity:0;transform:scale(.55)}}'
       '.pop{animation:pop .6s cubic-bezier(.16,1,.3,1) both;transform-box:fill-box;transform-origin:center}')


def mix(a, b, k):
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return '#' + ''.join(f'{round(x + (y - x) * k):02x}' for x, y in zip(ca, cb))


def techs():
    names = [name.lower() for _, items in STACK for name, _ in items]
    dupes = sorted({n for n in names if names.count(n) > 1})
    if dupes:
        raise ValueError(f'listed twice: {dupes}')
    return names


def hexagon(cx, cy, r):
    return ' '.join(f'{cx + r * math.cos(math.radians(a)):.1f},{cy + r * math.sin(math.radians(a)):.1f}'
                    for a in range(-90, 270, 60))


def icon(key, x, y, size, fg):
    """Draw a 24x24 icon with its top-left corner at (x, y), scaled to `size`."""
    k = size / 24
    g = f'<g transform="translate({x:.1f} {y:.1f}) scale({k:.3f})">'
    if not key.startswith('glyph:'):
        return g + f'<path d="{ICONS[key]}" fill="{fg}"/></g>'
    name = key[6:]
    if name == 'spark':
        return g + f'<path d="{SPARK}" fill="{fg}"/></g>'
    body = f'<path d="{GLYPHS[name]}" fill="none" stroke="{fg}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
    if name == 'agents':
        body += ''.join(f'<circle cx="{a}" cy="{b}" r="3.2" fill="{fg}"/>' for a, b in NODES)
    return g + body + '</g>'


def words(name):
    """Hex labels hold about 11 monospace capitals per line."""
    s = name.upper()
    if len(s) <= 11 or ' ' not in s:
        return [s]
    head, tail = s.rsplit(' ', 1)
    return [head, tail]


def hive(theme):
    bg, fg = PAL[theme]
    tint = mix(bg, fg, .07)
    total = len(techs())
    b = [label(40, 56, '03', 'STACK · THE FULL HIVE', fg),
         t(1160, 56, f'{total} TECHNOLOGIES · TAP THE PANEL ABOVE TO CLOSE ↑', 13, fg, 700, 'end', 2.5), rule(76, fg)]
    n = 0
    for k, (cat, items) in enumerate(STACK):
        top = TOP + k * (BAND + GAP)
        if k:
            b.append(rule(top - GAP / 2 - 1, fg))
        b += [t(40, top + 64, cat, 30, fg, disp=True),
              t(40, top + 90, f'{len(items):02d} {"TECHNOLOGY" if len(items) == 1 else "TECHNOLOGIES"}', 12, fg, 700, ls=2)]
        first = math.ceil(len(items) / 2)
        for i, (name, key) in enumerate(items):
            row, col = (0, i) if i < first else (1, i - first)
            cx = X0 + HW / 2 + col * HW + row * HW / 2
            cy = top + R + row * 1.5 * R
            lines = words(name)
            ly = cy + (26 if len(lines) == 1 else 19)
            cell = (f'<polygon points="{hexagon(cx, cy, R - 5)}" fill="{tint}" stroke="{fg}" stroke-width="2" stroke-linejoin="round"/>'
                    + icon(key, cx - 16, cy - (36 if len(lines) == 1 else 40), 32, fg)
                    + ''.join(t(f'{cx:.1f}', f'{ly + j * 14:.0f}', line, 11, fg, 700, 'middle', 1) for j, line in enumerate(lines)))
            b.append(f'<g class="pop" style="animation-delay:{.2 + n * .035:.2f}s">{cell}</g>')
            n += 1
    h = round(TOP + len(STACK) * BAND + (len(STACK) - 1) * GAP + 40)
    title = 'Full stack. ' + ' '.join(f'{cat.capitalize() if cat != "AI" else cat}: {", ".join(x for x, _ in items)}.'
                                      for cat, items in STACK)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" '
            f'aria-label="{escape(title)}"><title>{escape(title, quote=False)}</title>'
            f"<style>@font-face{{font-family:IS;src:url(data:font/woff2;base64,{FONT}) format('woff2');font-weight:900}}"
            f'{BASE}{CSS}@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>'
            f'<rect width="{W}" height="{h}" fill="{bg}"/>{"".join(b)}</svg>'), title


HINT = 'LANGUAGES / AI / DELIVERY · TAP TO EXPAND ↓'


def readme_block(title):
    return '\n'.join([
        '<!-- STACK:START -->', '<a id="stack"></a>', '<details>',
        '<summary><picture><source media="(prefers-color-scheme: dark)" srcset="assets/stack-night.svg">'
        '<img src="assets/stack-day.svg" width="100%" align="top" alt="Stack: Python, TypeScript, JavaScript, Go, SQL, Java, C++; '
        'agentic AI, multi-agent systems, RAG, LangGraph, LangChain, MCP, Pydantic AI; FastAPI, React, Node.js, PostgreSQL, '
        'pgvector, MongoDB, Docker, GitHub Actions, Vercel. Tap to open the full hive."></picture></summary>',
        '<picture><source media="(prefers-color-scheme: dark)" srcset="assets/stack-hive-night.svg">'
        f'<img src="assets/stack-hive-day.svg" width="100%" align="top" alt="{escape(title)}"></picture>',
        '</details>', '<!-- STACK:END -->'])


def main():
    techs()
    for theme in ('night', 'day'):
        svg, title = hive(theme)
        (ROOT / f'assets/stack-hive-{theme}.svg').write_bytes(svg.encode('utf-8'))
        panel = ROOT / f'assets/stack-{theme}.svg'
        s, n = re.subn(r'(text-anchor="end" letter-spacing="2.5">)LANGUAGES / AI / DELIVERY[^<]*(</text>)',
                       lambda m: m.group(1) + HINT + m.group(2), panel.read_text(encoding='utf-8'))
        if n != 1:
            raise ValueError(f'cannot find the header hint in {panel.name}')
        panel.write_bytes(s.encode('utf-8'))
    readme_path = ROOT / 'README.md'
    readme = readme_path.read_text(encoding='utf-8')
    readme, n = re.subn(r'<!-- STACK:START -->.*?<!-- STACK:END -->', lambda _: readme_block(title), readme, flags=re.S)
    if n != 1:
        raise ValueError('Expected exactly one STACK block in README')
    readme_path.write_bytes(readme.encode('utf-8'))
    print(f'Built the stack hive: {len(techs())} technologies')


if __name__ == '__main__':
    main()
