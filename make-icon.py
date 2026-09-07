#!/usr/bin/env python3
"""產生網站圖示（菩提葉）。需先安裝 Pillow：pip install Pillow

  python3 make-icon.py

輸出 icon.svg、favicon-32.png、icon-192.png、icon-512.png、apple-touch-icon.png。
葉形是同一組貝茲曲線，SVG 與 PNG 兩邊共用，改形狀只要改下面的控制點。
"""
from PIL import Image, ImageDraw

S      = 512                    # 設計用的座標系
SUPER  = 4                      # 先畫大張再縮小，邊緣才平滑
GOLD_1 = (176, 138, 66)         # 底色漸層（上）
GOLD_2 = (122,  92, 39)         # 底色漸層（下）
LEAF   = (253, 250, 242)        # 葉子
VEIN   = (150, 116, 54)         # 葉脈

# 菩提葉輪廓：從頂端凹口出發，沿右側繞到葉尖，左側鏡像
N = (256, 156)                                  # 頂端凹口（心形的缺口）
R = (452, 268)                                  # 右側最寬處
T = (256, 512)                                  # 葉尖
SEG = [(N, (332,  58), (446, 126), R),          # 右上：肩膀圓一點
       (R, (452, 388), (346, 430), T)]          # 右下：一路收成尖角
SCALE = .86                                     # 整片葉子內縮，不要頂到邊
OY    = -28                                     # 往上挪一點，視覺才置中
VEIN_A, VEIN_B = (256, 252), (256, 436)         # 中脈起訖
mir = lambda p: (S - p[0], p[1])                # 左右鏡像
fit = lambda p: (S/2 + (p[0] - S/2) * SCALE, S/2 + (p[1] - S/2) * SCALE + OY)


def cubic(p0, p1, p2, p3, n=90):
    out = []
    for i in range(n + 1):
        t = i / n; u = 1 - t
        out.append((u*u*u*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t*t*t*p3[0],
                    u*u*u*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t*t*t*p3[1]))
    return out


def outline():
    pts = []
    for seg in SEG:
        pts += cubic(*seg)
    for seg in reversed(SEG):                   # 左側：鏡像後反向接回頂端
        pts += cubic(*[mir(p) for p in reversed(seg)])
    return [fit(p) for p in pts]


def svg_path():
    n = lambda p: "%g %g" % fit(p)
    d = "M" + n(N)
    for _, c1, c2, p in SEG:
        d += " C%s %s %s" % (n(c1), n(c2), n(p))
    for p0, c1, c2, _ in reversed(SEG):
        d += " C%s %s %s" % (n(mir(c2)), n(mir(c1)), n(mir(p0)))
    return d + " Z"


def render(size, rounded=True):
    k = size * SUPER / S
    w = size * SUPER
    img = ImageDraw.Draw(Image.new("RGBA", (w, w), (0, 0, 0, 0)))
    base = img._image
    for y in range(w):                          # 直向漸層
        f = y / (w - 1)
        img.line((0, y, w, y), fill=tuple(round(a + (b - a) * f) for a, b in zip(GOLD_1, GOLD_2)) + (255,))
    if rounded:                                 # favicon 自己帶圓角；iOS 會自己裁，所以滿版
        mask = Image.new("L", (w, w), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, w - 1), radius=w * 0.22, fill=255)
        base.putalpha(mask)
    img.polygon([(x * k, y * k) for x, y in outline()], fill=LEAF + (255,))
    line = lambda p, q, w: img.line([(fit(p)[0] * k, fit(p)[1] * k), (fit(q)[0] * k, fit(q)[1] * k)],
                                    fill=VEIN + (255,), width=max(1, round(w * k)))
    line(VEIN_A, VEIN_B, 13)
    return base.resize((size, size), Image.LANCZOS)


for name, size, rounded in [("favicon-32.png", 32, True), ("icon-192.png", 192, True),
                            ("icon-512.png", 512, True), ("apple-touch-icon.png", 180, False)]:
    render(size, rounded).convert("RGB" if not rounded else "RGBA").save(name)
    print("產生", name)

open("icon.svg", "w").write(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}">
  <defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#{"%02x%02x%02x" % GOLD_1}"/>
    <stop offset="1" stop-color="#{"%02x%02x%02x" % GOLD_2}"/>
  </linearGradient></defs>
  <rect width="{S}" height="{S}" rx="{round(S * 0.22)}" fill="url(#g)"/>
  <path d="{svg_path()}" fill="#{"%02x%02x%02x" % LEAF}"/>
  <path d="M{"%g %g" % fit(VEIN_A)} L{"%g %g" % fit(VEIN_B)}" stroke="#{"%02x%02x%02x" % VEIN}" stroke-width="13" stroke-linecap="round" fill="none"/>
</svg>
''')
print("產生 icon.svg")
