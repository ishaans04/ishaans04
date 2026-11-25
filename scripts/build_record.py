"""Build the About panel and the two panels its record rows open: Internship and Education.

GitHub allows one link per image, so the About and Internship panels are cut into
horizontal slices and the clickable rows become their own images. Every slice is drawn
in its panel's coordinates and shown through a viewBox window. The README stacks the
slices with align="top", which drops the baseline gap GitHub leaves under inline images,
so they meet edge to edge and read as one panel.

Education shows time enrolled and year of study, so the nightly activity workflow reruns
this script. Everything else comes out the same on every run.

    python scripts/build_record.py                    # as of today
    python scripts/build_record.py --date 2026-11-25  # as of a given day
"""
import argparse
import re
from datetime import date
from html import escape

from render_activity import BASE, DISP, FONT, MONO, PAL, ROOT, SANS, W, fit, label, measure, rule, t

# ---------------------------------------------------------------- facts (edit these)

CGPA = 8.5                  # out of 10, as on the résumé
ENROLLED = date(2024, 8, 1)  # B.Tech start
COURSE_YEARS = 4            # class of 2028
GITHUB = 'https://github.com/ishaans04'

ABOUT_LINES = ('MULTI-AGENT ORCHESTRATOR. I SEND', 'SWARMS OF AI AGENTS INTO THE FIELD,',
               'MAKE THEM ARGUE, CROSS-CHECK AND', 'ITERATE UNTIL THE PROOF HOLDS UP.')
ABOUT_SENTENCE = ('Multi-agent orchestrator. I send swarms of AI agents into the field, make them argue, '
                  'cross-check and iterate until the proof holds up.')

RECORD = [  # year, title, right-hand note, link target or None
    ('2026', 'WINNER, HORIZON HACKATHON', 'Hoollow · Square One · first attempt', None),
    ('2026', 'AGENTIC AI INTERN', 'IDCUBE Identification Systems · Jun–Jul  ↓', '#internship'),
    ('2024 →', 'B.TECH, INFORMATION TECHNOLOGY', 'Maharaja Surajmal Institute of Technology  ↓', '#education'),
    ('NOW', 'SPONSORSHIP HEAD', 'L.O.O.M. Society, MSIT', None),
]

INTERN_HEAD = ('TWO MONTHS, ONE AGENTIC PLATFORM,', 'SHIPPED END TO END.')
INTERN_SUB = 'Agentic AI Intern · June – July 2026 · Purple Fabric, RAG, API integration, React / TypeScript'
INTERN_ROWS = [  # title, name for alt text, tag under the title, two description lines, repository or None
    ('ENTERPRISEGPT', 'EnterpriseGPT', 'AGENTIC COMPLIANCE PLATFORM',
     ('Drove end-to-end development and deployment of an', 'agentic AI compliance platform.'), 'EnterpriseGPT'),
    ('2 AI AGENTS', 'Two AI agents', 'PURPLE FABRIC · RAG · APIS',
     ('Built on Purple Fabric with RAG and API integrations', 'to automate compliance workflows.'), None),
    ('FACE RECOGNITION', 'Face recognition', 'INSIGHTFACE · ARCFACE',
     ('Developed and trained a face detection and recognition', 'model on open-source InsightFace (ArcFace).'), 'Face-Recognition'),
]
INTERN_STACK = 'PURPLE FABRIC · RAG · API INTEGRATION · REACT · TYPESCRIPT · INSIGHTFACE'

CSS = '@keyframes rv{from{transform:translateY(110%)}}.rv{animation:rv .9s cubic-bezier(.16,1,.3,1) both;transform-box:fill-box}'


# ---------------------------------------------------------------- arithmetic

def gpa4(cgpa10):
    """Linear conversion of a 10-point CGPA to the 4-point scale."""
    return round(cgpa10 / 10 * 4, 2)


def plural(n, word):
    return f'{n} {word}{"" if n == 1 else "S"}'


def enrolment(today):
    """Months enrolled, year of study (1..COURSE_YEARS) and the share of the course behind us."""
    months = max(0, (today.year - ENROLLED.year) * 12 + today.month - ENROLLED.month - (today.day < ENROLLED.day))
    end = date(ENROLLED.year + COURSE_YEARS, ENROLLED.month, ENROLLED.day)
    share = min(1.0, max(0.0, (today - ENROLLED).days / (end - ENROLLED).days))
    year = min(COURSE_YEARS, months // 12 + 1)
    return months, year, share


def duration(months):
    y, m = divmod(months, 12)
    parts = ([plural(y, 'YEAR')] if y else []) + ([plural(m, 'MONTH')] if m or not y else [])
    return ', '.join(parts)


# ---------------------------------------------------------------- drawing

def doc(y0, h, title, bg, body):
    face = f"@font-face{{font-family:IS;src:url(data:font/woff2;base64,{FONT}) format('woff2');font-weight:900}}"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 {y0} {W} {h}" role="img" '
            f'aria-label="{escape(title)}"><title>{escape(title, quote=False)}</title>'
            f'<style>{face}{BASE}{CSS}@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>'
            f'<rect x="0" y="{y0}" width="{W}" height="{h}" fill="{bg}"/>{body}</svg>')


def headline(lines, top, fg, key, first_delay=.2, size=50):
    """Display lines that rise into place behind a clip, as in every panel's opening statement."""
    size = min([size] + [fit(line, 1120, size) for line in lines])
    out = []
    for i, line in enumerate(lines):
        y = top + i * 60
        out.append((y - 46, y + 14,
                    f'<clipPath id="{key}{i}"><rect x="0" y="{y - 46}" width="{W}" height="60"/></clipPath>'
                    f'<g clip-path="url(#{key}{i})">'
                    + t(38, y, line, size, fg, disp=True, cls='rv', style=f'animation-delay:{first_delay + i * .09:.2f}s')
                    + '</g>'))
    return out


def cut(blocks, windows, bg):
    """One (svg, title) per window; each SVG holds only the blocks that overlap its window."""
    out = {}
    for name, (y0, y1, title) in windows.items():
        body = ''.join(m for b0, b1, m in blocks if b0 < y1 and b1 > y0)
        out[name] = (doc(y0, y1 - y0, title, bg, body), title)
    return out


def about(theme):
    bg, fg = PAL[theme]
    blocks = [(0, 80, label(40, 56, '02', 'ABOUT', fg) + rule(76, fg))]
    blocks += headline(ABOUT_LINES, 140, fg, 'ab')
    blocks.append((400, 425, t(40, 420, 'RECORD', 13, fg, 700, ls=2.5)))
    for i, (year, title, note, _) in enumerate(RECORD):
        y = 440 + i * 64
        blocks.append((y, y + 64, f'<g class="up" style="animation-delay:{.8 + i * .1:.2f}s">' + rule(y, fg)
                       + t(40, y + 40, year, 14, fg, 700) + t(180, y + 42, title, 26, fg, disp=True)
                       + t(1160, y + 40, note, 16, fg, anchor='end', sans=True) + '</g>'))
    return cut(blocks, {
        'about': (0, 504, f'About: {ABOUT_SENTENCE} Record: winner, Horizon Hackathon 2026 (Hoollow, Square One, first attempt).'),
        'about-intern': (504, 568, '2026: Agentic AI intern, IDCUBE Identification Systems, June to July. Opens the internship panel.'),
        'about-btech': (568, 632, '2024 onward: B.Tech, Information Technology, Maharaja Surajmal Institute of Technology. '
                                  'Opens the education panel.'),
        'about-lead': (632, 746, 'Now: sponsorship head, L.O.O.M. Society, MSIT.'),
    }, bg)


def internship(theme):
    bg, fg = PAL[theme]
    blocks = [(0, 80, label(40, 56, '02·A', 'INTERNSHIP', fg)
               + t(1160, 56, 'IDCUBE IDENTIFICATION SYSTEMS PVT. LTD.', 13, fg, 700, 'end', 2.5) + rule(76, fg))]
    blocks += headline(INTERN_HEAD, 140, fg, 'ih')
    blocks.append((230, 260, t(40, 252, INTERN_SUB, 18, fg, sans=True, cls='fi', style='animation-delay:.45s')))
    blocks.append((290, 315, t(40, 310, 'WHAT I BUILT', 13, fg, 700, ls=2.5)))
    top, rh = 330, 84
    windows = {'internship': (0, top, 'Internship: Agentic AI intern at IDCUBE Identification Systems, June to July 2026. '
                                      'Two months, one agentic platform, shipped end to end. What I built:')}
    for i, (title, name, tag, lines, repo) in enumerate(INTERN_ROWS):
        y = top + i * rh
        body = (rule(y, fg) + t(40, y + 44, f'{i + 1:02d}', 14, fg, 700) + t(180, y + 46, title, 26, fg, disp=True)
                + t(180, y + 70, tag, 11, fg, 700, ls=1.5)
                + ''.join(t(620, y + 38 + k * 24, line, 16, fg, sans=True) for k, line in enumerate(lines)))
        if repo:
            body += t(1160, y + 40, '↗', 20, fg, anchor='end', sans=True)
        blocks.append((y, y + rh, f'<g class="up" style="animation-delay:{.6 + i * .1:.2f}s">{body}</g>'))
        windows[f'internship-{i + 1}'] = (y, y + rh, f'{i + 1:02d} {name}: {" ".join(lines)}'
                                          + (' Opens the repository.' if repo else ''))
    end = top + rh * len(INTERN_ROWS)
    blocks.append((end, end + 74, rule(end, fg) + t(40, end + 40, INTERN_STACK, 12, fg, 700, ls=1.2)))
    windows['internship-end'] = (end, end + 74, 'Stack: Purple Fabric, RAG, API integration, React, TypeScript, InsightFace.')
    return cut(blocks, windows, bg)


def education(theme, today):
    bg, fg = PAL[theme]
    months, year, share = enrolment(today)
    since = duration(months)
    grad = ENROLLED.year + COURSE_YEARS
    b = [label(40, 56, '02·B', 'EDUCATION', fg),
         t(1160, 56, 'MAHARAJA SURAJMAL INSTITUTE OF TECHNOLOGY', 13, fg, 700, 'end', 2.5), rule(76, fg)]
    b += [m for _, _, m in headline(['B.TECH, INFORMATION TECHNOLOGY'], 140, fg, 'eh')]
    b.append(t(40, 184, 'Maharaja Surajmal Institute of Technology, New Delhi · August 2024 to present', 18, fg,
               sans=True, cls='fi', style='animation-delay:.35s'))

    # Two score boxes: the résumé figure, and the same CGPA on a 4-point scale.
    for i, (value, out_of, name, note) in enumerate([
            (f'{CGPA:g}', '/ 10', 'CGPA · OUT OF 10', 'AS ON MY RÉSUMÉ'),
            (f'{gpa4(CGPA):.2f}', '/ 4', 'CGPA · OUT OF 4', f'= {CGPA:g} ÷ 10 × 4')]):
        x, w = 40 + i * 570, 550
        num = 110
        b.append(f'<g class="up" style="animation-delay:{.45 + i * .1:.2f}s">'
                 f'<rect x="{x + 1.5}" y="221.5" width="{w - 3}" height="177" fill="none" stroke="{fg}" stroke-width="3"/>'
                 + t(x + 30, 260, name, 13, fg, 700, ls=2.5) + t(x + w - 30, 260, note, 12, fg, 700, 'end', 1.2)
                 + t(x + 26, 372, value, num, fg, disp=True)
                 + t(f'{x + 26 + measure(value, num) + 16:.0f}', 372, out_of, 40, fg, disp=True) + '</g>')

    # Time enrolled, with the four years of the course as a bar.
    state = f'YEAR {year} OF {COURSE_YEARS} · CLASS OF {grad}' if share < 1 else f'CLASS OF {grad} · COMPLETE'
    b += [t(40, 452, 'TIME AT MSIT', 13, fg, 700, ls=2.5), t(1160, 452, state, 13, fg, 700, 'end', 2.5),
          t(40, 506, since, 40, fg, disp=True),
          t(f'{40 + measure(since, 40) + 16:.0f}', 506, 'and counting, since August 2024.', 18, fg, sans=True)]
    gap, seg = 10, (1120 - 3 * 10) / 4
    for k in range(COURSE_YEARS):
        x = 40 + k * (seg + gap)
        fill = min(1.0, max(0.0, share * COURSE_YEARS - k))
        bar = f'<rect x="{x + 1:.1f}" y="531" width="{seg - 2:.1f}" height="24" fill="none" stroke="{fg}" stroke-width="2"/>'
        if fill:
            bar += f'<rect x="{x:.1f}" y="530" width="{seg * fill:.1f}" height="26" fill="{fg}"/>'
        b.append(f'<g class="fi" style="animation-delay:{.7 + k * .12:.2f}s">{bar}'
                 + t(f'{x:.1f}', 580, f'AUG {ENROLLED.year + k}', 11, fg, 700, ls=1.5) + '</g>')
    b.append(t(1160, 580, str(grad), 11, fg, 700, 'end', 1.5))
    title = (f'Education: B.Tech, Information Technology at Maharaja Surajmal Institute of Technology, New Delhi, '
             f'since August 2024. CGPA {CGPA:g} out of 10, or {gpa4(CGPA):.2f} out of 4 on a linear scale. '
             f'{since.lower()} in: year {year} of {COURSE_YEARS}, class of {grad}.')
    return {'education': (doc(0, 616, title, bg, ''.join(b)), title)}


# ---------------------------------------------------------------- README

def picture(stem, alt, href=None):
    pic = (f'<picture><source media="(prefers-color-scheme: dark)" srcset="assets/{stem}-night.svg">'
           f'<img src="assets/{stem}-day.svg" width="100%" align="top" alt="{escape(alt)}"></picture>')
    return f'<a href="{href}">{pic}</a>' if href else pic


def readme_block(titles):
    """README markup for the three panels. Alt text is the slice titles, minus anything that changes daily."""
    grad = ENROLLED.year + COURSE_YEARS
    edu = (f'Education: B.Tech, Information Technology at Maharaja Surajmal Institute of Technology, New Delhi, since '
           f'August 2024. CGPA {CGPA:g} out of 10, or {gpa4(CGPA):.2f} out of 4 on a linear scale. Class of {grad}.')
    about_rows = [picture('about', titles['about'])]
    for row, stem in zip(RECORD[1:], ('about-intern', 'about-btech', 'about-lead')):
        about_rows.append(picture(stem, titles[stem], row[3]))
    intern = [picture('internship', titles['internship'])]
    for i, row in enumerate(INTERN_ROWS, 1):
        intern.append(picture(f'internship-{i}', titles[f'internship-{i}'], f'{GITHUB}/{row[4]}' if row[4] else None))
    intern.append(picture('internship-end', titles['internship-end']))
    return '\n'.join(['<!-- RECORD:START -->', '<a id="about"></a>', *about_rows, '',
                      '<a id="internship"></a>', *intern, '',
                      '<a id="education"></a>', picture('education', edu), '<!-- RECORD:END -->'])


def build(today):
    files, titles = {}, {}
    for theme in ('night', 'day'):
        for name, (svg, title) in {**about(theme), **internship(theme), **education(theme, today)}.items():
            files[f'{name}-{theme}.svg'] = svg
            titles[name] = title
    return files, titles


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', type=date.fromisoformat, default=date.today(), help='Build as of this day (YYYY-MM-DD)')
    args = parser.parse_args()
    files, titles = build(args.date)
    readme_path = ROOT / 'README.md'
    readme = readme_path.read_text(encoding='utf-8')
    readme, n = re.subn(r'<!-- RECORD:START -->.*?<!-- RECORD:END -->', lambda _: readme_block(titles), readme, flags=re.S)
    if n != 1:
        raise ValueError('Expected exactly one RECORD block in README')
    for name, svg in files.items():
        (ROOT / 'assets' / name).write_bytes(svg.encode('utf-8'))
    readme_path.write_bytes(readme.encode('utf-8'))
    print('Built', len(files), 'record panels as of', args.date.isoformat())


if __name__ == '__main__':
    main()
