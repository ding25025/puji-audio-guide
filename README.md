# 小護法養成記　語音導覽

普濟精舍　護博會展覽的行動語音導覽網頁。手機掃 QR code 開啟即可聆聽開場、五大核心與四個展區的導覽。

- `index.html`　導覽網頁（逐字稿也寫在裡面的 `TRACKS`）
- `make-audio.sh`　用 [edge-tts](https://github.com/rany2/edge-tts) 產生 `audio1~6.mp3`
- `audio1~6.mp3`　開場與調研、五大核心、啟蒙區、歷練區、叛逆區、成長區
- `make-icon.py`　產生菩提葉圖示（`icon.svg`、`icon-*.png`、`apple-touch-icon.png`）
- `make-qr.py`　產生六段導覽的 QR Code，輸出到 `qr/`
- `manifest.webmanifest`　讓手機可以「加入主畫面」，開啟時沒有瀏覽器介面

## 網頁功能

- 播放／暫停、前後跳轉 10 秒、進度條可點可拖
- 逐字稿預設收合，按「逐字稿」按鈕或開始播放才展開，一次只開一段
- 深色／淺色切換、大字模式，選擇會記在使用者自己的手機上
- 鍵盤可全程操作（Tab 移動、Enter 播放、進度條上用左右鍵 ±5 秒），
  並提供 ARIA 標記、焦點外框、高對比與減少動態的支援

## 重新產生圖示

```bash
pip install Pillow
python3 make-icon.py
```

## 重新產生 QR Code

```bash
pip install qrcode Pillow
python3 make-qr.py            # 換網址就在後面加上去：python3 make-qr.py https://...
```

段落名稱直接從 `index.html` 的 `TRACKS` 讀，不會兩邊對不上。每一段三種檔案：

| 檔案 | 用途 |
|---|---|
| `qr/a1-card.png` | A6 直式卡片 300dpi，可以直接印出來貼在展板上 |
| `qr/a1.png` | 純 QR，白底，自己排版用 |
| `qr/a1.svg` | 純 QR 向量圖，印大張不會糊 |

`qr/` 不進版控（產出檔量大又能隨時重跑），要印的時候自己跑一次就有。

容錯等級設 H，中央嵌菩提葉仍掃得到（已用解碼器驗證過，卡片縮到 22%、純 QR 縮到 15% 都還讀得出來）。

## 重新產生語音檔

```bash
pipx install edge-tts     # 或 pip install edge-tts
bash make-audio.sh
```

腳本會把逐字稿寫到 `txt/`，另存一份發音修正過的 `tts/` 再送去合成
（例如「精舍→精社」，讓「舍」唸四聲）。改稿子時記得 `index.html` 裡的文字也要一起改。

## 網址錨點

`#a1`～`#a6` 可直接連到指定段落，例如 `.../#a5` 會捲到叛逆區並 highlight，
方便各展區放不同的 QR code。
