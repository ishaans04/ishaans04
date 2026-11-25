"""Teach the Model: a tiny neural network trained by profile visitors.

A visitor clicks a tile in the README, which opens an issue titled `teach|ROW|COL`.
The workflow runs this script: it adds a labelled point at that tile (labels alternate 1, 0, 1, ...),
retrains a 2 -> 16 -> 1 tanh MLP from a fixed seed with Adam, and redraws the board between the
TEACH markers. Standard library only; the browser preview uses the same algorithm and seed.
"""
import json
import math
import os
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / 'assets/teach/state.json'
README = ROOT / 'README.md'
REPO = os.environ.get('GITHUB_REPOSITORY', 'ishaans04/ishaans04')
H, EPOCHS, LR, COLS, ROWS = 16, 600, 0.05, 12, 6
LETTERS = 'ABCDEFGHIJKL'
SEED = [{'r': 1, 'c': 2, 'label': 1, 'by': 'ishaans04'}, {'r': 4, 'c': 9, 'label': 1, 'by': 'ishaans04'},
        {'r': 1, 'c': 9, 'label': 0, 'by': 'ishaans04'}, {'r': 4, 'c': 2, 'label': 0, 'by': 'ishaans04'}]


def rng(seed):
    s = seed & 0xFFFFFFFF

    def nxt():
        nonlocal s
        s = (1664525 * s + 1013904223) & 0xFFFFFFFF
        return s / 4294967296
    return nxt


def xy(r, c):
    return (c - 5.5) / 5.5 * 1.6, (r - 2.5) / 5.5 * 1.6


def js_round(x):
    return math.floor(x + 0.5)


def train(points):
    r = rng(20261125)
    w1, b1, w2 = [], [], []
    b2 = 0.0
    for _ in range(H):
        w1.append([(r() * 2 - 1) * 2, (r() * 2 - 1) * 2])
        b1.append(r() * 2 - 1)
        w2.append((r() * 2 - 1) * 0.5)
    size = 4 * H + 1
    m, v = [0.0] * size, [0.0] * size
    xs = [xy(p['r'], p['c']) for p in points]
    ts = [p['label'] for p in points]
    n = len(points) or 1
    loss = 0.0
    for ep in range(1, EPOCHS + 1):
        g = [0.0] * size
        loss = 0.0
        for (x, y), target in zip(xs, ts):
            h = [math.tanh(w1[j][0] * x + w1[j][1] * y + b1[j]) for j in range(H)]
            z = b2
            for j in range(H):
                z += w2[j] * h[j]
            p = 1 / (1 + math.exp(-z))
            loss += -(target * math.log(p + 1e-9) + (1 - target) * math.log(1 - p + 1e-9))
            dz = (p - target) / n
            for j in range(H):
                dh = dz * w2[j] * (1 - h[j] * h[j])
                g[3 * j] += dh * x
                g[3 * j + 1] += dh * y
                g[3 * j + 2] += dh
                g[3 * H + j] += dz * h[j]
            g[4 * H] += dz
        c1, c2 = 1 - 0.9 ** ep, 1 - 0.999 ** ep

        def step(i, w):
            m[i] = 0.9 * m[i] + 0.1 * g[i]
            v[i] = 0.999 * v[i] + 0.001 * g[i] * g[i]
            return w - LR * (m[i] / c1) / (math.sqrt(v[i] / c2) + 1e-8)
        for j in range(H):
            w1[j][0] = step(3 * j, w1[j][0])
            w1[j][1] = step(3 * j + 1, w1[j][1])
            b1[j] = step(3 * j + 2, b1[j])
            w2[j] = step(3 * H + j, w2[j])
        b2 = step(4 * H, b2)
    preds = []
    for rr in range(ROWS):
        for cc in range(COLS):
            x, y = xy(rr, cc)
            z = b2
            for j in range(H):
                z += w2[j] * math.tanh(w1[j][0] * x + w1[j][1] * y + b1[j])
            preds.append(js_round(1e3 / (1 + math.exp(-z))) / 1e3)
    return preds, js_round(loss / n * 1e4) / 1e4


def tile(state, idx):
    p = state['preds'][idx]
    cls = 1 if p >= 0.5 else 0
    conf = abs(p - 0.5) * 2
    r, c = divmod(idx, COLS)
    pt = next((q for q in state['points'] if q['r'] == r and q['c'] == c), None)
    if pt:
        last = state.get('last') or {}
        prefix = 'n' if last.get('r') == r and last.get('c') == c else 'l'
        return f"{prefix}{pt['label']}{'' if pt['label'] == cls else 'x'}"
    prev = state.get('prev') or []
    if len(prev) == len(state['preds']) and (1 if prev[idx] >= 0.5 else 0) != cls:
        return f'f{cls}'
    return f"p{cls}{'h' if conf >= 0.6 else 'm' if conf >= 0.25 else 'l'}"


def describe(name):
    kind = {'p': 'prediction', 'f': 'prediction that just flipped', 'l': 'training point', 'n': 'newest training point'}[name[0]]
    return f"{kind} {name[1]}" + (', model disagrees' if name.endswith('x') else '')


def fresh_state():
    preds, loss = train(SEED)
    return {'points': [dict(p) for p in SEED], 'next': 1, 'rounds': 1, 'teachers': ['ishaans04'], 'last': None,
            'preds': preds, 'prev': [], 'loss': loss, 'message': 'Seeded with 4 points. Your move.'}


def load():
    if STATE.exists():
        return json.loads(STATE.read_text(encoding='utf-8'))
    return fresh_state()


def play(state, user, r, c):
    label = state['next']
    existing = next((q for q in state['points'] if q['r'] == r and q['c'] == c), None)
    if existing:
        existing.update(label=label, by=user)
    else:
        state['points'].append({'r': r, 'c': c, 'label': label, 'by': user})
    state['prev'] = state['preds']
    state['preds'], state['loss'] = train(state['points'])
    state['next'] = 1 - label
    state['rounds'] += 1
    state['last'] = {'r': r, 'c': c, 'label': label, 'by': user}
    if user not in state['teachers']:
        state['teachers'] = (state['teachers'] + [user])[-500:]
    flips = sum(1 for a, b in zip(state['prev'], state['preds']) if (a >= 0.5) != (b >= 0.5))
    state['message'] = (f"@{user} placed a {label} at {LETTERS[c]}{r + 1}. Retrained on {len(state['points'])} points, "
                        f"{flips} tile{'s' if flips != 1 else ''} flipped.")
    return state['message']


def render(state):
    body = quote('Press "Submit new issue". A GitHub Action retrains the network and redraws the board in about a minute, then closes this issue.')
    rows = []
    for r in range(ROWS):
        cells = []
        for c in range(COLS):
            name = tile(state, r * COLS + c)
            title = quote(f'teach|{r}|{c}')
            cells.append(f'<a href="https://github.com/{REPO}/issues/new?title={title}&body={body}">'
                         f'<img src="assets/teach/{name}.svg" width="8.2%" alt="{LETTERS[c]}{r + 1}: {describe(name)}"></a>')
        rows.append(''.join(cells))
    n = state['next']
    return '\n'.join([
        '<!-- TEACH:START -->',
        f'<p align="center"><img src="assets/teach/next-{n}.svg" width="60%" alt="Your click places a {n}"></p>',
        '<p align="center">', '<br>\n'.join(rows), '</p>',
        f'<p align="center"><sub>{state["message"]}</sub><br>',
        f'<sub>{len(state["points"])} points · {len(state["teachers"])} teachers · {state["rounds"]} training rounds · loss {state["loss"]}</sub></p>',
        '<!-- TEACH:END -->'])


def main():
    title = os.environ.get('ISSUE_TITLE', '').strip()
    user = re.sub(r'[^A-Za-z0-9-]', '', os.environ.get('ISSUE_USER', 'someone'))[:39] or 'someone'
    state = load()
    match = re.fullmatch(r'teach\|([0-5])\|(\d{1,2})', title)
    if match and int(match.group(2)) < COLS:
        message = play(state, user, int(match.group(1)), int(match.group(2)))
    else:
        message = 'That tile was not recognised. Click a tile on the profile to teach the model.'
    readme = README.read_text(encoding='utf-8')
    readme, count = re.subn(r'<!-- TEACH:START -->.*?<!-- TEACH:END -->', lambda _: render(state), readme, flags=re.S)
    if count != 1:
        raise ValueError('Expected exactly one TEACH block in README')
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')
    README.write_text(readme, encoding='utf-8')
    out = os.environ.get('GITHUB_OUTPUT')
    if out:
        with open(out, 'a', encoding='utf-8') as fh:
            fh.write(f'message={message}\n')
    print(message)


if __name__ == '__main__':
    main()
