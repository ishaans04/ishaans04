"""Render the clickable keycap buttons: section nav, demo links and contact links.

Each button is its own small SVG because a README link can only wrap a whole image
(GitHub strips image maps). Static, no font download, about 1 KB each.
"""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'buttons'
RED, INK = '#ff3b14', '#120200'
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
PAL = {'night': (INK, RED), 'day': (RED, INK)}
DEPTH = 7

# name: (index, label, glyph, width)
BUTTONS = {
    'about': ('02', 'ABOUT', '↓', 240),
    'stack': ('03', 'STACK', '↓', 240),
    'work': ('04', 'WORK', '↓', 240),
    'activity': ('05', 'ACTIVITY', '↓', 240),
    'play': ('06', 'PLAY', '↓', 240),
    'contact': ('07', 'CONTACT', '↓', 240),
    'square-one': ('▶', 'PLAY SQUARE ONE', '↗', 480),
    'haven': ('▶', 'HAVEN DEMO', '↗', 480),
    'email': ('@', 'EMAIL', '↗', 480),
    'linkedin': ('in', 'LINKEDIN', '↗', 480),
}


def button(theme, index, label, glyph, w, h=72):
    bg, fg = PAL[theme]
    face_w, face_h = w - DEPTH, h - DEPTH
    size = 30 if w <= 240 and len(label) > 6 else 32
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
            f'aria-label="{escape(label.title())}"><title>{escape(label.title())}</title>'
            f'<rect x="{DEPTH}" y="{DEPTH}" width="{face_w}" height="{face_h}" fill="{fg}"/>'
            f'<polygon points="{face_w},1.5 {w},{DEPTH} {w},{h} {DEPTH},{h} 1.5,{face_h}" fill="{fg}"/>'
            f'<rect x="1.5" y="1.5" width="{face_w - 1.5}" height="{face_h - 1.5}" fill="{bg}" stroke="{fg}" stroke-width="3"/>'
            f'<g font-family="{MONO}" font-weight="700" fill="{fg}">'
            f'<text x="12" y="22" font-size="13" letter-spacing="1">{escape(index)}</text>'
            f'<text x="{face_w - 12}" y="24" font-size="17" text-anchor="end">{glyph}</text>'
            f'<text x="{face_w / 2:.1f}" y="{face_h / 2 + size * .36 + 4:.1f}" font-size="{size if w > 240 else min(size, 26)}" '
            f'text-anchor="middle" letter-spacing="1">{escape(label)}</text></g></svg>')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (index, label, glyph, w) in BUTTONS.items():
        for theme in PAL:
            (OUT / f'{name}-{theme}.svg').write_text(button(theme, index, label, glyph, w), encoding='utf-8')
    print('built', len(BUTTONS) * 2, 'buttons')


if __name__ == '__main__':
    main()
