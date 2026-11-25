"""Render the activity panel (night + day) and the four byte-per-day dividers from assets/activity.json.

Standard library only. Mirrors the profile's red/black typographic system; animation is CSS inside the SVG.
"""
import json
from datetime import date, timedelta
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RED, INK = '#ff3b14', '#120200'
PAL = {'night': (INK, RED), 'day': (RED, INK)}
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
DISP = "IS,'Arial Black',Impact,sans-serif"
MON = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
FONT = (ROOT / 'assets/fonts/display.woff2.b64').read_text(encoding='utf-8').strip()
ADV = json.loads((ROOT / 'assets/fonts/display-metrics.json').read_text(encoding='utf-8'))['advance']
BASE = ('@keyframes fi{from{opacity:0}}.fi{animation:fi .7s ease both}'
        '@keyframes up{from{opacity:0;transform:translateY(24px)}}.up{animation:up .8s cubic-bezier(.16,1,.3,1) both}'
        '@keyframes off{from,to{opacity:0}}@keyframes bk{50%{opacity:0}}.bk{animation:bk 1s steps(1) infinite}')
W = 1200


def measure(s, size):
    return sum(ADV.get(c, 60.0) for c in s) * size / 100


def fit(s, max_w, max_size):
    return min(max_size, int(max_w / max(measure(s, 100), 1) * 100))


def delay(s):
    return f'animation-delay:{s:.2f}s'


def t(x, y, txt, size=14, fill=RED, weight=None, anchor=None, ls=None, op=None, cls=None, style=None, disp=False, sans=False):
    fam = DISP if disp else SANS if sans else MONO
    a = f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}"'
    if weight or disp:
        a += f' font-weight="{weight or 900}"'
    a += f' fill="{fill}"'
    if anchor:
        a += f' text-anchor="{anchor}"'
    if ls is not None:
        a += f' letter-spacing="{ls}"'
    if op is not None:
        a += f' fill-opacity="{op}"'
    if style:
        a += f' style="{style}"'
    if cls:
        a += f' class="{cls}"'
    return a + f'>{escape(str(txt), quote=False)}</text>'


def svg(w, h, title, css, body, font=True):
    face = f"@font-face{{font-family:IS;src:url(data:font/woff2;base64,{FONT}) format('woff2');font-weight:900}}" if font else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">'
            f'<title>{escape(title, quote=False)}</title><style>{face}{BASE}{css}'
            '@media (prefers-reduced-motion:reduce){*{animation:none!important}}</style>' + body + '</svg>')


def label(x, y, n, name, fill, anchor=None):
    return t(x, y, f'({n}) {name}', 13, fill, 700, anchor, 2.5)


def rule(y, fill, x=40, w=1120):
    return f'<rect x="{x}" y="{y}" width="{w}" height="2" fill="{fill}"/>'


def mon(iso):
    return f'{iso[8:10]} {MON[int(iso[5:7]) - 1]}'


def model(data):
    own = data['login'].lower()
    items = data['projects']['items']

    def mine(p):
        return p['full_name'].lower().startswith(own + '/')

    def last(p):
        return max(p['daily']) if p['daily'] else ''

    own_names = {p['name'].lower() for p in items if mine(p)}
    projects = [p for p in items if mine(p) or p['name'].lower() not in own_names][:6]
    end = date.fromisoformat(data['projects']['to'])
    dates = [(end - timedelta(days=i)).isoformat() for i in range(29, -1, -1)]
    latest = sorted(projects, key=lambda p: (last(p), p['commits']), reverse=True)[0] if projects else None
    hours = data['commit_time_sample']['hours_ist']
    peak = max(range(24), key=lambda i: (sum(hours[(i + j) % 24] for j in range(3)), -i))
    active = sum(1 for d in data['calendar']['days'] if d['contributionCount'])
    return mine, projects, dates, last, latest, peak, active


def activity(theme, data):
    bg, fg = PAL[theme]
    mine, projects, dates, last, latest, peak, active = model(data)
    n = len(projects)
    yl, rh = 400, 34
    h = yl + max(n, 1) * rh + 110
    b = [f'<rect width="{W}" height="{h}" fill="{bg}"/>', label(40, 56, '05', 'ACTIVITY', fg),
         t(1160, 56, 'PUBLIC GITHUB DATA · UPDATED ' + data['updated_at'][:10], 13, fg, 700, 'end', 2.5), rule(76, fg),
         t(40, 118, 'NOW BUILDING', 13, fg, 700, ls=2.5)]
    name = ((latest['name'] if mine(latest) else latest['full_name']) if latest else 'quiet week').upper()
    nsz = fit(name, 600, 140)
    nw = measure(name, nsz)
    b.append(f'<g class="up" style="{delay(.2)}">' + t(36, f'{120 + nsz * .78:.1f}', name, nsz, fg, disp=True)
             + f'<rect x="{52 + nw:.0f}" y="{120 + nsz * .06:.0f}" width="{nsz * .14:.0f}" height="{nsz * .72:.0f}" fill="{fg}" class="bk"/></g>')
    if latest:
        b.append(t(40, 296, f"{latest['commits']} COMMITS IN 30 DAYS · LAST PUSH {mon(last(latest))}", 13, fg, 700, ls=1.5, cls='fi', style=delay(.5)))
    pk = f'{peak:02d}:00–{(peak + 3) % 24:02d}:00'
    for i, (v, lb) in enumerate([(f"{data['calendar']['total']:,}", 'CONTRIBUTIONS · 12 MONTHS'), (str(active), 'ACTIVE DAYS · 12 MONTHS'), (pk, 'PEAK HOURS · IST')]):
        y = 150 + i * 76
        b.append(f'<g class="up" style="{delay(.3 + i * .1)}">' + t(1160, y, v, 50, fg, anchor='end', disp=True) + t(1160, y + 22, lb, 12, fg, 700, 'end', 2) + '</g>')
    b += [rule(330, fg), t(40, 366, 'COMMITS PER PROJECT PER DAY · LAST 30 DAYS', 13, fg, 700, ls=2.5),
          t(1160, 366, f'{mon(dates[0])} — {mon(dates[29])}', 13, fg, 700, 'end', 2.5)]

    def cx(i):
        return round(316 + i * 28.8 + 12, 1)

    for k, p in enumerate(projects):
        y = yl + k * rh
        b.append(t(40, y + 22, (p['name'] if mine(p) else p['name'] + ' ·  COLLAB').upper(), 18, fg, disp=True))
        for i, d in enumerate(dates):
            v = p['daily'].get(d, 0)
            st = delay(.4 + i * .03)
            if not v:
                b.append(t(cx(i), y + 21, '·', 14, fg, anchor='middle', op=.4, cls='fi', style=st))
            elif v >= 30:
                b.append(f'<g class="fi" style="{st}"><rect x="{cx(i) - 13:.1f}" y="{y + 5}" width="26" height="23" fill="{fg}"/>' + t(cx(i), y + 21, v, 13, bg, 700, 'middle') + '</g>')
            else:
                b.append(t(cx(i), y + 21, v, 13, fg, 800 if v >= 10 else 400, 'middle', cls='fi', style=st))
    if not n:
        b.append(t(40, yl + 22, 'NO PUBLIC PROJECT COMMITS IN THIS WINDOW.', 18, fg, disp=True))
    ya = yl + max(n, 1) * rh + 14
    for i in (0, 7, 14, 21, 29):
        b.append(t(cx(i), ya, mon(dates[i]), 10, fg, 700, 'middle', 1))
    b += [rule(h - 66, fg), t(40, h - 32, 'THE BINARY BETWEEN SECTIONS IS REAL: MY LAST 44 DAYS OF CONTRIBUTIONS, ONE BYTE PER DAY.', 12, fg, 700, ls=1.2)]
    title = (f"Activity. Now building {name}. {data['calendar']['total']} contributions in the last 12 months, {active} active days, "
             f'peak hours {pk} IST. Commits per project per day for the last 30 days.')
    return svg(W, h, title, '', ''.join(b))


def dividers(data):
    days = data['calendar']['days'][-44:]
    out = []
    for q in range(4):
        ch = days[q * 11:q * 11 + 11]
        if not ch:
            continue
        bits = ''.join(format(min(255, d['contributionCount']), '08b') for d in ch)
        cw = 1010 / 88
        g = ''.join(f'<text x="{i * cw + cw / 2:.1f}" y="30" text-anchor="middle" fill-opacity="{1 if bit == "1" else .3}" '
                    f'style="animation:off {.05 + i * .016:.3f}s linear">{bit}</text>' for i, bit in enumerate(bits))
        lbl = f"{mon(ch[0]['date'])} — {mon(ch[-1]['date'])}"
        title = f"Contributions from {lbl}, one byte per day: {', '.join(str(d['contributionCount']) for d in ch)}."
        body = f'<g font-family="{MONO}" font-size="15" font-weight="700" fill="{RED}">{g}</g>' + t(1200, 30, lbl, 11, RED, 700, 'end', 1.5)
        out.append(svg(W, 44, title, '', body, font=False))
    return out


def render_all(data):
    files = {f'activity-{th}.svg': activity(th, data) for th in ('night', 'day')}
    for i, s in enumerate(dividers(data), 1):
        files[f'divider-{i}.svg'] = s
    return files


def readme_line(data):
    return (f'<p align="center"><sub>Refreshed daily from public GitHub data · last refresh {data["updated_at"][:10]} UTC · '
            f'<a href="assets/activity.json">raw data</a></sub></p>')


if __name__ == '__main__':
    payload = json.loads((ROOT / 'assets/activity.json').read_text(encoding='utf-8'))
    for name, content in render_all(payload).items():
        (ROOT / 'assets' / name).write_text(content, encoding='utf-8')
    print('Rendered', ', '.join(render_all(payload)))
