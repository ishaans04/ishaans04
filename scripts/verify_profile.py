"""Validate profile assets and render the GitHub-sanitized Markdown for visual review."""
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT/'tmp'
TMP.mkdir(exist_ok=True)


def main():
    readme = (ROOT/'README.md').read_text(encoding='utf-8')
    # Markdown through GitHub's actual renderer, including details and table rules.
    payload = {'text': readme, 'mode': 'gfm', 'context': 'ishaans04/ishaans04'}
    response = subprocess.run(['gh','api','markdown','--input','-'], input=json.dumps(payload),
                              capture_output=True, text=True, encoding='utf-8', check=True)
    html = response.stdout
    for name in re.findall(r'src="assets/([^"]+)"', readme):
        assert (ROOT/'assets'/name).is_file(), name
        # API outputs a GitHub-hosted absolute image URL; replace only that asset.
        html = re.sub(r'(?:https://github.com/ishaans04/ishaans04/(?:raw|blob)/[^" ]+/)?assets/'+re.escape(name)+r'(?:\?raw=true)?',
                      '../assets/'+name, html)
    for asset in (ROOT/'assets').glob('*.svg'):
        tree = ET.fromstring(asset.read_text(encoding='utf-8'))
        assert tree.tag.endswith('svg')
        assert not any(node.tag.endswith(('script','foreignObject')) for node in tree.iter())
        assert not re.search(r'(?:href|src)="https?://', asset.read_text(encoding='utf-8'))
    assert not re.search(r'weekend|Friday|Sunday|mostly at hackathons|co-authored-by', readme, re.I)
    assert '<details>' in html and '<table' in html
    assert 'SENTRA' in html and 'Horizon' in html
    css = '''body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}
    :root{--bg:#0d1117;--fg:#d5dee8;--line:#30363d;--link:#70b9ff;--code:#222c39}
    body.light{--bg:#fff;--fg:#1f2328;--line:#d0d7de;--link:#0969da;--code:#eff1f3}
    article{box-sizing:border-box;max-width:1012px;margin:24px auto;padding:32px;border:1px solid var(--line);border-radius:6px}
    img{max-width:100%;height:auto;box-sizing:border-box}a{color:var(--link);text-decoration:none}a:hover{text-decoration:underline}
    p{margin:16px 0}h3{font-size:20px;line-height:1.3;margin:24px 0 16px}table{border-collapse:collapse;width:100%;display:block;overflow:auto;margin:16px 0}
    table table{display:table}th,td{border:1px solid var(--line);padding:12px 16px}tr:nth-child(2n){background:color-mix(in srgb,var(--code) 35%,transparent)}
    td p{margin:10px 0}td h3{margin:4px 0 12px}code{background:var(--code);border-radius:5px;padding:2px 6px;font-size:85%;white-space:normal}
    summary{cursor:pointer;padding:12px 0}sub{font-size:12px;color:var(--fg)}@media(max-width:600px){article{margin:0;padding:16px;border:0}th,td{padding:8px}table{font-size:14px}td h3{font-size:18px}}
    '''
    preview = TMP/'preview.html'
    preview.write_text('<!doctype html><html><meta charset="utf-8"><style>'+css+'</style><body><article>'+html+'</article></body></html>',encoding='utf-8')
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='msedge')
        page = browser.new_page(viewport={'width':1200,'height':900}, device_scale_factor=1)
        page.goto(preview.as_uri())
        page.wait_for_timeout(1700)
        images = page.locator('article img').evaluate_all('(xs)=>xs.map(x=>({src:x.getAttribute("src"),loaded:x.complete&&x.naturalWidth>0}))')
        assert all(x['loaded'] for x in images), images
        page.screenshot(path=str(TMP/'desktop-dark.png'),full_page=True)
        page.locator('body').evaluate('(e)=>e.classList.add("light")')
        page.screenshot(path=str(TMP/'desktop-light.png'),full_page=True)
        page.set_viewport_size({'width':390,'height':844})
        page.locator('body').evaluate('(e)=>e.classList.remove("light")')
        page.screenshot(path=str(TMP/'mobile.png'),full_page=True)
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Horizontal page overflow'
        # Each SVG is rendered independently for character and typography inspection.
        for asset in (ROOT/'assets').glob('*.svg'):
            page.set_viewport_size({'width':1200,'height':1100})
            page.goto(asset.as_uri())
            page.wait_for_timeout(1700)
            page.locator('svg').screenshot(path=str(TMP/(asset.stem+'.png')))
            overflow = page.locator('text').evaluate_all('''xs=>xs.map(e=>({text:e.textContent,b:e.getBBox()})).filter(e=>e.b.x < -2 || e.b.x+e.b.width>1202)''')
            assert not overflow, (asset.name, overflow)
        browser.close()
    print('Verified XML, self-contained assets, rendered images, Markdown tables/details, mobile width, and SVG text bounds.')
    print('Previews:', TMP)


if __name__ == '__main__':
    main()
