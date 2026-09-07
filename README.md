# 小護法養成記　語音導覽

普濟精舍　護博會展覽的行動語音導覽網頁。手機掃 QR code 開啟即可聆聽四個展區的導覽。

- `index.html`　導覽網頁（逐字稿也寫在裡面的 `TRACKS`）
- `make-audio.sh`　用 [edge-tts](https://github.com/rany2/edge-tts) 產生 `audio1~4.mp3`
- `audio1~4.mp3`　啟蒙區、歷練區、叛逆區、成長區
- `make-icon.py`　產生菩提葉圖示（`icon.svg`、`icon-*.png`、`apple-touch-icon.png`）
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

## 重新產生語音檔

```bash
pipx install edge-tts     # 或 pip install edge-tts
bash make-audio.sh
```

腳本會把逐字稿寫到 `txt/`，另存一份發音修正過的 `tts/` 再送去合成
（例如「精舍→精社」，讓「舍」唸四聲）。改稿子時記得 `index.html` 裡的文字也要一起改。

## 網址錨點

`#a1`～`#a4` 可直接連到指定展區，例如 `.../#a3` 會捲到叛逆區並highlight，
方便各展區放不同的 QR code。
