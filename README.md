# 小護法養成記　語音導覽

普濟精舍　護博會展覽的行動語音導覽網頁。手機掃 QR code 開啟即可聆聽四個展區的導覽。

- `index.html`　導覽網頁（逐字稿也寫在裡面的 `TRACKS`）
- `make-audio.sh`　用 [edge-tts](https://github.com/rany2/edge-tts) 產生 `audio1~4.mp3`
- `audio1~4.mp3`　啟蒙區、歷練區、叛逆區、成長區

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
