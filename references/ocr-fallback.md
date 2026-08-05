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

## Pitfalls

- **Pillow in venv**: The Hermes venv may not have Pillow. Use `/usr/bin/python3` or install with `--break-system-packages`.
- **Very tall images**: Vision API will reject images with extreme aspect ratios. Always split before OCR.
- **Tesseract not installed**: Install requires sudo. Check with `which tesseract` first.
- **OCR quality varies**: Chinese text in screenshots with colored backgrounds or small fonts may produce noisy output. Manual cleanup of the final text is expected.
