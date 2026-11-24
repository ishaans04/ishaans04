"""Build the self-contained animated SVG artwork used by the profile."""
from html import escape
from pathlib import Path
import math

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"
OUT.mkdir(exist_ok=True)
INK = "#08101b"
WHITE = "#edf4ff"
MUTED = "#9aaec4"


def path(d, fill="none", stroke=INK, sw=3, **attrs):
    extra = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round" {extra}/>'


def circle(x, y, r, fill, stroke="none", sw=1, **attrs):
    extra = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'


def rect(x, y, w, h, fill, rx=0, stroke="none", **attrs):
    extra = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" {extra}/>'


def text(x, y, value, size=22, fill=WHITE, weight=400, mono=False, **attrs):
    extra = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" class="{"mono" if mono else "sans"}" {extra}>{escape(value)}</text>'


def star(cx, cy, outer, inner, fill):
    points = []
    for i in range(10):
        a = -math.pi / 2 + math.pi * i / 5
        r = outer if i % 2 == 0 else inner
        points.append(f"{cx+r*math.cos(a):.1f},{cy+r*math.sin(a):.1f}")
    return f'<polygon points="{" ".join(points)}" fill="{fill}"/>'


def character(name, x, y, width, height):
    """Inline the unmodified original PNG so GitHub needs no external fetch."""
    from base64 import b64encode
    image = b64encode((OUT/'characters'/f'{name}.png').read_bytes()).decode('ascii')
    return f'<image x="{x}" y="{y}" width="{width}" height="{height}" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{image}"/>'


def thor():
    return character('thor', 0, -68, 290, 420)


def ironman():
    return character('ironman', -5, 15, 290, 270) + '<g class="reactor">' + circle(194, 145, 25, 'none', '#9de9ff', 2, opacity='.5') + '</g>'


def captain():
    return character('captain', -5, 4, 300, 300)


def hulk():
    return character('hulk', -27, 42, 335, 260)


def spiderman():
    return character('spiderman', 38, 15, 230, 310)


STYLE = '''
.sans{font-family:'Segoe UI',Arial,Helvetica,sans-serif}.mono{font-family:Consolas,'Liberation Mono',monospace}
.arrival{animation:arrival 10s ease-in-out infinite}.name{animation:reveal 10s ease-in-out infinite}
.bolt{animation:bolt 10s ease-in-out infinite}.drift{animation:drift 5s ease-in-out infinite}
.reactor{animation:reactor 3s ease-in-out infinite}.exhaust{animation:exhaust .8s ease-in-out infinite;transform-origin:120px 310px}
.shield{transform-origin:196px 191px;animation:shield 7s ease-in-out infinite}
.smash{animation:smash 7s ease-in-out infinite;transform-origin:110px 300px}
.smash-fist{animation:punch 7s ease-in-out infinite;transform-origin:40px 170px}
.impact{animation:impact 7s ease-out infinite;transform-origin:65px 307px}
.hang{animation:hang 6s ease-in-out infinite;transform-origin:144px 0}
.deploy{animation:deploy 9s ease-in-out infinite}
.stone{animation:stone 4s ease-in-out infinite;transform-box:fill-box;transform-origin:center}
.orbit{animation:orbit 24s linear infinite;transform-origin:190px 225px}
@keyframes arrival{0%{transform:translateY(-35px);opacity:0}8%,95%{transform:translateY(0);opacity:1}100%{opacity:0}}
@keyframes reveal{0%,6%{opacity:0;transform:translateY(10px)}16%,96%{opacity:1;transform:translateY(0)}100%{opacity:0}}
@keyframes bolt{0%,5%{opacity:0}8%{opacity:.95}19%,100%{opacity:0}}
@keyframes drift{50%{transform:translateY(-7px)}}
@keyframes deploy{0%{opacity:.55;transform:translate(-25px,10px)}12%,92%{opacity:1;transform:translate(0,0)}100%{opacity:.55;transform:translate(8px,-6px)}}
@keyframes reactor{50%{opacity:.5}}
@keyframes exhaust{50%{transform:scaleY(.7);opacity:.6}}
@keyframes shield{0%,65%,100%{transform:rotate(0)}80%{transform:rotate(-20deg)}90%{transform:rotate(14deg)}}
@keyframes smash{0%,45%,100%{transform:translateY(0)}52%{transform:translateY(-12px)}60%{transform:translateY(5px)}70%{transform:translateY(0)}}
@keyframes punch{0%,45%,100%{transform:rotate(0)}52%{transform:rotate(18deg)}60%{transform:rotate(-8deg)}70%{transform:rotate(0)}}
@keyframes impact{0%,56%,80%,100%{opacity:0}60%{opacity:1}75%{opacity:0}}
@keyframes hang{0%,100%{transform:rotate(-5deg)}50%{transform:rotate(5deg)}}
@keyframes stone{50%{transform:translateY(-5px);opacity:.7}}
@keyframes orbit{to{transform:rotate(360deg)}}
@media(prefers-reduced-motion:reduce){*{animation:none!important}.bolt,.impact{opacity:0}}
'''


def svg(name, height, title, content, accent="#79dfff"):
    defs = f'''<defs>
    <linearGradient id="bg" x2="1" y2="1"><stop stop-color="#101d30"/><stop offset=".55" stop-color="#0b1422"/><stop offset="1" stop-color="#080e19"/></linearGradient>
    <radialGradient id="halo"><stop stop-color="{accent}" stop-opacity=".17"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>
    <pattern id="grid" width="36" height="36" patternUnits="userSpaceOnUse"><path d="M36 0H0V36" fill="none" stroke="#56718d" stroke-opacity=".08"/></pattern>
    <filter id="glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="6"/></filter>
    </defs>'''
    background = rect(1, 1, 1198, height-2, "url(#bg)", 20, "#22334a")
    background += rect(1, 1, 1198, height-2, "url(#grid)", 20)
    background += f'<ellipse cx="178" cy="{height/2}" rx="320" ry="{height*.8}" fill="url(#halo)"/>'
    background += path(f"M20 {height-1}H1180", stroke=accent, sw=2, opacity=".35")
    markup = f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}" role="img" aria-labelledby="title"><title id="title">{escape(title)}</title>{defs}<style>{STYLE}</style>{background}{content}</svg>'
    (OUT/name).write_text(markup, encoding="utf-8")


def chapter(num, hero, title, sub, illustration, accent, motion="drift"):
    content = circle(180, 151, 107, "none", accent, 1, opacity=".22")
    content += circle(180, 151, 88, "none", accent, 1, opacity=".12", stroke_dasharray="4 12")
    content += f'<g transform="translate(65 12) scale(.78)"><g class="deploy"><g class="{motion}">{illustration}</g></g></g>'
    content += text(365, 63, f"{num} / {hero.upper()}", 17, accent, 600, True, letter_spacing="3")
    content += text(362, 133, title, 58, weight=750, letter_spacing="-2")
    content += text(365, 179, sub, 24, MUTED)
    content += text(365, 230, "ISHAANS04  /  AVENGERS INITIATIVE", 14, "#607b95", mono=True, letter_spacing="2")
    content += text(1107, 88, num, 68, "#22354a", 800, text_anchor="middle")
    return content


def build():
    intro = text(42, 45, "AVENGERS INITIATIVE", 15, "#93dfff", 600, True, letter_spacing="4")
    intro += text(1155, 45, "PERSONNEL FILE / 04", 14, MUTED, mono=True, text_anchor="end")
    intro += '<g class="orbit">' + circle(190, 265, 145, "none", "#57b7e8", 1, opacity=".25", stroke_dasharray="120 20 4 20") + '</g>'
    intro += '<g transform="translate(32 140) scale(1.08)"><g class="arrival">' + thor() + '</g></g>'
    lightning = path("M174 2 134 48 158 46 114 100 137 96 125 123", stroke="#92eaff", sw=4)
    lightning += path("M135 47 92 66 102 91 76 120 M115 100 164 120 149 151", stroke="#71cbe7", sw=2)
    intro += '<g class="bolt">' + lightning + '</g>'
    intro += '<g class="name">'
    intro += text(398, 135, "CREATIVE TECHNOLOGIST  /  AI ENGINEER", 17, "#8bc8e5", mono=True, letter_spacing="2")
    intro += text(390, 247, "ISHAAN", 112, weight=800, letter_spacing="-5")
    intro += text(390, 354, "SHARMA", 112, weight=800, letter_spacing="-5")
    intro += rect(400, 384, 50, 4, "#7bddff", 2)
    intro += text(400, 430, "Ishaan builds AI that shows its work.", 31, "#b9eaff", 600)
    intro += text(400, 470, "Evidence. Guardrails. Interfaces that make sense.", 23, MUTED)
    intro += '</g>'
    intro += text(42, 536, "THOR / BRING THE THUNDER", 13, "#6d8fa9", mono=True, letter_spacing="2")
    intro += text(1155, 536, "SCROLL TO ASSEMBLE  ↓", 13, "#92b9d2", mono=True, text_anchor="end", letter_spacing="2")
    svg("hero-thor.svg", 562, "Ishaan Sharma. Ishaan builds AI that shows its work. Thor arrives with lightning.", intro)

    svg("arsenal-ironman.svg", 280,
        "Iron Man: The engineering arsenal. Intelligence needs an engine.",
        chapter("01", "Iron Man", "Intelligence needs an engine.", "The stack behind the suits.", ironman(), "#ffb965"), "#ffb965")

    svg("missions-captain.svg", 280,
        "Captain America: Featured projects. Built with a purpose.",
        chapter("02", "Captain America", "Built with a purpose.", "Four pinned projects. One clear standard: show the work.", captain(), "#85baff"), "#85baff")

    hulky = chapter("03", "Hulk", "Small commits. Big impact.", "The activity behind the builds.", hulk(), "#9dde79", "smash")
    hulky += '<g transform="translate(65 12) scale(.78)"><g class="impact">' + path("M65 307 25 299 4 313 M65 307 43 328 M65 307 100 315 118 308 M65 307 81 334", stroke="#a9e680", sw=3) + '</g></g>'
    svg("telemetry-hulk.svg", 280, "Hulk: Small commits, big impact. Public GitHub activity.", hulky, "#9dde79")

    spidey = chapter("04", "Spider-Man", "Good ideas need a connection.", "Have a useful problem? Let's build something that holds up.", "", "#ff8b9e")
    spidey += '<g transform="translate(50 0) scale(.8)"><g class="hang">'
    spidey += '<g transform="translate(0 0)">' + spiderman() + '</g></g></g>'
    svg("uplink-spiderman.svg", 320, "Spider-Man hangs from a web. Connect with Ishaan Sharma.", spidey, "#ff8b9e")

    stones = text(42, 47, "SIX STONES. ONE ENGINEERING PHILOSOPHY.", 17, "#b0c5dd", 600, True, letter_spacing="2")
    labels = [
        ("SPACE", "Connect", "APIs + MCP", "#6eacff"),
        ("MIND", "Reason", "Agents + RAG", "#f1d46f"),
        ("REALITY", "Verify", "Sources + tests", "#fb7c87"),
        ("POWER", "Engineer", "Systems + data", "#ba91fa"),
        ("TIME", "Recover", "State + replay", "#6cd5a0"),
        ("SOUL", "Design", "People + product", "#f6ad6c"),
    ]
    for i, (name, verb, detail, color) in enumerate(labels):
        x = 108+i*197
        stones += circle(x, 110, 34, color, opacity=".12", filter="url(#glow)")
        stones += f'<g class="stone" style="animation-delay:{i*.5}s">'
        stones += path(f"M{x} 77 {x+21} 91 {x+18} 122 {x} 139 {x-18} 122 {x-21} 91Z", color, "none", 0)
        stones += path(f"M{x} 77 {x+4} 101 {x+21} 91 M{x+4} 101 {x+18} 122 {x} 139 {x-5} 109 {x-21} 91Z", "#fff", "none", 0, opacity=".24")
        stones += '</g>'
        stones += text(x, 172, name, 13, color, 600, True, text_anchor="middle", letter_spacing="2")
        stones += text(x, 205, verb, 25, weight=700, text_anchor="middle")
        stones += text(x, 235, detail, 16, MUTED, text_anchor="middle")
    svg("infinity-stones.svg", 270, "Six Infinity Stones: Connect, Reason, Verify, Engineer, Recover, Design.", stones, "#b898ee")

    # A compact award graphic; all project details and links remain native README text.
    award = circle(97, 80, 44, "#2d261b", "#c29a4c", 1)
    award += star(97, 78, 23, 10, "#ffce7c")
    award += text(174, 56, "SQUARE ONE", 36, weight=800, letter_spacing="1")
    award += text(176, 91, "WINNER / HORIZON HACKATHON BY HOOLLOW / 2026", 18, "#e8bb71", 600, True)
    award += text(176, 126, "First attempt. First win.", 22, MUTED)
    svg("square-one-award.svg", 166, "Square One. Winner, Horizon Hackathon by Hoollow, 2026. First attempt, first win.", award, "#ffd087")


if __name__ == "__main__":
    build()
    print(f"Built {len(list(OUT.glob('*.svg')))} SVG assets in {OUT}")
