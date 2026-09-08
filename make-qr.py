#!/usr/bin/env python3
"""產生四個展區的 QR Code。需先安裝：pip install qrcode Pillow

  python3 make-qr.py [網址]

展區名稱直接從 index.html 的 TRACKS 讀，網址預設是 GitHub Pages 那個。
每一站輸出三種檔案到 qr/：
  a1.png        純 QR（去背，方便自己排版）
  a1.svg        純 QR 向量圖（印大張不會糊）
  a1-card.png   10×10 公分方形卡片 300dpi，可以直接印出來貼在展板上
"""
import io, os, re, sys
import qrcode
from qrcode.constants import ERROR_CORRECT_H
from PIL import Image, ImageDraw, ImageFont

BASE = sys.argv[1] if len(sys.argv) > 1 else "https://ding25025.github.io/puji-audio-guide/"
OUT  = "qr"

BG, FG   = (248, 246, 241), (33, 31, 26)     # 卡片底色、主要文字
GOLD     = (138, 106, 47)
MUTED    = (111, 106, 94)
SONG     = "/System/Library/Fonts/Supplemental/Songti.ttc"   # 宋體繁體
HEITI    = "/System/Library/Fonts/STHeiti Light.ttc"         # 黑體繁體
font = lambda path, size, idx: ImageFont.truetype(path, size, index=idx)


def tracks():
    """從 index.html 讀展區，避免兩邊資料不同步"""
    html = io.open("index.html", encoding="utf-8").read()
    got = re.findall(r"id:'(\w+)', title:'([^']+)', label:'([^']+)'", html)
    if not got:
        raise SystemExit("index.html 裡找不到 TRACKS")
    return got


def qr_matrix(url):
    q = qrcode.QRCode(error_correction=ERROR_CORRECT_H, border=4)
    q.add_data(url); q.make(fit=True)
    return q.get_matrix()


def qr_image(url, px, dark=FG, light=(255, 255, 255)):
    """畫成圖。背景一定要是實色：透明背景在很多軟體會被壓成黑底，就掃不到了"""
    m = qr_matrix(url)
    n = len(m)
    cell = max(1, px // n)
    img = Image.new("RGBA", (n * cell, n * cell), light + (255,))
    d = ImageDraw.Draw(img)
    for y, row in enumerate(m):
        for x, on in enumerate(row):
            if on:
                d.rectangle([x*cell, y*cell, (x+1)*cell-1, (y+1)*cell-1], fill=dark + (255,))
    return img          # 不再縮放：px 不是模組數的整數倍時，格子會忽寬忽窄而掃不到


def with_logo(qr, ratio=.21):
    """中央嵌菩提葉；容錯設為 H，遮住這點面積仍掃得到"""
    if not os.path.exists("icon-512.png"):
        return qr
    side = round(qr.width * ratio)
    pad  = round(side * .13)
    plate = Image.new("RGBA", (side + pad*2, side + pad*2), (0, 0, 0, 0))
    ImageDraw.Draw(plate).rounded_rectangle([0, 0, plate.width-1, plate.height-1],
                                            radius=plate.width*.24, fill=(255, 255, 255, 255))
    logo = Image.open("icon-512.png").convert("RGBA").resize((side, side), Image.LANCZOS)
    plate.paste(logo, (pad, pad), logo)
    qr = qr.copy()
    qr.paste(plate, ((qr.width - plate.width)//2, (qr.height - plate.height)//2), plate)
    return qr


def svg(url, path):
    m = qr_matrix(url); n = len(m)
    rects = "".join(f'<rect x="{x}" y="{y}" width="1" height="1"/>'
                    for y, row in enumerate(m) for x, on in enumerate(row) if on)
    io.open(path, "w", encoding="utf-8").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n} {n}" shape-rendering="crispEdges">'
        f'<rect width="{n}" height="{n}" fill="#fff"/><g fill="#{"%02x%02x%02x" % FG}">{rects}</g></svg>\n')


def headphone(d, x, cy, s, color):
    """耳機圖示：上方頭帶半圓 + 左右兩顆耳罩。x 是左緣，cy 是垂直中心"""
    r, cw, lw = s*.46, s*.26, max(3, round(s*.11))
    cx = x + r + cw/2
    d.arc([cx-r, cy-r, cx+r, cy+r], 180, 360, fill=color, width=lw)
    for ex in (cx-r, cx+r):
        d.rounded_rectangle([ex-cw/2, cy-lw/2, ex+cw/2, cy+r], radius=cw/2, fill=color)
    return 2*r + cw          # 佔用寬度


def card(url, num, path):
    """10×10 公分方形卡片，300dpi = 1181px。上方只留「耳機 語音導覽 NN」，下方留白"""
    W = H = 1181
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([30, 30, W-31, H-31], radius=44, outline=GOLD, width=4)

    f1, f2 = font(HEITI, 64, 0), font(SONG, 78, 2)
    t1, cy, s = "語音導覽", 130, 56
    iw, g1, g2 = s*1.18, 26, 28
    w1, w2 = d.textlength(t1, font=f1), d.textlength(num, font=f2)
    x = (W - (iw + g1 + w1 + g2 + w2)) / 2
    headphone(d, x, cy, s, GOLD)
    d.text((x + iw + g1, cy), t1, font=f1, fill=FG, anchor="lm")
    d.text((x + iw + g1 + w1 + g2, cy), num, font=f2, fill=GOLD, anchor="lm")
    d.text((W/2, 206), "拿起手機掃一掃，聽見這裡的故事", font=font(HEITI, 30, 0), fill=MUTED, anchor="mm")

    q = with_logo(qr_image(url, 800))
    qx, qy = (W - q.width)//2, 278
    d.rounded_rectangle([qx-26, qy-26, qx+q.width+25, qy+q.height+25], radius=28, fill=(255, 255, 255))
    img.paste(q, (qx, qy), q)
    img.save(path, dpi=(300, 300))


os.makedirs(OUT, exist_ok=True)
for i, (tid, title, label) in enumerate(tracks(), 1):
    url = BASE + "#" + tid
    with_logo(qr_image(url, 1200)).save(f"{OUT}/{tid}.png")
    svg(url, f"{OUT}/{tid}.svg")
    card(url, f"{i:02d}", f"{OUT}/{tid}-card.png")
    print(f"語音導覽 {i:02d}　{title}　{url}")
print(f"\n完成，檔案在 {OUT}/")
