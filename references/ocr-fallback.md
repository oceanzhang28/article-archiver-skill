# OCR Fallback for Screenshot/Image Text Extraction

Use this when the vision API fails (e.g. DeepSeek provider rejects `image_url` content type with `unknown variant image_url, expected text`).

## Prerequisites

```bash
sudo apt-get install -y tesseract-ocr tesseract-ocr-chi-sim
pip3 install --break-system-packages pytesseract Pillow
```

## Workflow

### 1. Resize and split the image

WeChat group chat screenshots are often very tall (16000+ px). Split into ~2000px chunks for reliable OCR:

```python
from PIL import Image

img = Image.open('/path/to/screenshot.jpg')
h = img.size[1]
chunk_h = 2000

for i in range(0, h, chunk_h):
    box = (0, i, img.size[0], min(i + chunk_h, h))
    chunk = img.crop(box)
    path = f'/tmp/ocr_chunk_{i//chunk_h}.png'
    chunk.save(path, 'PNG')
```

### 2. OCR with Chinese+English

```python
import pytesseract

full_text = []
for chunk_path in sorted_chunk_paths:
    text = pytesseract.image_to_string(Image.open(chunk_path), lang='chi_sim+eng')
    full_text.append(text)

combined = '\n'.join(full_text)
```

### 3. Clean up OCR artifacts

Common OCR errors in WeChat screenshots:
- Line-break hyphenation within Chinese words (join adjacent short lines)
- `Al` → `AI` (common OCR confusion)
- `闻思修` sender name prefix on each message (strip or normalize)
- Horizontal rules and emoji treated as gibberish text (filter non-CJK lines)

### 4. Reconstruct message flow

Group consecutive lines from the same sender. Remove OCR noise (standalone symbols, broken English fragments). Add paragraph breaks where the original message had natural pauses.

### 5. Product-promo preview images (toolbook sales pages)

Product-sales pages (高绩效HR 198页可编辑PPT toolbook promos) carry NO prose — the body is banner + product intro + `— 资料预览 —` + N preview images of the product pages. To write real 摘要/核心要点 instead of fabricating from the title:

- **Download all preview images** (37 in the HRBP工具书 piece): extract the `![image](url)` list from the JSON body, strip the `#imgIndex=...` fragment, download with a ThreadPoolExecutor (8 workers, ~30s for 37 imgs). Save as `img_<n>.png` where n = imgIndex, so page order is preserved.
- **OCR a SAMPLE, not all**: first ~8 pages (usually the index/TOC: 痛点-解决路径索引, 场景化索引, 自评体系, 能力模型) + a few spread pages (e.g. 12/16/20/24/28) to cover the operational modules (人才盘点, 正向激励, 冲突调解, 人效核算).
- **Read for structure, not transcription**: OCR output is noisy (`SRS RST` / `SaRS Hes costal` garbled runs). Extract the toolbook's real framework — self-assessment dimensions, workflow steps, KPI formulas, chapter names — and use THAT for 摘要/核心要点. Don't try to transcribe every table cell.
- **Add a slide-note** in the archive body: the preview images ARE the article's content, so the note (`> **注**：本文为...产品推广帖，正文为预览图...`) tells the reader the images carry the substance.

## Pitfalls

- **Pillow in venv**: The Hermes venv may not have Pillow. Use `/usr/bin/python3` or install with `--break-system-packages`.
- **Very tall images**: Vision API will reject images with extreme aspect ratios. Always split before OCR.
- **Tesseract not installed**: Install requires sudo. Check with `which tesseract` first.
- **OCR quality varies**: Chinese text in screenshots with colored backgrounds or small fonts may produce noisy output. Manual cleanup of the final text is expected.
