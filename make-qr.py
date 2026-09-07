#!/usr/bin/env python3
"""產生四個展區的 QR Code。需先安裝：pip install qrcode Pillow

  python3 make-qr.py [網址]

展區名稱直接從 index.html 的 TRACKS 讀，網址預設是 GitHub Pages 那個。
每一站輸出三種檔案到 qr/：
  a1.png        純 QR（去背，方便自己排版）
  a1.svg        純 QR 向量圖（印大張不會糊）
  a1-card.png   A6 直式卡片 300dpi，可以直接印出來貼在展板上
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


def card(url, title, label, path):
    """A6 直式 300dpi"""
    W, H = 1240, 1748
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([28, 28, W-29, H-29], radius=46, outline=GOLD, width=4)

    if os.path.exists("icon-192.png"):
        leaf = Image.open("icon-192.png").convert("RGBA").resize((104, 104), Image.LANCZOS)
        img.paste(leaf, ((W - 104)//2, 122), leaf)

    d.text((W/2, 300), "小護法養成記", font=font(SONG, 62, 2), fill=FG, anchor="mm")
    d.text((W/2, 372), "普濟精舍　護博會展覽", font=font(HEITI, 34, 0), fill=MUTED, anchor="mm")

    q = with_logo(qr_image(url, 820))
    qx, qy = (W - q.width)//2, 470
    d.rounded_rectangle([qx-26, qy-26, qx+q.width+25, qy+q.height+25], radius=28, fill=(255, 255, 255))
    img.paste(q, (qx, qy), q)

    d.text((W/2, 1436), label, font=font(HEITI, 40, 0), fill=GOLD, anchor="mm")
    d.text((W/2, 1532), title, font=font(SONG, 96, 2), fill=FG, anchor="mm")
    d.text((W/2, 1632), "掃描聆聽語音導覽", font=font(HEITI, 38, 0), fill=MUTED, anchor="mm")
    img.save(path, dpi=(300, 300))


os.makedirs(OUT, exist_ok=True)
for tid, title, label in tracks():
    url = BASE + "#" + tid
    with_logo(qr_image(url, 1200)).save(f"{OUT}/{tid}.png")
    svg(url, f"{OUT}/{tid}.svg")
    card(url, title, label, f"{OUT}/{tid}-card.png")
    print(f"{label}　{title}　{url}")
print(f"\n完成，檔案在 {OUT}/")
