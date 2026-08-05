# Slide-Based / Image-Heavy WeChat Articles

Some WeChat articles (especially from accounts like 高绩效HR) are published as slide decks — each "paragraph" is an `<img>` tag showing a presentation slide, with minimal or no text between images.

## Recognition

After extraction with `extraction-script.py`:
- `body_length` may be large but the markdown is mostly `![image](url)` lines with ~5-20 Chinese characters between them
- The article reads like slide titles, not prose paragraphs
- There are 30+ images in sequence

## Extraction Template

When the article is identified as slide-based, use this adapted structure:

```markdown
> **注**：本文原为幻灯片形式发布，正文内容嵌入在图片中。以下为从页面中提取的文字框架。图片部分保留了原文的幻灯片截图链接。

### 一、[Section from extracted heading]

[bullet points and text between images]

---

![幻灯片N](image-url)

---
```

## Summary Writing

- Base summaries on the extracted text framework (headings, bullet points, any prose between images).
- Do NOT fabricate detail. If the text says "40+关键指标" without listing them, say "40+关键指标" — don't guess which ones.
- The slide images will contain far more detail than the extracted text. Acknowledge this in the summary if the text framework is thin — or better, run the full OCR extraction below to build a real framework.
- Still write all mandatory sections (摘要, 核心要点, 这篇解决什么问题, 快速判断).

## Image Handling

- Preserve all image links in order within `## 原文`.
- Images are critical content here, not decoration — they ARE the article body.
- Group consecutive slides under a section heading if the extracted text provides one.
- Use sequential naming: `![幻灯片1]`, `![幻灯片2]`, etc.

## Example

Article: "美的集团组织与人才效能指标体系与评价体系" (高绩效HR, 2026-07-01)
- 49 slides images, sparse text framework
- Extracted framework: "7+3" mechanism, 8-dimension indicators, 5 functional categories, trinity coordination
- Summaries written from framework text, all images preserved

Article: "华为干部管理体系全景手册（120页PPT）" (高绩效HR, 2026-08-01)
- 120 slides + cover + ads (124 images total), text framework between images was only promo text
- Full OCR produced a rich framework: 7 篇 dividers (战略/标准/选拔/考核/发展/继任/监察) + 总结
- Archive rebuilt with per-篇 bullet frameworks + images grouped by index ranges

## Full OCR Framework Extraction (preferred for large decks)

When the extracted text framework is thin (~5-20 chars between images), do NOT settle for a skeleton summary. Download all slide images and OCR them to build a real, searchable framework — this turns an image-only archive into something text-searchable in Obsidian.

### 1. Extract image URLs

```python
import json, re, os
with open('/tmp/article_meta.json') as f:
    data = json.load(f)
urls = re.findall(r'!\[[^\]]*\]\((https://mmbiz\.qpic\.cn/[^)]+)\)', data['body_markdown'])
os.makedirs('/tmp/slides', exist_ok=True)
with open('/tmp/slide_urls.txt','w') as f:
    for i, u in enumerate(urls):
        f.write(f"{i}\t{u}\n")
```

### 2. Download concurrently via a .sh file

The terminal tool rejects inline `&` backgrounding in foreground commands ("Use terminal(background=true)…"). Write the loop to a script and run `bash /tmp/download_slides.sh`. Strip `&watermark=...` and `#imgIndex=...` query fragments for cleaner downloads:

```bash
#!/bin/bash
cd /tmp/slides
cat /tmp/slide_urls.txt | while IFS=$'\t' read -r i u; do
  clean="${u%%&watermark*}"
  clean="${clean%%&randomid*}"
  clean="${clean%%#imgIndex*}"
  curl -s -m 30 -A "Mozilla/5.0" -o "slide_${i}.jpg" "$clean" &
  if (( $(jobs -r | wc -l) >= 8 )); then wait; fi
done
wait
echo "downloaded: $(ls /tmp/slides/ | wc -l)"
```

### 3. OCR every slide (background with notify)

```bash
#!/bin/bash
cd /tmp/slides
: > /tmp/slides_ocr.txt
for f in $(ls slide_*.jpg | sort -V); do
  idx="${f%.jpg}"; idx="${idx#slide_}"
  echo "===== SLIDE $idx =====" >> /tmp/slides_ocr.txt
  tesseract "$f" - -l chi_sim+eng --psm 3 2>/dev/null >> /tmp/slides_ocr.txt
  echo "" >> /tmp/slides_ocr.txt
done
```

Run with `terminal(background=true, notify_on_complete=true)` — 120 images ≈ 5-8 min. Poll `grep -c '^===== SLIDE' /tmp/slides_ocr.txt` for progress.

### 4. Map slides to deck sections

Image-URL order in the extraction body == slide index 1:1 (`slide_0` = cover). OCR reveals the deck's internal structure — PPT decks have divider slides like `战略篇 / 标准篇 / 选拔篇 / 考核篇 / 发展篇 / 继任篇 / 监察篇`. Use divider slide indices to group image ranges per section.

### 5. Rebuild 原文 with framework + grouped images

For each 篇: `### 篇名` heading, a bullet framework synthesized from OCR text (keep the slide's real numbers, e.g. `A+ 10% / B+ 20% / B 50% / C+D 20%`, `7-2-1 学习模型`), then the slide images for that range in original order. Drop pure-ad images (会员卡图, QR codes) but keep their surrounding text; keep the cover and trailing course-ad images.

### 6. Rewrite summaries from OCR-verified content

摘要/核心要点 should come from what the slides actually say — OCR often confirms, corrects, or enriches the framework, and lets you include concrete percentages, product names, and tool names that were invisible in the raw extraction.
