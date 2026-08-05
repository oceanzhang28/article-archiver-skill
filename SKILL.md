---
name: article-archiver
description: "Use when the user asks to archive, save, transfer, or batch-import WeChat public-account articles, web articles, article links, Feishu documents, or long text into Obsidian knowledge folders with complete original body, summaries, and entry-page links."
---

# Article Archiver

Archive articles into Obsidian `00知识库/`: preserve the full original body, add structured notes before it, classify the article, and update the matching entry page.

## Vault Layout

- Vault root in Hermes: `/mnt/obsidian/`
- HR articles: `00知识库/HR知识/`, entry page `00知识库/HR知识入口.md`
- AI articles: `00知识库/AI知识/`, entry page `00知识库/AI知识入口.md`
- Business articles: `00知识库/商业知识/`, entry page `00知识库/商业知识入口.md`
- 卡兹克 articles: `00知识库/卡兹克/`, entry page `00知识库/卡兹克入口.md`
- 卡兹克 subfolders: `AI资讯`, `claude code`, `codex`, `prompt`, `skills`, `workbuddy`

## Core Rules

1. Preserve the full article body. Do not replace the original article with a summary.
2. For WeChat articles, preserve structure from HTML blocks before converting to Markdown. Do not strip all HTML first.
3. Put notes before the original body using the standard template below.
4. Update the relevant entry page once per archived article and avoid duplicate links.
5. In the Jianguoyun WebDAV environment, write through WebDAV PUT and verify with WebDAV GET. Do not rely on the FUSE mount for persistence or for reads that follow any write — the FUSE cache becomes stale after WebDAV PUT operations.

## Read Article Content

### WeChat Public-Account URLs

For `mp.weixin.qq.com` URLs, read `references/wechat-extraction.md` and use `references/extraction-script.py`.

Required behavior:
- Fetch the article HTML with browser or curl.
- Extract metadata from JavaScript variables and fallback footer patterns.
- Extract `div#js_content` or `content_noencode` as HTML.
- Convert the body HTML to semantic Markdown while preserving paragraphs, blockquotes, lists, code, tables, and image positions.
- Run the WeChat formatting checklist in `references/wechat-formatting.md`.

### Normal Website URLs

Prefer browser extraction if available. Otherwise fetch HTML and extract the main article from `article`, `main`, or the largest content-like block. Preserve heading, paragraph, list, quote, image, code, and table structure where possible.

### Direct Text

Use the provided text as the original body. Add paragraph breaks only when the text is clearly collapsed into one long line.

### Screenshot / Chat Record Images

When the user sends a screenshot of chat records, training sessions, or article images and asks to archive the text content:

1. If the current model provider supports vision, use `vision_analyze` on the image directly.
2. If vision fails (e.g. DeepSeek returns `unknown variant image_url, expected text`), fall back to OCR. See `references/ocr-fallback.md` for the full tesseract workflow — install, split, OCR with `chi_sim+eng`, and cleanup.
3. After extracting text, reconstruct the message flow: group by sender, remove OCR noise, add paragraph breaks.
4. If the content is a course/training share, use the training-summary template (add `source: 群聊截图` and `## 原文（课程分享记录）` section instead of `## 原文`). Classify by content topic (HR/AI/卡兹克) as normal.
5. Upload to the appropriate vault folder via WebDAV as usual. Create the target directory with `MKCOL` if it doesn't exist (WebDAV PUT to a non-existent directory returns 409).

### Feishu Documents

When the user provides a Feishu document URL (feishu.cn/wiki/... or feishu.cn/docx/...) and asks to save it to Obsidian:

1. **Identify the account**: Determine whether the document is on the user's personal or work Feishu account. Use `lark-cli profile use <name>` to switch profiles.
2. **Resolve the document**: If it's a wiki URL (`/wiki/<token>`), use `lark-cli wiki spaces get_node --as user --params '{"token":"<wiki_token>"}'` to get `obj_type` and `obj_token`. If it's a direct docx URL, extract the `docx` token directly.
3. **Authenticate**: If the user identity token is expired, use the split-flow auth login pattern (`lark-cli auth login --scope "wiki:node:read" --no-wait --json` → QR code → user scans → `lark-cli auth login --device-code <code>`).
4. **Fetch as Markdown**: `lark-cli docs +fetch --as user --api-version v2 --doc "<obj_token>" --doc-format markdown`
5. **Save to Obsidian**: Classify the document (see Classify Destination below). Internal company docs go to `01工作区/<project>/`. Skip the article template (no 摘要/核心要点/快速判断) — these are raw work documents — but do add YAML frontmatter with title, source, date, url, and relevant tags.
6. **Verify**: Confirm the file was written correctly with the full content preserved.

If the user provides a batch file, read article title and URL columns, extract each article independently, then update entry pages after all article files are ready. Do not add duplicate links if the same title or path already exists.

Batch mode must not lower note quality. For every article, read enough of the full body to understand the thesis, evidence, examples, middle sections, and conclusion before writing `## 摘要` and `## 核心要点`. Never generate summaries by copying the opening paragraphs or using a generic template such as `文章围绕“标题”展开`. If there is not enough time to write real summaries for the full batch, archive fewer articles and continue later rather than writing low-quality notes.

## Classify Destination

Classify by **WeChat public account** (the `nickname` JS variable), not just by topic. See `references/classification-by-account.md` for the account-to-folder mapping and decision tree.

| Destination | Use When | Path |
| --- | --- | --- |
| HR | HR, OD, talent, compensation, performance, recruiting, HRBP, SSC, workforce effectiveness | `00知识库/HR知识/` |
| AI | AI tools, AI workflows, prompt, agent, AI products, AI applications, AI-era personal development | `00知识库/AI知识/` |
| 商业知识 | business strategy, business models, growth, marketing, product strategy, operations, finance, capital markets, company cases, entrepreneurship, industry analysis | `00知识库/商业知识/` |
| 卡兹克 | Author is 卡兹克 / 数字生命卡兹克, or the article belongs to that author collection | `00知识库/卡兹克/` |
| 工作文档 | Internal company documents: meeting notes, project docs, BP reviews, HR operational docs | `01工作区/<project>/` |

Priority: if an article is both 卡兹克 and AI, classify it under 卡兹克 first. Then choose the most relevant 卡兹克 subfolder. If an article is both AI and HR, classify by the main reader problem: AI tool/workflow/product learning goes to AI; HR organization/talent/workforce problems go to HR. If an article is both business and HR or AI, classify by the dominant topic, not by incidental examples.

For internal company documents (工作文档), place them under `01工作区/<project>/` using the project name as folder — e.g. `01工作区/全棉时代/`, `01工作区/固生堂/`. These are raw work documents: skip the article template (no 摘要/核心要点/快速判断 sections), but always include YAML frontmatter with title, source, date, url, and relevant tags. Preserve the full original body.

### Entry-Page Subcategories

For HR entry page:
- HR资讯
- HR的AI应用
- hrBP相关
- 组织发展
- 人才发展
- 薪酬绩效
- 招聘
- SSC

For AI entry page:
- AI工具: specific tools, platforms, plugins, setup guides
- AI使用提效: prompts, workflows, usage methods, cost or token control
- AI应用: field, organization, product, or work-scenario implementation cases
- AI个人发展: personal capability, career, skill tree, product thinking, long-term self-development

For 商业知识 entry page:
- 商业模式: value proposition, monetization, unit economics, platform/ecosystem logic, flywheels
- 战略管理: competitive strategy, positioning, moat, strategic choices, resource allocation
- 产品与增长: product strategy, user growth, retention, pricing, channels, product-led growth
- 市场营销: brand, consumer insight, campaigns, sales, go-to-market, category creation
- 经营管理: operating system, process, supply chain, organization execution, management mechanisms
- 财务与资本: financial analysis, fundraising, valuation, M&A, capital markets, investor narratives
- 行业案例: company cases, industry reports, sector comparison, market structure, benchmark studies
- 创业与创新: founder thinking, startup methods, zero-to-one, innovation management, new venture lessons

For 卡兹克 entry page:
- AI资讯
- claude code
- codex
- prompt
- skills
- workbuddy

If an entry page is missing or empty, create a simple category structure matching the HR/AI entry-page style: title, short organizing principle, `## 分类说明`, `## 主题分类`, subcategory headings, and `## 全部文章索引`.

## File Naming

Use the article title as the base filename, but sanitize unsafe characters before writing:

- Remove or replace `/`, `\`, `?`, `*`, `:`, `|`, `<`, `>`, control characters, and Chinese curly quotes if the environment rejects them.
- Prefer a stable, readable filename made from Chinese characters, letters, numbers, spaces, and common punctuation: `.`, `-`, `_`, `，`, `。`.
- Keep the YAML `title` as the original title even if the filename is sanitized.
- Full-width Chinese punctuation (`：` `？` `（）` `，` `。`) is safe in filenames and survives WebDAV PUT fine — the vault already stores files like `麦肯锡：AI时代，三支柱之后，HR往哪走？.md`. Only ASCII specials (`:` `/` `?` `*` etc.) actually need sanitizing; don't over-strip full-width chars.

## Article Template

Every archived article must use this structure:

```markdown
---
title: {original title}
author: {author or empty}
source: {微信公众号 / website / text}
date: {YYYY-MM-DD or empty}
url: {original URL or empty}
tags:
  - article
  - wechat
---

# {original title}

## 摘要

{150-250 Chinese characters. State the core claim, why it matters, how the author argues, and what the reader can take away.}

## 核心要点

- {point 1: claim + evidence/example}
- {point 2: claim + evidence/example}
- {point 3: claim + evidence/example}

## 这篇解决什么问题

{One sentence describing the decision, action, or understanding problem this article helps with.}

## 快速判断

- **适合人群**：{who should read it}
- **适合场景**：{when it is most useful}
- **不适合场景**：{when it is not worth reading}

---

## 原文

{complete original body in Markdown, preserving structure and order}

---

> 来源：{author/source}
> 原文链接：{url}
```

For better summaries, read `references/summary-guidelines.md`.

Hard rule: the note sections must be a real synthesis of the full article. Do not use the first paragraphs as a substitute for summary, and do not make all articles share the same summary sentence pattern.

## Entry Page Update

1. Read the full entry page via WebDAV GET (not local FUSE path). After any prior WebDAV PUT in the same session, the local FUSE cache at `/mnt/obsidian/` may be stale and return outdated content.
2. Add one wikilink to the selected subcategory section.
3. Add one wikilink to the all-articles index section if that section exists.
4. Keep existing order if the page already has one. Otherwise append to the relevant list.
5. Check for existing same-title or same-path links before adding.
6. ⚠️ **Avoid `replace()` link duplication**: The marker string used for insertion (e.g. the last wikilink in a section) often appears in BOTH the subcategory section AND the `## 全部文章索引` section. Using `str.replace(old, new)` without `count=1` replaces ALL occurrences, creating duplicate links. Always use `replace(old, new, 1)` or split at the `## 全部文章索引` header to edit each section independently.
7. 🔍 **Verify the replacement actually landed**: After building `old_string`, use `repr()` to inspect the exact whitespace between entries before constructing the replacement — entry pages can have 1, 2, or 3 blank lines between sections, and a whitespace mismatch causes `replace()` to silently do nothing. After uploading, re-read via WebDAV GET and count the occurrences of the new link: it should appear exactly twice (once in the subcategory section, once in `## 全部文章索引`). If the count is 0 or 4+, the replacement missed and created duplicates — fix immediately. ⚠️ Count the **full wikilink** `[[path|display]]` (or the link line `- [[...]]`), NOT the bare title string: the title text appears in BOTH the path and display halves, so counting the bare title returns 4 for a correct result (2 links × 2 halves). Counting the full `[[path|display]]` substring returns exactly 2.

Wikilink format:

```markdown
- [[relative/path/filename|display title]]
```

Use the path relative to the vault when the file is in a nested folder or when duplicate titles may exist. Omit `.md`.

Entry-page path conventions differ per page — copy the existing style from the target entry page rather than guessing: AI知识入口 uses `[[AI知识/...]]` (no `00知识库/` prefix); 卡兹克入口 uses `[[00知识库/卡兹克/...]]`; HR知识入口 mixes `[[HR知识/...]]` and `[[00知识库/HR知识/...]]`. Match the dominant style of the section you're inserting into (recent entries usually reflect the current convention).

## WebDAV Writing

`/mnt/obsidian/` is a Jianguoyun WebDAV FUSE mount. Writes through the mount may appear successful but fail to persist. Upload files with WebDAV PUT, then verify with WebDAV GET.

Do not hardcode credentials in this skill. Read credentials from `/etc/davfs2/secrets` or environment variables provided by the deployment. Note: the secrets file is typically root-only (`chmod 600`), so `read_file` and plain `cat` will fail with Permission denied — use `sudo cat /etc/davfs2/secrets`.

Required write flow:

1. Convert `/mnt/obsidian/{relative path}` to WebDAV URL path under `https://dav.jianguoyun.com/dav/obsidian/`.
2. URL-encode each path segment.
3. Upload with `curl -T`.
4. Treat HTTP `201` and `204` as success.
5. Read the same URL back and verify the expected title/frontmatter exists.
6. After a WebDAV PUT, the local FUSE cache at `/mnt/obsidian/` is stale — it does not reflect the new content. Any subsequent reads of vault files in the same session must also use WebDAV GET, not the local path.

## Final Quality Checklist

Before writing the final file:

- Frontmatter starts and ends with `---`.
- `## 摘要`, `## 核心要点`, `## 快速判断`, and `## 原文` are present.
- 摘要 is 150–250 Chinese chars — measure with `len()` on the 摘要 text programmatically, not by eye; overshooting (300+) is the common failure and requires trimming before upload.
- The original body is complete and not summarized away.
- WeChat articles pass `references/wechat-formatting.md`.
- No standalone `!`, empty image links, or empty list items remain.
- Code blocks have balanced triple backticks.
- Paragraph repair did not modify code blocks, tables, lists, or blockquotes.
- Entry-page links are not duplicated.
- WebDAV GET confirms the uploaded content.

## Pitfalls

### Extraction script returns empty on direct URL fetch

`python3 references/extraction-script.py --json "<url>"` sometimes returns all-empty fields even when the article exists and has valid HTML. The built-in `fetch_url()` uses a fixed UA/timeout that may not work for all cases.

**Workaround**: Pre-fetch the HTML with curl first, then pipe to the script:

```bash
curl -s -L -A "Mozilla/5.0 ..." "<url>" -o /tmp/article.html
cat /tmp/article.html | python3 references/extraction-script.py --json --url "<url>"
```

Always verify that `body_length > 0` after extraction. If zero, retry with the pipe approach.

### Extraction script `--json` output key names

`--json` output keys are `body_markdown` and `body_length` — NOT `body`. Reading `data.get('body')` returns empty and can make a successful extraction look like a failure. Always check `data['body_length']` (or `data['body_markdown']`) instead.

Note: when reading `--json` output, the body field is keyed `body_markdown` (not `body`). Reading `data.get('body')` returns None/0 and falsely looks like a failed extraction — always check `body_markdown` for content and `body_length` for the size.

### Slide-based / image-heavy WeChat articles

Some WeChat articles are published as slide decks — the body is almost entirely `<img>` tags with minimal text (slide titles/bullets). The extraction script will produce a stream of `![image](url)` lines with sparse text between them.

**How to handle**:
1. Extract all available text framework (headings, bullet points) from between images.
2. Preserve all image links in the `## 原文` section so the visual content is not lost.
3. Note in the body: `> **注**：本文原为幻灯片形式发布，正文内容嵌入在图片中。以下为从页面中提取的文字框架。`
4. Write summaries from the text framework — don't fabricate detail not present in the extracted text.
5. Still run the full quality checklist; the template sections remain mandatory.

### Republished WeChat article (same title, new sn URL) — update in place, don't duplicate

Accounts like 高绩效HR repost the same PPT deck under a new `mp.weixin.qq.com/s/<sn>` URL while keeping identical `mmbiz.qpic.cn` image URLs. The user may send the new link weeks later.

**Before archiving, check the vault for an existing file with the same title** (PROPFIND the target folder):

```bash
curl -s -u 'USER:PASS' -X PROPFIND "https://dav.jianguoyun.com/dav/obsidian/00知识库/HR知识/" -H "Depth: 1" \
  | grep -oP '(?<=<d:href>)[^<]+' | grep -E '标题关键词'
```

If the file already exists: **update it in place** —
1. Refresh `url` (and `date`) in the frontmatter + footer to the new repost link.
2. Enrich the body if the old archive was thin (e.g. image-only, no text framework) — see `references/slide-articles.md` OCR workflow.
3. Do NOT create a second file, and do NOT add entry-page wikilinks: the title is almost certainly already linked (possibly inside `<mark class="conflict">` blocks from a merge). Verify before touching the entry page; leave conflict markers alone.

Use a `curl -T /tmp/file` PUT to overwrite the existing WebDAV path (same filename), then verify with GET — the file count in the folder must not increase.

### FUSE mount write permissions

The `/mnt/obsidian/` davfs mount may be owned by `root:root` with no write permission for the agent user. When `cp` or the `patch` tool fails with `Permission denied`:

1. For writing article files: `sudo cp /tmp/article.md "/mnt/obsidian/00知识库/.../article.md"`
2. For editing entry pages: use `sudo sed -i` with careful patterns, or write the updated entry page to `/tmp/` first and `sudo cp` it into place.
3. After a sudo write, the local read of `/mnt/obsidian/` usually reflects the content (the stale-cache concern from direct WebDAV PUT does not apply to FUSE writes).

### Entry page update via patch tool fails on root-owned files

The Hermes `patch` tool manipulates files through bash, which inherits the agent's user permissions. When the entry page is root-owned on the davfs mount, `patch` will fail with `Permission denied`. Fall back to `sudo sed` for single-line insertions, or write a temp file and `sudo cp` for multi-line edits.

### Never use `curl -T /dev/stdin` inside `execute_code`

`execute_code`'s `terminal()` function sends the command string as-is to a shell — there is no stdin pipe from Python. Calling `curl -T /dev/stdin` inside `execute_code` uploads **zero bytes**, silently wiping the remote file. This has destroyed the entry page before.

**Rule**: Always write content to a temp file first, then upload with `curl -T /tmp/file`. Never attempt `-T /dev/stdin` from execute_code.

```python
# ✅ Correct
with open('/tmp/entry_updated.md', 'w') as f:
    f.write(content)
terminal(f"curl -s -w '%{{http_code}}' -u '{USER}:{PASS}' -T /tmp/entry_updated.md '{url}'")

# ❌ Wrong — wipes the remote file
terminal(f"echo '{content}' | curl -s -T /dev/stdin -u '{USER}:{PASS}' '{url}'")
```

### Entry page update: split-at-index strategy (preferred)

Always split the entry page content at `## 全部文章索引` and edit each section independently. This avoids the problem of marker strings (like article titles) appearing in multiple sections:

```python
idx_all = content.find('## 全部文章索引')
section1 = content[:idx_all]   # Contains AI使用提效 / AI应用 / etc.
section2 = content[idx_all:]   # The all-articles index

# Insert in section1 after the last link in the target subcategory
# Insert in section2 after the last link in the index
result = section1 + section2
```

This is more reliable than `str.replace(old, new, 1)` because it guarantees each insertion goes into the correct section regardless of where else the marker string appears.

### Entry page corruption from `read_file` output format

The `read_file` tool returns content with `LINE_NUM|CONTENT` prefixes (e.g. `1|# AI知识入口`). If you accidentally pipe this output into a file write, the entry page becomes corrupted with line-number prefixes on every line.

**Detection**: After downloading the entry page via WebDAV GET, check if lines start with `\d+\|`:
```bash
grep -c '^[0-9]*|' entry.md
```

**Fix**: Strip line-number prefixes before any edit:
```python
import re
lines = content.split('\n')
clean = [re.sub(r'^\d+\|', '', line) for line in lines]
content = '\n'.join(clean)
```

**Prevention**: Never use `read_file()` output as the data source for entry page edits. Always use WebDAV GET (curl) or the raw local `cat` output instead. The `read_file` tool is for inspection only.

### `str.replace()` matches wrong occurrence when path and display text are the same

When a wikilink has the same text in its path part (before `|`) and display part (after `|`), e.g. `[[00知识库/卡兹克/codex/全网最详细的Codex入门教程，手把手教你玩转Vibe Coding。|全网最详细的Codex入门教程，手把手教你玩转Vibe Coding。]]`, a `str.replace(old, new, 1)` where `old` starts with the title text will match the **second occurrence** (the display text after `|`), not the end of the line. This consumes the `]]` and corrupts the wikilink into a merged mess.

**Prevention — use positional insertion, never string replacement on wikilink lines**:
```python
# ✅ Correct: find section boundaries by position
codex_start = content.find('### codex')
next_hdr = content.find('\n### ', codex_start + 10)
codex_block = content[codex_start:next_hdr]
lines = codex_block.split('\n')
# Find the last wikilink line index in the array
last_idx = max(i for i, line in enumerate(lines) if line.startswith('- [['))
# Insert the new line after the last wikilink
new_block = '\n'.join(lines[:last_idx+1]) + '\n' + NEW_LINK + '\n' + '\n'.join(lines[last_idx+1:])

# ❌ Wrong — replace() on wikilink content can match the display text
content.replace('全网最详细的Codex入门教程]]\n\n### prompt', ...)  # matches display text!
```

**Rule of thumb**: if you're touching an entry page, use `find()` to locate section starts/ends, `split('\n')` to get lines, and insert by array index. Never construct a `replace(old, new)` where `old` contains text that appears in both the path and display portion of a wikilink.

### `rfind` + `find("\\\\\\\\n")` trailing-newline trap

When inserting a wikilink at the end of a section (after the last entry), using `content.rfind(...)` then `content.find("\\n", last_pos)` is fragile. If the file has no trailing newline after the last line, `find("\\n")` returns `-1`, and `content[:0]` + `content[0:]` inserts the link at the **beginning** of the file.

**Prevention**: Always check `end_of_line == -1` and handle by appending:

```python
end_of_line = content.find("\n", last_pos)
if end_of_line == -1:
    content = content + "\n" + new_link + "\n"
else:
    content = content[:end_of_line+1] + new_link + "\n" + content[end_of_line+1:]
```

### Whitespace sensitivity in entry page `replace()` operations

When constructing `old_string` for a `str.replace(old, new, 1)` on the entry page, the exact number of blank lines between the last wikilink in a section and the next `###` header matters. Entry pages can have 1, 2, or 3 blank lines in these gaps, and they can change across sessions. A whitespace mismatch causes `replace()` to silently do nothing — the count stays at 1, and `count=1` prevents a duplicate from the other section, so you get no insertion at all.

**Prevention**: Before building `old_string`, use `repr(content[section_end-100:section_end+100])` to inspect exact whitespace around the insertion point. After uploading, always verify: re-read via WebDAV GET and count occurrences of the new link — it must be exactly 2 (one per section).

### Chinese curly quotes in marker strings

When constructing `old_string` from article titles that contain Chinese curly quotes (`""`, Unicode U+201C/U+201D), never type them manually in Python source — what you see in a shell or read_file output may look like straight `""` (U+0022) but is actually `""` in the file. A manual `""` matches nothing and `replace()` silently does nothing.

**Rule**: always extract marker substrings directly from the fetched content, never construct them by hand. Use `content.find('keyword')` to locate the anchor, then slice the surrounding region:

```python
idx = content.find('震惊！字节跳动裁掉')  # partial keyword after the target
marker = content[idx:content.find('\n\n### 薪酬绩效', idx)]
old1 = marker + '\n\n### 薪酬绩效'
```

This guarantees the exact bytes match, regardless of quote encoding, invisible characters, or variant punctuation.

### Entry page with merge conflict artifacts (`<mark class="conflict ours/theirs">`)

Obsidian Sync or git merge operations can leave literal `<mark class="conflict ours">` and `<mark class="conflict theirs">` markers in the entry page file. These are NOT HTML — they are raw text in the markdown file, creating two competing sets of wikilinks (one in the "ours" block, one in the "theirs" block). This causes several problems:

1. **Duplicate content**: The same section may appear twice with different link sets. A `### AI资讯` header followed by one set of links, then `<mark class="conflict ours">...</mark><mark class="conflict theirs">...`, then another set of links.
2. **Misleading occurrence counts**: When you count wikilink occurrences during verification, the count may be 4 (2 conflict versions × 2 sections) instead of the expected 2. After WebDAV PUT, if your edit collapsed one version, the count drops to 2 — which is correct, but the intermediate count during construction misleads.
3. **Partial resolution**: Using the `find()` + `split('\\n')` + positional insertion approach (split-at-index) works correctly with conflict markers because it inserts after the *last* wikilink in the array, regardless of which conflict version's last link it finds. But using `section1.replace(ai_block, new_ai_block)` may inadvertently collapse one conflict version while preserving the other, silently "resolving" the conflict for that section while leaving it active elsewhere.

**Best practice**:
- Always use WebDAV GET to read the entry page and inspect its content for conflict markers before editing. Run `grep -c 'conflict' /tmp/entry.md` to detect them.
- Prefer the positional insertion approach (find section → split lines → find last wikilink index → insert) over `replace()` on section blocks. Positional insertion works the same way regardless of conflict markers.
- ⚠️ **In the all-articles index, insert BEFORE the conflict zone**: when `## 全部文章索引` ends with `<mark class="conflict ...">` blocks, the *last* wikilink in the array is usually inside the "theirs" block. Inserting after it puts the new link inside the conflict — it would be dropped if the conflict later resolves to "ours". Instead, walk the lines, track the last wikilink, and **break on the first `<mark class="conflict"` line** so the new link lands after the last clean wikilink, outside all conflict blocks:
```python
last_clean = -1
for i, line in enumerate(s2_lines):
    if line.startswith('- [['):
        last_clean = i
    elif '<mark class="conflict' in line and last_clean != -1:
        break
assert last_clean != -1
s2_new = '\n'.join(s2_lines[:last_clean+1]) + '\n' + NEW_LINK + '\n' + '\n'.join(s2_lines[last_clean+1:])
```
- 🔍 **Check whether the conflict zone is at the END of the section first**: the break-on-conflict rule above is only correct when the conflict block is the last thing in the index section. If clean wikilinks exist AFTER the conflict block (conflict is mid-file — check the file tail: it ends with a `- [[...]]` wikilink line, not `</mark>`), breaking at the first conflict marker inserts the new link mid-index: still exactly 2 occurrences and outside conflicts, but out of the append-at-end order. In that case insert after the ABSOLUTE last wikilink of the section (append at end) instead of breaking at the conflict. Example: AI知识入口 has a mid-file conflict in both AI应用 and 全部文章索引 with clean links after it — append at end there; 卡兹克入口's 全部文章索引 ENDS with a conflict block — break before it there.
- ♻️ **Fixing a misplaced mid-index insertion**: if a link already landed before a mid-file conflict zone, remove the index occurrence and re-append at end: split content at `## 全部文章索引`, remove the first occurrence of the link line in section2 (`section2.replace(LINK_LINE + '\n', '', 1)` — safe: the subcategory occurrence lives in section1), then append at the very end (`section2.rstrip('\n') + '\n' + LINK_LINE + '\n'`). Re-upload and verify: full-link count stays 2, conflict count unchanged.

Verify after upload that conflict marker count is unchanged (`grep -c 'conflict'` before and after) and the full wikilink appears exactly 2×.

**Mid-file conflict zones (break-on-conflict is wrong there)**: the `break` on the first `<mark class="conflict"` line is only correct when the conflict block sits at the END of the index. If clean wikilinks FOLLOW the conflict zone (conflict is mid-file and the file continues with more links), the loop above stops at the first conflict and inserts the new link in the MIDDLE of the list. In that case take the ABSOLUTE last wikilink of the whole section — it is clean — and append after it:

```python
last_idx = max(i for i, line in enumerate(s2_lines) if line.startswith('- [['))
s2_new = '\n'.join(s2_lines[:last_idx+1]) + '\n' + NEW_LINK + '\n' + '\n'.join(s2_lines[last_idx+1:])
```

This bit `AI知识入口` (2026-08): the conflict zone sat mid-index with 3 clean links after it; break-on-conflict placed the new link before the conflict instead of at the file end. Repositioning = remove the misplaced line from the index section only, `section2.rstrip('\n') + '\n' + NEW_LINK + '\n'`, re-upload, re-verify (count must stay 2).
- For verification, the final uploaded file should have the new link exactly 2 times (once in subcategory, once in all-articles index). If it's 4+, the edit hit both conflict versions — verify the file isn't corrupted.
- Do NOT attempt to clean up conflict markers during routine archiving — that's a separate maintenance task. Positional insertion coexists with them safely.

## Knowledge Card Path (Alternative Output — Explicit Opt-In Only)

Knowledge cards (`00知识库/00知识卡片/`) are an **explicit opt-in** format. Only use them when the user directly says "知识卡片" or asks for a condensed structured summary. For all "转存" / "保存" / "归档" requests, use the full-article archive format by default.

### Decision rules

| When | What to do |
| --- | --- |
| User says "转存" / "保存" / "归档" a WeChat article | **Full-article archive** with `## 原文` — always |
| User says "做张知识卡片" / "知识卡片格式" / mentions card_tag explicitly | **Knowledge card** — structured summary without `## 原文` |
| Uncertain which the user wants | Default to **full-article archive**. It's safer to have too much content than too little; a full archive can be condensed later, but a knowledge card discards the original body. |
| Author is 卡兹克 | Full-article archive in `卡兹克/<subfolder>/`. (卡兹克's tutorials are archived like any other article — the user prefers full-body preservation.) |

### Knowledge card format

See `references/knowledge-card-format.md` for the template, frontmatter, and card-numbering rules. Only use when explicitly requested.

### Card numbering

Cards are numbered **by `card_tag` sequence**, not globally. Check the existing cards in `00知识库/00知识卡片/` to find the next number for the target tag.

Existing tags in use: `AI`, `GROWTH`, `STRATEGY`.

## References

- `references/wechat-extraction.md`: Fetching WeChat article HTML, metadata extraction, and script usage.
- `references/wechat-formatting.md`: WeChat HTML-to-Markdown formatting rules and post-extraction checks.
- `references/summary-guidelines.md`: Summary and note-writing rules.
- `references/knowledge-card-format.md`: Knowledge card template, frontmatter, and numbering rules.
- `references/extraction-script.py`: Standalone WeChat extraction script.
- `references/ocr-fallback.md`: Tesseract OCR workflow for screenshots when the vision API is unavailable.
- `references/slide-articles.md`: Detailed guidance for slide-based / image-heavy WeChat articles.
- `references/classification-by-account.md`: Account-to-folder mapping for WeChat article classification.
