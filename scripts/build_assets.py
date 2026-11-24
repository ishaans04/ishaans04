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


def thor():
    a = []
    # Cape, hair, layered armor and one raised hammer arm.
    a += [path("M83 129 Q32 165 24 299 L89 276 119 316 167 283 216 306 Q212 223 174 131Z", "#9a293e"),
          path("M83 137 Q51 211 51 283 L83 256 115 298 108 154Z", "#da4052", sw=0),
          path("M100 68 Q68 78 70 136 L57 166 84 158 107 131 150 153 180 159 171 111 Q172 69 137 64Z", "#d6a94f"),
          path("M83 106 Q84 69 121 68 Q158 69 158 109 L148 144 117 158 88 137Z", "#edb697"),
          path("M88 115 100 124 108 119 M132 119 142 124 153 116", stroke="#8c5142", sw=2),
          path("M101 102 115 105 M135 105 148 101", stroke=INK, sw=3),
          path("M106 108 113 109 M137 109 144 108", stroke="#dffcff", sw=3),
          path("M123 107 119 122 126 123 M111 132 Q126 141 140 129", stroke="#9e604c", sw=2),
          path("M83 92 Q82 61 119 57 Q159 58 164 86 L160 110 148 84 127 81 104 88 88 118Z", "#efc96a"),
          path("M91 73 111 66 M143 71 155 83 M78 124 74 146", stroke="#ffe7a0", sw=3),
          path("M93 138 116 156 147 141 178 160 171 240 146 268 89 254 65 192Z", "#263c53"),
          path("M102 160 120 172 148 155 163 199 148 235 102 226 89 185Z", "#405971"),
          path("M84 159 Q58 151 47 172 L40 211 64 220 85 185Z", "#e5aa8a"),
          path("M46 207 40 238 65 248 74 217Z", "#9ab5c7"),
          path("M161 160 178 139 190 91 214 94 207 159 183 193Z", "#e6b293"),
          path("M187 100 185 76 215 72 220 100Z", "#abc5d4"),
          path("M190 74 190 59 Q200 48 213 58 L216 75Z", "#edb697"),
          path("M96 233 145 243 164 263 149 308 122 311 116 274 98 304 73 297 83 259Z", "#18283c")]
    for x, y in [(94, 171), (150, 174), (99, 207), (148, 209)]:
        a += [circle(x, y, 13, "#9fb6c8", INK, 2), circle(x-3, y-3, 5, "#e1edf4")]
    a += [rect(89, 237, 62, 10, "#98a9b7", 3), rect(112, 236, 20, 13, "#d8e5ed", 2),
          '<g class="hammer">',
          path("M201 58 201 8", stroke="#624a37", sw=12),
          path("M201 55 201 12", stroke="#c1a276", sw=4),
          path("M168 7 180 -5 228 -5 239 7 239 35 226 45 177 45 168 34Z", "#a9c3d6"),
          path("M180 -5 180 33 168 34 M180 33 227 33 239 35 M227 -5 227 33", stroke="#e6f7ff", sw=2),
          path("M182 1 221 1 M183 8 215 8 M183 17 205 17", stroke="#6e8fa8", sw=2), '</g>']
    return ''.join(a)


def ironman():
    a = [path("M85 108 Q57 115 42 145 L54 200 82 180 97 144Z", "#ab263b"),
         path("M155 111 181 120 198 155 176 173 147 144Z", "#ca3543"),
         path("M77 130 101 107 144 108 166 137 157 205 137 238 95 227 75 179Z", "#b62b3e"),
         path("M96 123 119 137 144 123 154 151 137 173 101 170 86 147Z", "#e54953"),
         path("M84 174 101 180 138 180 155 165 M99 194 137 198 M98 208 135 214", stroke="#661d31", sw=5),
         path("M100 61 102 40 122 30 147 39 155 58 150 101 134 117 111 107 101 88Z", "#c63744"),
         path("M109 48 120 51 138 45 147 52 145 81 135 103 118 99 109 81Z", "#e9b75c"),
         path("M109 65 122 69 126 76 133 69 148 64", stroke="#813d31", sw=3),
         path("M113 68 123 71 M134 71 144 68", stroke="#d9ffff", sw=4),
         path("M119 91 136 91", stroke="#703728", sw=3),
         path("M103 43 108 34 132 25 151 37", stroke="#f26668", sw=3),
         path("M85 225 103 226 112 269 92 302 69 294 84 259Z", "#a7293a"),
         path("M117 231 139 228 157 258 165 297 143 303 127 270Z", "#c13542"),
         path("M85 248 103 251 102 270 85 275Z", "#e5b153"),
         path("M134 252 151 258 155 278 139 275Z", "#e9b75c"),
         path("M72 290 94 295 92 310 60 309Z", "#db414a"),
         path("M143 295 165 290 180 310 147 311Z", "#dc424c"),
         path("M44 147 30 165 38 201 58 212 73 195 61 177Z", "#d5a04b"),
         path("M37 193 32 221 58 233 72 214 60 201Z", "#c83b46"),
         path("M179 146 202 144 220 125 236 139 219 175 195 185 176 169Z", "#e6af54"),
         path("M214 126 216 111 221 102 226 117 228 96 233 95 237 115 242 101 247 105 245 124 255 115 261 121 248 143 229 149Z", "#d5434d"),
         circle(122, 154, 17, "#4dbfdd", INK, 3), circle(122, 154, 11, "#d4fbff"),
         '<g class="reactor">', circle(122, 154, 22, "none", "#9de9ff", 2),
         circle(236, 128, 11, "#d9fcff"), circle(236, 128, 17, "none", "#73dcff", 2), '</g>',
         '<g class="exhaust">', path("M68 313 76 361 90 315Z", "#9deeff", sw=0),
         path("M146 314 160 363 164 313Z", "#9deeff", sw=0), '</g>']
    return ''.join(a)


def captain():
    a = [path("M94 125 67 140 45 188 61 209 92 179Z", "#315e92"),
         path("M56 195 43 235 63 247 83 213Z", "#b93748"),
         path("M87 126 117 115 155 128 171 161 155 223 134 245 92 233 73 173Z", "#345c83"),
         path("M85 143 116 131 151 143 155 179 132 198 92 184Z", "#487baa"),
         path("M99 68 Q101 38 126 38 Q156 39 157 72 L150 106 133 123 111 113 101 91Z", "#dca88e"),
         path("M98 76 97 55 110 32 143 29 160 50 159 86 146 87 145 67 112 67 111 87 100 87Z", "#3b6c9a"),
         path("M109 77 121 79 M136 79 147 75", stroke="#1d334b", sw=3),
         path("M126 79 123 94 130 95 M120 104 138 103", stroke="#975e4d", sw=2),
         text(119, 58, "A", 24, WHITE, 800),
         path("M91 53 81 48 90 70 100 75 M160 50 171 45 162 70 157 73", "#d4e7ef"),
         star(121, 158, 26, 11, "#ecf4f7"),
         path("M95 195 105 198 105 229 95 225Z", "#e6eef4"),
         path("M112 201 123 202 123 235 112 233Z", "#cb3b4e"),
         path("M131 202 142 197 141 229 131 234Z", "#e6eef4"),
         path("M90 234 116 240 110 273 100 308 74 306 86 268Z", "#2b4667"),
         path("M124 239 144 229 158 264 164 307 141 311 130 273Z", "#315376"),
         path("M78 283 105 288 101 315 67 315Z", "#ab3042"),
         path("M139 288 162 285 175 314 142 315Z", "#bb3749"),
         rect(88, 229, 57, 10, "#654a3c", 2), rect(111, 228, 16, 13, "#bdcbd2", 2),
         '<g class="shield">', circle(196, 191, 73, "#c9364c", INK, 4),
         circle(196, 191, 58, "#e5edf3"), circle(196, 191, 43, "#c9364c"),
         circle(196, 191, 30, "#396a9b"), star(196, 191, 25, 10, "#f3f8ff"),
         path("M151 153 Q179 127 210 136", stroke="#ff94a3", sw=3), '</g>']
    return ''.join(a)


def hulk():
    return ''.join([
        path("M81 135 Q50 131 28 162 L15 212 42 238 73 216 87 181Z", "#488e4b"),
        path("M150 140 Q178 122 203 145 L230 185 209 213 174 195 155 177Z", "#65af60"),
        path("M80 129 113 113 151 129 177 166 159 224 130 253 85 238 59 188Z", "#62ab59"),
        path("M76 159 Q94 141 117 155 Q138 141 158 156 L151 186 124 194 84 182Z", "#7fc66b", sw=2),
        path("M85 202 112 209 146 202 M92 219 119 225 139 217 M119 164 120 197", stroke="#387a3f", sw=3),
        path("M94 76 Q94 47 123 44 Q154 44 160 73 L155 110 135 131 110 120 94 98Z", "#7ab866"),
        path("M92 86 87 66 98 36 115 40 124 30 135 40 152 36 166 58 160 88 145 66 132 70 119 61 108 74Z", "#1b302a"),
        path("M101 83 118 88 M137 88 153 82", stroke="#213c2e", sw=5),
        path("M107 89 116 90 M139 91 148 88", stroke="#e8f3bc", sw=3),
        path("M126 90 121 105 131 106", stroke="#437345", sw=3),
        path("M111 112 144 110 137 120 119 120Z", "#e2eac8", sw=2),
        path("M71 226 99 237 131 240 157 221 175 251 151 279 123 265 97 279 66 260Z", "#665080"),
        path("M97 244 96 268 M135 244 145 266", stroke="#423650", sw=4),
        path("M65 260 94 274 83 300 50 304 42 288Z", "#609a52"),
        path("M146 276 172 253 192 277 204 302 167 311 154 295Z", "#71b15d"),
        path("M48 292 75 293 87 311 79 322 34 321 28 314Z", "#7abd65"),
        path("M176 299 199 294 217 312 211 322 164 322 159 315Z", "#79b965"),
        '<g class="smash-fist">',
        path("M25 206 55 213 77 241 72 269 55 285 18 279 4 254 8 226Z", "#78b966"),
        path("M13 234 30 231 42 236 58 234 70 244 M20 251 38 254 M42 255 57 257 M22 269 52 273", stroke="#3b7442", sw=3),
        '</g>',
        path("M179 174 Q191 151 205 162 L218 181 212 195 198 201 181 192Z", "#82c76a"),
        path("M190 167 204 178 M186 177 199 186", stroke="#4e8d47", sw=3)])


def spiderman():
    # Draw upright, then hang the whole figure upside down.
    a = [path("M87 119 64 122 48 96 50 49 70 43 77 88 102 103Z", "#c43d4c"),
         path("M145 117 164 108 179 75 174 41 194 35 204 80 183 133 157 145Z", "#cf4050"),
         path("M91 105 125 96 153 111 164 152 143 198 99 188 80 150Z", "#cf4050"),
         path("M85 128 99 154 102 186 86 176 76 146Z", "#2d6395"),
         path("M153 129 138 157 139 190 156 179 166 148Z", "#255582"),
         path("M98 61 Q98 31 124 30 Q153 30 155 61 L147 88 126 103 106 88Z", "#db4756"),
         path("M105 55 121 64 117 78 109 74Z", "#e8f4fa", sw=3),
         path("M147 54 130 64 134 79 144 73Z", "#e8f4fa", sw=3),
         path("M125 33 125 98 M100 50 151 50 M102 83 149 84 M106 36 143 92 M146 37 108 92", stroke="#70283b", sw=1.3),
         path("M100 186 121 195 105 226 79 243 69 221 88 203Z", "#2f6492"),
         path("M124 195 143 188 166 212 164 241 139 240 138 220Z", "#326b9b"),
         path("M71 218 83 239 56 260 37 253 40 237Z", "#c53c4e"),
         path("M141 236 165 231 183 249 173 266 148 263Z", "#c53c4e"),
         path("M50 48 47 29 55 13 64 17 63 33 74 29 79 37 69 49Z", "#d84856"),
         path("M175 43 166 26 173 15 184 22 190 12 197 18 194 35Z", "#cf4050"),
         path("M121 121 127 134 133 119 M124 134 124 157 M119 138 108 130 M128 139 139 130 M119 147 108 154 M129 147 139 154 M122 154 116 168 M127 154 132 169", stroke="#152b40", sw=3),
         path("M94 110 154 114 M85 127 161 132 M94 174 150 179 M102 105 98 184 M145 108 146 184 M60 58 72 57 M52 78 75 78 M180 57 198 54 M179 77 203 74", stroke="#7e2c40", sw=1.2)]
    return '<g transform="translate(256 292) rotate(180 0 0)">' + ''.join(a) + '</g>'


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
.stone{animation:stone 4s ease-in-out infinite;transform-box:fill-box;transform-origin:center}
.orbit{animation:orbit 24s linear infinite;transform-origin:190px 225px}
@keyframes arrival{0%{transform:translateY(-35px);opacity:0}8%,95%{transform:translateY(0);opacity:1}100%{opacity:0}}
@keyframes reveal{0%,6%{opacity:0;transform:translateY(10px)}16%,96%{opacity:1;transform:translateY(0)}100%{opacity:0}}
@keyframes bolt{0%,5%{opacity:0}8%{opacity:.95}19%,100%{opacity:0}}
@keyframes drift{50%{transform:translateY(-7px)}}
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
    content += f'<g transform="translate(65 12) scale(.78)"><g class="{motion}">{illustration}</g></g>'
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
    lightning = path("M257 2 226 77 255 72 219 144 242 139 211 209", stroke="#92eaff", sw=4)
    lightning += path("M227 76 181 95 191 120 165 149 M219 145 272 165 257 196", stroke="#71cbe7", sw=2)
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
    spidey += path("M144 -10V53", stroke="#c4d8e8", sw=2)
    spidey += '<g transform="translate(0 32)">' + spiderman() + '</g></g></g>'
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
