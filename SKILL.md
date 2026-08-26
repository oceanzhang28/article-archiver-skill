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

Priority: if an article is both 卡兹克 and AI, classify it under 卡兹克 first. Then choose the most relevant 卡兹克 subfolder. **But 卡兹克 personal-reflection / essay articles (心得分享类, numbered lists of reflections/lessons like 9条心得 / 6点特质 / 7点心得, AND 人物故事/采访随笔 like the 2026-08-24 两位高中生炼丹社 piece) go to the 卡兹克 ROOT directory — NOT a subfolder and NOT into the entry page** (verified 2026-08-20 on 《创业2年半后，想跟你分享关于AI组织的这7点心得。》; 2026-08-24 on 《两个16岁的高中生，共享了自己的显卡和API，想让全校同学都免费用上AI。》). Precedents all living at `00知识库/卡兹克/` root with NO wikilink in 卡兹克入口: 《用AI的这三年，想跟你分享这9条心得。》(2026-02), 《AI时代的人才，我觉得最重要的是这6点特质。》(2026-05), 《上周做了场内部分享，关于我做AI这三年来总结的内容创作方法论。》. 卡兹克入口 only indexes the 6 subfolder sections (and currently has no 全部文章索引) — root-level articles have no home there, so skip the entry-page update entirely. Distinguish from tool-specific tutorials (claude code/codex/prompt/skills/workbuddy subfolders) and from news/product-opinion pieces (AI资讯). If an article is both AI and HR, classify by the main reader problem: AI tool/workflow/product learning goes to AI; HR organization/talent/workforce problems go to HR. If an article is both business and HR or AI, classify by the dominant topic, not by incidental examples.

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
- ⚠️ **The ASCII pipe `|` is rejected by Jianguoyun WebDAV with HTTP 400 `IllegalArgument` / `the nustore path is not valid` — even when percent-encoded as `%7C`.** Percent-encoding does NOT help; the server decodes and re-validates. Replace ` | ` with ` - ` (or another safe char) in the FILENAME only, keep the original title (with `|`) in the YAML `title` and the H1. Real case: `森马…方法论 | AI新组织观察` → filename `森马…方法论 - AI新组织观察.md`. When a PUT returns 400, check the error body (`<s:exception>IllegalArgument</s:exception>`) — it names the offending path — then sanitize and retry. ✅ **Full-width `｜` (U+FF5C) is a DIFFERENT character and is SAFE** — verified 2026-08-26: `每个销售都有一份不同周报，活动报名翻倍｜Anthropic营销团队AI实践.md` PUT with HTTP 201 (encoded `%EF%BD%9C`), and the same fullwidth bar is already used in existing entry-page wikilinks (e.g. `咨询行业实战指南｜用好 TraeWork…`). Only ASCII `|` (U+007C) triggers the 400; don't over-sanitize fullwidth bars.

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

For slide-deck articles (70页PPT), the trailing ad slides (出海课程/线上课程/内训主题) are kept as images but flagged:

```markdown
> **注**：以下为文末课程推广页（出海人力资源管理GLOBAL模型实战强化班、线上课程系列、高绩效HR精品内训主题），非课件正文。
```

⚠️ **Distinguish course-ad slides from duplicated header promos**: when the tail block merely REPEATS the header promo (same 回复"XX"领PDF CTA + 长按识别二维码 + 报名咨询 lines, as in the AI领导力手册 90页PPT piece, 2026-08), it is NOT course content — drop it entirely and keep only the body slides, since the info is already preserved in the archived frontmatter. Rule of thumb: keep+flag = new course offerings; drop = verbatim repeat of header promo text/QR.

Use the path relative to the vault when the file is in a nested folder or when duplicate titles may exist. Omit `.md`.

Entry-page path conventions differ per page — copy the existing style from the target entry page rather than guessing: AI知识入口 uses `[[AI知识/...]]` (no `00知识库/` prefix); 卡兹克入口 has FLIPPED between `[[卡兹克/<subfolder>/...]]` (no prefix) and `[[00知识库/卡兹克/<subfolder>/...]]` (with prefix) — as of 2026-08-11 the live page uses `00知识库/`-prefixed links throughout (e.g. `- [[00知识库/卡兹克/AI资讯/...|...]]`); HR知识入口 mixes `[[HR知识/...]]` and `[[00知识库/HR知识/...]]`; 商业知识入口 uses `[[商业知识/...]]` (no `00知识库/` prefix — e.g. `- [[商业知识/谈业务，要有逻辑、有结构|谈业务，要有逻辑、有结构]]`). Match the dominant style of the section you're inserting into (recent entries usually reflect the current convention).

**卡兹克入口's structure has FLIPPED between versions — always read the live file first.** Earlier sessions recorded "no `## 全部文章索引`" (insert 1 link, verify count == 1), but a later session (2026-08-11) found the page WITH `## 全部文章索引` again — the two-link rule (count == 2) applies whenever that section exists. Before deciding 1-link vs 2-link, run `grep -n '^## \|^### '` on the WebDAV-fetched entry. When the page has the index section, insert one link in the matching subcategory section AND one in `## 全部文章索引`, then verify the full wikilink appears exactly 2×.

⚠️ **Both HR知识入口 and 卡兹克入口 carry TWO full copies of the page structure (legacy duplication — two `## 分类说明`, two `## 主题分类`, two `## 全部文章索引` blocks). Verified 2026-08-18 on both.** The established convention is to update ONLY the FIRST copy: insert once in the first copy's subcategory section + once in the first copy's index block, then verify full-wikilink count == 2. The second copy is stale/abandoned — inserting there too pushes the count to 4. HR知识入口's first index header is literally `暂## 全部文章索引` (locate with substring `全部文章索引` or `暂##`); 卡兹克入口's first index header is a normal `## 全部文章索引`. Both pages' first copies use `00知识库/`-prefixed links (卡兹克) or `HR知识/`-prefixed (HR, recent entries) — match the live section style. 🔍 **Verification pitfall (fired 2026-08-20 on the 战略工具库 piece): to find the SECOND copy's H1 for first-copy-only counting, use `content.find('# HR知识入口', 1000)` — a bare `find('# HR知识入口')` returns position 0 (the file's own first H1), so `content[:second_h1].count(link)` yields 0 and makes a correct first-copy insertion look like it landed in the second copy.** Always pass a start offset past position 0 when locating the duplicate structure's boundary marker.

**HR知识入口 per-section style (verified 2026-08)**: the subcategory sections (hrBP相关 / 组织发展 / 人才发展 / 薪酬绩效 / 招聘) use **no-prefix** wikilinks — `- [[业务、人、专业，HRBP到底要先懂哪个？|业务、人、专业，HRBP到底要先懂哪个？]]` — while `## 全部文章索引` uses `[[HR知识/标题|标题]]` (recent entries). So insert the same title twice with DIFFERENT prefixes: no-prefix in the subcategory block, `HR知识/`-prefixed in the index. ⚠️ **Exception — 人才发展 section mixes prefixes** (verified 2026-08-12): recent 人才发展 entries (平台公司关键岗位继任计划, AI重构任职资格管理, 出海组织观察日记（五）) use `HR知识/`-prefixed links alongside older no-prefix ones — insert with `HR知识/` prefix there to match recent convention. ⚠️ **Same for 组织发展** (verified 2026-08-16 on 物业公司定岗定编实操指南): recent 组织发展 entries (美的集团, 字节跳动全员信, 物业公司如何做好流程优化/定岗定编/算明白经济账, 首席组织官十大组织系统, AI时代组织观察·第二季) are all `HR知识/`-prefixed, while the first batch of older entries (组织诊断从哪里开始, 组织诊断的九宫格, 安克创新, 阿里离职贴…) stays no-prefix — insert with `HR知识/` prefix. Always eyeball the live section's last few links before choosing the prefix. ⚠️ **薪酬绩效 also uses `HR知识/` prefix for recent entries** (verified 2026-08-17 on the 销售激励 piece): the newest run (集团型企业的薪酬改革, 激励不只是分钱, 张一鸣人力成本, 销售激励) is all `HR知识/`-prefixed while older ones (一篇文章读懂"人效", 继续说说人效, 头部企业人均营收350万) stay no-prefix — insert with `HR知识/` prefix there too.

⚠️ **HR知识入口's index header is literally `暂## 全部文章索引`** (a leading `暂` glued to the `##` — verified 2026-08-13). `content.find('## 全部文章索引')` returns -1 and the split-at-index strategy silently fails. Locate the section with `content.find('全部文章索引')` (substring match) or the literal `暂## 全部文章索引`, then proceed with the normal positional insert/append logic.

⚠️ **HR知识入口 is a DUPLICATED full-page structure — update ONLY the first copy** (verified 2026-08-18 on the 周鸿祎 leadership piece). The file contains TWO complete entry pages back-to-back: two `## 分类说明` / `## 主题分类` blocks, two sets of subcategory sections (two `### 组织发展`, two `### 人才发展`, etc.), and two index sections (first is the `暂## 全部文章索引`, second is a clean `## 全部文章索引`). The second structure is a stale duplicate — do NOT insert links into it. How to confirm the convention before editing: count the last archived article's full wikilink `[[HR知识/<title>|<title>]]` in the file — it appears exactly 2×, BOTH in the first structure (subcategory + first index), 0× in the second. Bounding regions: locate the first `### 组织发展` for the subcategory insert; for the first index, locate `暂## 全部文章索引` (the 暂 prefix disambiguates to the FIRST copy — a bare `find('## 全部文章索引')` may hit the second copy) and bound its end with a second `# HR知识入口` (the duplicate structure begins with its own H1) or the second `## 分类说明`. Verify after upload that the full wikilink count is still exactly 2.

**Empty subcategory placeholder → replace, don't append**: entry pages often seed empty sections with a placeholder line like `暂无专门文章，后续有竞争战略、定位、护城河、战略取舍、资源配置相关内容时可放入这里。` (商业知识入口's 战略管理 was like this). When the target subcategory has NO wikilinks yet (only the placeholder), **replace the placeholder line with the new wikilink** instead of trying to find a "last wikilink" to insert after — there isn't one, and the placeholder must not survive alongside the article. Pattern:

```python
placeholder = '暂无专门文章，后续有竞争战略、定位、护城河、战略取舍、资源配置相关内容时可放入这里。'
assert content.count(placeholder) == 1, f"placeholder count: {content.count(placeholder)}"
content = content.replace(placeholder, LINK)
```

The rest of the flow is unchanged: still also insert into `## 全部文章索引` (if the page has one), still verify the full wikilink count (2× for pages with an index, 1× for 卡兹克入口 which has none).

### Verification gotcha: locating the SECOND H1 when counting first-copy vs second-copy placements

Duplicated entry pages (HR知识入口, AI知识入口, 卡兹克入口) need a before/after check: new link must appear exactly 2×, BOTH in the first structure, 0× in the second. To slice "first copy", you must find the SECOND `# 入口` H1 — **always call `content.find('# AI知识入口', 1000)` (or any offset > 0), never the bare `find()`**. The bare form matches position 0 (the first H1) and the "before" slice becomes empty → verification reports "0 in first copy / 2 in second copy" and makes a CORRECT insert look like it landed in the wrong copy (fired 2026-08-20 on AI知识入口). Same trap when slicing on the duplicate's `## 分类说明` / `## 全部文章索引` — anchor with a start offset past the first occurrence, or use the `暂##`-prefixed first-copy index header where present.

## WebDAV Writing

`/mnt/obsidian/` is a Jianguoyun WebDAV FUSE mount. Writes through the mount may appear successful but fail to persist. Upload files with WebDAV PUT, then verify with WebDAV GET.

Do not hardcode credentials in this skill. Read credentials from `/etc/davfs2/secrets` or environment variables provided by the deployment. Note: the secrets file is typically root-only (`chmod 600`), so `read_file` and plain `cat` will fail with Permission denied — use `sudo cat /etc/davfs2/secrets`. Each credential line is `<WebDAV base URL> <user> <password>` (e.g. `https://dav.jianguoyun.com/dav/ 373869036@qq.com ae2m9zu845d86g88`). After stripping `#` comments and blank lines, grep by the URL root (`dav.jianguoyun.com`) — the literal string `obsidian` does NOT appear in the line, so grepping for it silently returns nothing and looks like missing credentials.

Required write flow:

1. Convert `/mnt/obsidian/{relative path}` to WebDAV URL path under `https://dav.jianguoyun.com/dav/obsidian/`.
2. URL-encode each path segment.
3. Upload with `curl -T`.
4. Treat HTTP `201` and `204` as success.
5. Read the same URL back and verify the expected title/frontmatter exists.
6. After a WebDAV PUT, the local FUSE cache at `/mnt/obsidian/` is stale — it does not reflect the new content. Any subsequent reads of vault files in the same session must also use WebDAV GET, not the local path.
7. ⚠️ **GET byte size vs local char count — expect a big mismatch, don't false-alarm**: a Chinese-heavy article that is ~6.5K chars locally returns ~16K+ bytes from WebDAV GET because UTF-8 encodes each CJK char as 3 bytes (and image URLs are long). Comparing `wc -c` of the GET against Python `len()` of the local file shows ~2.5–3× inflation and can look like a corrupted or duplicated upload (real example 2026-08: 6547 chars → 16475 bytes — file was fine). Verify by structure — title/frontmatter present, `## 原文` exists, expected section markers — not by raw byte count.

## 高绩效HR (曼妮AI) Account Artifacts

Articles from `高绩效HR` (author 曼妮AI, e.g. the HRBP 成长顺序 piece) are article + heavy course-ad hybrids. Handle the two promo blocks:

### Header ad banner — drop

The top of the body is a promo banner: 超级会员年卡 + 扫码回复"福利"领资料 + 了解(link) + quoted image with 企业定制内训或公开课欢迎联系 + 梁老师 phone. Cut from the first banner image to the real opening line:

```python
banner_start = body.find('![image](https://mmbiz.qpic.cn/mmbiz_jpg/N5hX4ywNBk9EQkXYNOhvAesgzCXB8FJ9')
banner_end = body.find('想成为合格的业务伙伴')   # real article opening sentence
if banner_start != -1 and banner_end != -1:
    body = body[:banner_start] + body[banner_end:]
```

Anchor the end on the stable opening sentence, not on banner markup — the banner varies between posts.

### Tail training-course ad — compress, don't preserve

After the real ending (e.g. `欢迎在评论区聊聊你的看法。`), 高绩效HR appends a long course-ad: 《...实战训练营》+ 课程收益 + multi-unit 课程大纲 + 讲师简介 bio + 报名二维码 + 更多实战课程 images + `长按二维码或点击"阅读原文"报名`. This can be half the body. Cut at the ending marker and replace with one line:

```python
core_end = body.find('欢迎在评论区聊聊你的看法。')
if core_end != -1:
    core_end += len('欢迎在评论区聊聊你的看法。')
    body = body[:core_end] + '\n\n---\n\n> （文末为《业务为基：战略HRBP实战训练营》课程推广：9月4-5日上海，4680元/人，含课程收益、大纲与讲师简介，已省略）\n'
```

### Inline ### noise specific to this account

- `至关重要：### 先懂业务，再懂人，最后才是用专业解决问题\n\n。` → `：**先懂业务，再懂人，最后才是用专业解决问题**。` (inline ### → bold + merge the split `。`)
- `点击"### 阅读原文` → `点击"**阅读原文**`

Then run the standard checklist (no standalone punct, no inline `###` at line start, no standalone `!`, balanced backticks).

### 工具库-style articles (STRATEGY TOOLKIT / "30个工具" format, 2026-08-20)

高绩效HR publishes tool-library posts (e.g. 《战略工具库：30个可直接落地使用的战略管理工具》— a full toolkit with HTML template tables, ~42K chars). Distinct artifacts:

- **Header banner**: same 超级会员年卡/扫码领资料/企业定制内训/梁老师 phone block, PLUS an extra line `添加下方微信回复"XX"限时3天按指引分享获取本文内容` + QR — drop the whole block up to the real deck start (the banner ends at `长按识别二维码咨询报名`, real content begins at the `STRATEGY TOOLKIT` title line — anchor the cut on that, not on a body sentence).
- **Two-digit section headers with NO space**: `01战略分析工具` / `02战略制定工具` … `07工具库使用指南` extract as bare lines (no trailing space, no bold — distinct from the `01 ` trailing-space and `**01**` patterns). Generic regex: `re.sub(r'^(\d{2}[^\n]{2,30})$', r'### \1', body, flags=re.M)` — the `{2,30}` class catches ALL sections 01–07 in one pass (a `^(\d{2}战略...)` anchored variant only matches the 01–03 sections whose titles start with 战略).
- **`> ### 适用场景：` labels**: every tool has `> ### 适用场景：` → `> **适用场景**：` (blockquote inline-### → bold). Same pattern for `> ### 愿景：` / `> ### 预算：` etc. Generic: `re.sub(r'> ### ([^：\n]+)：', r'> **\1**：', body)`.
- **`_ | ### 人才：` rows** (strategy-house table rows): `re.sub(r'_\s*\|\s*###\s*([^：\n]+)：', r'_ \| **\1**：', body)`.
- **Table-cell ###**: standard `re.sub(r'(<t[dh]>)\s*###\s*([^<\n]+)', r'\1**\2**', body)` (fired on `<td>### 60-70%` etc.).
- **Inline ### in the 使用说明/最后提醒 blocks**: `收录### 30 个` → `收录**30 个**`; and the closing 最后提醒 block has `"闭环"：### 分析→…再分析\n\n，` and `结束，### 80%的时间…\n\n。` — the source uses **curly quotes** (`"` U+201C), so a hand-typed straight-quote `replace()` silently no-ops; use regex with `[”"]` class: `re.sub(r'闭环[”"]：###\s*分析→制定→解码→执行→复盘→再分析\n\n，', '闭环**分析→制定→解码→执行→复盘→再分析**，', body)` (also merges the split continuation punctuation).
- **Tail course ad**: ends with a full 训战课 promo (`> 工具在手，更需系统方法带教落地` → 《战略规划与解码落地班》9月18-19日上海 5980元 + 课程大纲 + 讲师简介 + 报名信息 table). Cut from `> 工具在手，更需系统方法带教落地` — this is a NEW course offering, not a header-promo repeat, so compress/drop per the tail-course rule.
- **Classification**: tool-library posts → `HR知识/组织发展` (matches the 组织发展 subcategory's "战略闭环和管理模型" description and the existing BLM article precedent).

高绩效HR also publishes tool-library collections (e.g. 《战略工具库：30个可直接落地使用的战略管理工具（附下载）》). These are strategy/management toolkits with blockquote-wrapped tool cards + HTML tables. Distinct artifacts and handling:

- **Classify to HR知识/组织发展** — the 组织发展 section description includes "战略闭环和管理模型", and the account already has 《解锁 BLM 业务领先模型：开启战略闭环与组织诊断新视野》 there. Strategy-toolkit content from 高绩效HR → 组织发展, NOT 商业知识 (account priority wins).
- **Header banner**: cut everything before the `STRATEGY TOOLKIT` marker line (the 超级会员年卡 + 扫码回复"福利" + 企业定制内训 + 梁老师电话 + 添加微信回复"战略工具"限时3天分享获取 block). `body = body[body.find('STRATEGY TOOLKIT'):]`.
- **Tail course ad**: cut at `> 工具在手，更需系统方法带教落地` (the 战略规划与解码落地班 promo: 9月18-19日上海 5980元, 刘善武讲师, 课程大纲 tables). Compress-or-drop; dropping is fine since it's a pure course ad.
- **Blockquote label `###` → bold**: every tool card emits `> ### 适用场景：` / `> ### 愿景：` / `> ### 预算：` etc. — convert with `body = re.sub(r'> ### ([^：\n]+)：', r'> **\1**：', body)`. This is the single biggest artifact (49 occurrences in the 30-tool piece).
- **`_ | ### 人才：` lines**: table-ish rows extract as `_ | ### 人才：` / `_ | ### 文化：` / `_ | ### 机制：` — convert with `body = re.sub(r'_\s*\|\s*###\s*([^：\n]+)：', r'_ \| **\1**：', body)` (the `_ |` prefix is preserved).
- **Bare section headers `01战略分析工具`** — section titles extract as bare `01战略分析工具` ... `07工具库使用指南` (two digits + title, NO space, NO bold, NO `###`): `body = re.sub(r'^(\d{2}[^\n]{2,30})$', r'### \1', body, flags=re.M)`. NOTE: a regex requiring `战略` in the title only matches 01-03; the bare-`\d{2}` form matches all 7.
- **Inline ### mid-prose with split continuation** (使用说明/最后提醒 blocks): `收录### 30 个` → `收录**30 个**`; `闭环"：### 分析→制定→解码→执行→复盘→再分析\n\n，` → `闭环**分析→制定→解码→执行→复盘→再分析**，` (curly quotes — use a `[”"]` regex class, plain replace fails). Same for `结束，### 80%的时间应该花在执行和复盘中\n\n。`.
- **`### 评分规则：`** → `**评分规则**：` (standalone label).
- Standard table-cell fix applies too: `re.sub(r'(<t[dh]>)\s*###\s*([^<\n]+)', r'\1**\2**', body)` for `<td>### 60-70%` cells.

Then run the standard checklist (no standalone punct, no inline `###` at line start, no standalone `!`, balanced backticks).

### DSTE / strategy-system prose articles (▍▎ format, 2026-08-25)

高绩效HR also publishes prose explainers of strategy systems (e.g. 《华为DSTE战略管理体系落地》— 四部曲闭环: 战略规划(4-9月)/战略解码(10-12月)/战略执行/战略复盘(次年1-3月), tools BLM + 两上两下预算 + BSC/组织绩效/PBC + 滚动预测 + 一报一会). Distinct artifacts:

- **`▍`/`▎` headers**: extraction emits `▍DSTE落地"四部曲"` as a bare line and `> ▎差距分析：战略的起点` / `> ▎"两上两下"预算流程` / `> ▎"一报一会"：华为内部高效管理工具` inside blockquotes. Convert with `re.sub(r'^▍(.+)$', r'### \1', body, flags=re.M)` and `re.sub(r'^> ▎(.+)$', r'#### \1', body, flags=re.M)`.
- **Cover block is content**: the body opens with a blockquote cover (`> DSTE · 四部曲闭环` … `> 战略管理是企业…四个核心环节。`) — KEEP it. Cut the header banner from the first promo image up to the cover marker (`body = body[body.find('> DSTE · 四部曲闭环'):]`), anchoring on the cover line, not a body sentence.
- **Bare numbered headers**: `01第一部曲：战略规划——看清方向，做正确的事` … `04第四部曲：…` → `###` via the same `^(\d{2}...)` rule as the 工具库 pieces (use `{2,40}` char range for the longer titles).
- **List-label split**: `- **一是愿景**\n\n即企业长远想要…` (bold label + blank line + content) → merge with `：`. ⚠️ Test the colon on the label AFTER stripping `**`: `label.strip('*').endswith('：')` — `'**问题一：**'.endswith('：')` is False (string ends in `**`) and silently adds a second colon.
- **Line-broken output list**: `战略规划阶段的输出成果包括：\n企业技术…\n市场洞察报告\n…` (no bullets) → prefix each content line with `- `.
- **Tail course ad**: cut from `★课程推荐：` (e.g. 《战略规划与解码落地班》9月18-19日上海 5980元) and compress to one flagged line per the tail-course rule.
- **Classification**: strategy-system content (DSTE/BLM/战略闭环) → HR知识/组织发展, same as the 战略工具库 precedent.

⚠️ **Inline-`###` regex must LOOP until stable (applies to ANY account with heavy inline ###)**: a single `re.sub(r'###\s+([^\n]+?)\s*\n\n([^\n]*)', ...)` pass leaves many artifacts behind because group2 `[^\n]*` greedily consumes the REST of the continuation line — including any later `### X` marker on the same line (e.g. `### 4月至9月\n\n推进，…未来### 3～5年\n\n的发展…` — the first match swallows `### 3～5年` as literal text). The swallowed markers sit at end-of-line, so a second pass fixes them; chains need 2-3 passes. Use:

```python
while True:
    new = re.sub(r'###\s+([^\n]+?)\s*\n\n([^\n]*)',
                 lambda m: f"**{m.group(1).strip()}**{m.group(2)}", body)
    if new == body:
        break
    body = new
```

Then verify no stray `###` lines remain except legit `### `/`#### ` headings. ⚠️ If you assert this with a regex, use `re.search(r'^#{3,6}\s+#{3,6}', ...)` — a `^#{1,6}\s*###` check backtracks (`#` + `###`) and flags every legit `#### X` sub-heading as a false positive (fired 2026-08-26 on the Anthropic 销售周报 piece).

## AI组织进化论 Account Artifacts

Articles from `AI组织进化论` (麦肯锡报告中文解读/整理, e.g. 智能体采用鸿沟 piece) repeat these extraction artifacts:

### Bare numbered headers `01 ` (trailing space) + plain subtitle lines

The numbered sections extract as `01 ` (bare digits + trailing space) followed by a plain-text subtitle line — NOT the `**01**` / `**###` pattern of 润米商城. Convert both to `###`:

```python
body = re.sub(r'^(\d{2})\s+$', r'### \1', body, flags=re.M)          # "01 " -> "### 01"
for sub in ['一道被多数企业做反的投资题', '员工不是不愿改变，而是同时失去了四种安全感']:  # subtitle lines
    if ('\n' + sub + '\n') in body:
        body = body.replace('\n' + sub + '\n', '\n### ' + sub + '\n')
```

### `> 结语` closing header → `### 结语`

The closing section extracts as a blockquote `> 结语` — it's a section header, convert to `### 结语`.

### Chinese-numeral chapter headers (一、~七、) + numbered sub-steps (第 N 步)

Not every AI组织进化论 post uses the `01 ` bare-number format — the Anthropic 销售周报 piece (2026-08-26) uses 中文数字章节 (`一、第一步没有写代码，他先写了一份"假周报"` … `七、案例三点启示`) plus `第 N 步：` sub-steps and standalone sub-labels in section 三:

```python
body = re.sub(r'^([一二三四五六七八九十]+、[^\n]{1,60})$', r'### \1', body, flags=re.M)
body = re.sub(r'^(第 \d+ 步：[^\n]{1,60})$', r'#### \1', body, flags=re.M)
for sub in ['本周三件事', '未来几周的活动', '已报名的联系人', '会后跟进', '可分享的营销内容']:
    body = body.replace('\n' + sub + '\n', '\n#### ' + sub + '\n')
```

⚠️ **Checklist regex trap (fired 2026-08-26)**: asserting "no nested ###" with `re.search(r'^#{1,6}\s*###', body, re.M)` FALSE-POSITIVES on every legit `#### X` sub-heading — `#{1,6}` backtracks to `#` + `###`. Use `re.search(r'^#{3,6}\s+#{3,6}', body, re.M)` (whitespace required between hash groups).

### Flattened prompt-template code block (`<pre>` lines joined into one line)

WeChat `<pre data-lang="markdown">` blocks whose lines are separate `<code>` elements extract as ONE giant line (e.g. the 复现模板 in the Anthropic 销售周报 piece). Rebuild line breaks from the prompt's own structure:

```python
code = code.replace('\xa0', ' ')          # WeChat uses \xa0 after "N."
code = re.sub(r'(?=# )', '\n', code)      # before each "# 角色"-style marker
code = re.sub(r'(?=\d\. )', '\n', code)   # before each numbered item
# then fix glued "# header" + prose pairs (角色 / 发送前校验 had prose continuations):
code = code.replace('# 角色你负责生成每周销售营销简报。', '# 角色\n你负责生成每周销售营销简报。')
```

### Tail citation variant: plain `参考资料` + `原文链接` BEFORE the 📍 CTA

The citation block isn't always `### 资料来源：` — it can be plain `参考资料` + citation + `原文链接：https://…`, placed BEFORE the 📍关注 CTA (verified 2026-08-26, Anthropic piece cites claude.com/blog). The standard splice still works because `cta_start < rec_start`: `body = body[:cta_start].rstrip() + '\n\n' + body[rec_start:]`. Keep `参考资料` / `原文链接` / `其他推荐阅读：` as plain lines (faithful to source).

### Inline `###` mid-sentence

Concept names bolded mid-paragraph extract as inline `###` with the continuation split across a blank line:

```python
m = re.search(r'麦肯锡把它称为### C4重构\s*\n\n：组织从A出发', body)
if m:
    body = body.replace(m.group(0), '麦肯锡把它称为**C4重构**：组织从A出发')
```

### Tail promo structure — keep 资料来源 + 推荐阅读, drop the CTA lines

The tail has three layers, keep/drop as follows:
- **KEEP**: `### 资料来源：` + the McKinsey citation/author list/link (real content), and the `其他推荐阅读：` link list (matches the vault's existing AI组织进化论 archives, which also keep these links).
- **DROP**: `若需全文PDF，也可以私信"报告"，我来发送` (interaction CTA), `📍关注AI组织进化论｜赋能AI组织转型` (follow CTA), and the course-promo paragraph (`极简AI领导力-成为AI原生管理者…欢迎私信交流`).

⚠️ **Tail ORDER trap (fired 2026-08-20 on the 英伟达 ChatGPT Work piece)**: extraction order is `…正文 → OpenAI原文链接 → 📍关注… CTA + course promo → 其他推荐阅读： link list`. The 推荐阅读 list comes AFTER the 📍 CTA, so a naive `body = body[:body.find('📍关注AI组织进化论')]` cut deletes the list too (the vault convention keeps it). Fix — cut only the middle CTA block, splice the list back:

```python
cta_start = body.find('📍关注AI组织进化论')
rec_start = body.find('其他推荐阅读：')
if cta_start != -1 and rec_start != -1:
    body = body[:cta_start].rstrip() + '\n\n' + body[rec_start:]
```

Verify afterwards: `'其他推荐阅读' in body` is True and `'📍关注AI' not in body`.

Also remember the account emits `var nickname = htmlDecode("AI组织进化论")` — grep the raw HTML for the htmlDecode pattern when plain `var nickname = "..."` extraction returns empty (see classification-by-account.md).

### 卡兹克 Prompt-collection articles with nested ```` ```markdown ```` fences (12个Prompt合集 style, verified 2026-08-21)

卡兹克's prompt-collection posts (e.g. 《都Agent时代了，我还是想分享给你这12个我最常用的Prompt。》) contain prompt templates whose TEXT includes a literal ```` ```markdown ```` marker (the prompt is itself a markdown doc with a nested code block). The extraction script wraps each `<pre data-lang="markdown">` in a plain 3-backtick fence, so the literal ```` ```markdown ```` line inside the prompt CLOSES the outer fence early and a trailing ```` ``` ```` re-opens it — the prompt's `##`/`###` lines then render as real headings instead of code, and fences end up unbalanced.

**Detect**: count fence lines with `re.findall(r'^```+', body, re.M)` — an odd count, or a ```` ``` ```` appearing *inside* another 3-backtick block (pattern: ```` ``` ```` `# Role：X` … ```` ```markdown ```` … ```` ``` ```` ```` ``` ````).

**Fix**: rebuild the affected blocks with a **4-backtick outer fence** (````markdown … ````) so the inner 3-backtick ```` ```markdown ```` / ```` ``` ```` lines stay literal:

```python
# broken:  ```\n# Role：深度天赋挖掘机\n...\n```markdown\n## 核心理念...\n```\n```\n
# fixed:   ````markdown\n# Role：深度天赋挖掘机\n...\n```markdown\n## 核心理念...\n```\n````\n
new_block = block.replace('```\n# Role：深度天赋挖掘机', '````markdown\n# Role：深度天赋挖掘机', 1)
new_block = re.sub(r'\n```\n```\n\n$', '\n```\n````\n\n', new_block)   # final fence -> 4 backticks
```

Variant (人生设计术 in the same article): the inner ```` ```markdown ```` closes, MORE prompt content follows (`## 提问流程` etc.), then the final ```` ``` ```` — same 4-backtick outer fence works; everything up to the final ```` ```` is prompt text.

**Verify before upload** with a fence-state parser (CommonMark-ish: track a fence-length stack; a line of N backticks closes when N >= top, opens when N >= 3 and stack empty):

```python
state = []
for l in body.split('\n'):
    m = re.match(r'^(```+)(.*)$', l)
    if m:
        n = len(m.group(1))
        if state and n >= state[-1]: state.pop()
        elif n >= 3: state.append(n)
assert not state   # all fences closed
```

Also for these articles: numbered prompt sub-headings (`1. 苏格拉底式提问`, `2. 反向拆解`, … — numbers restart per section) → `### 1. …` via a replace-list (same rule as 卡兹克 速通-style numbered modes); replace `\xa0` → regular space globally (prompt code blocks use `1.\xa0每次只问一个问题…`); clean garbled image alt like `![Amazon.co.jp: 学会提问 : …](…)` → `![《学会提问》](…)`.

## 商业知识 Account Artifacts (麦肯锡, 2026-08)

Articles from `麦肯锡`'s own account go to 商业知识 by topic (see classification-by-account.md), NOT auto-routed to HR知识. Artifacts: blockquote section headers → `###`; level headings split as `**0级：…**` + `**（"…"）**` on two lines → merge `### 0级：…（"…"）`; author block `> ### Name` noise → bold; cut the 欢迎关注麦肯锡中国 tail promo but keep 作者介绍/感谢. Full detail in `references/wechat-formatting.md` (麦肯锡 Account Artifacts section).

⚠️ **商业知识入口 is a SINGLE-copy page** (verified 2026-08-21: one `## 分类说明`, one `## 主题分类`, one `## 全部文章索引` — NO duplicated second structure like HR知识入口/卡兹克入口). Insert one link in the target subcategory + one in the index, verify full-wikilink count == 2. Style: `[[商业知识/标题|标题]]` (no `00知识库/` prefix). Empty subcategories use placeholder line `暂无专门文章，后续有…` → replace the placeholder, don't append after it.

## Final WeChat Checklist

Before writing the final file:

- Frontmatter starts and ends with `---`.
- `## 摘要`, `## 核心要点`, `## 快速判断`, and `## 原文` are present.
- 摘要 is 150–250 Chinese chars — measure with `len()` on the 摘要 text programmatically, not by eye; overshooting (300+) is the common failure and requires trimming before upload. Note: `len()` counts ASCII too — summaries packed with English tool names/digits (Codex, OpenAI, API, 214个文件) blow past 250 even when the CJK count is only ~150; treat `len(摘要) ≤ 250` as the hard ceiling and trim aggressively.
- ⚠️ **Measure 摘要 length BEFORE the first upload and trim to ≤250 in one local pass** — don't upload, verify, discover 300+, patch, re-upload (3–4 cycles per article; real case 2026-08-17: 卡兹克 Agent piece went 358→297→275→246, 赛普咨询 piece 291→257→251→247). Assemble the whole file in /tmp, run the `len()` check on the 摘要 slice, trim locally until 150–250, THEN PUT once.
- ⚠️ **Data-heavy summaries (multi-benchmark / multi-stat articles) overshoot by 100+ chars — draft with ONE anchor, not full enumeration**. Real case (2026-08-17, 卡兹克 RealReplicaBench piece): first draft enumerated all three benchmarks with task counts + metrics (107 tasks / 23组42项 / 60.75% / 73.79% / 58.82% / 32.5%) → 358 chars, needed THREE trim rounds (358→297→275→246) and re-uploads. Draft strategy: fully detail ONE anchor example (the main benchmark the article is about), compress the others to one-line comparisons ("腾讯 E-Bench 最佳 avg@3 为73.79%，但3次全对稳定性仅58.82%"), and drop secondary metrics. Run `len()` on the 摘要 BEFORE the first upload, not after — a trim means a wasted PUT + GET verify cycle.
- ⚠️ **Undershoot also fails the floor**: a too-terse summary (< 150) silently fails the range too. Real case (2026-08, AI领导力手册 90页PPT piece): first draft hit 145 — expanded with the content form (90页PPT), the concrete deliverable (68个场景提示词), and the access mechanism (回复"AI领导力"下载) to reach 169. If `len(摘要) < 150`, add coverage details (form/scope/deliverable/access), not padding.
- The original body is complete and not summarized away.
- WeChat articles pass `references/wechat-formatting.md`.
- No standalone `!`, empty image links, or empty list items remain.
- Code blocks have balanced fences — count 3-backtick AND 4-backtick fence lines separately. ⚠️ Prompt blocks whose text contains literal ```` ```markdown ```` markers (卡兹克 prompt collections) extract with broken nested fences; wrap the whole block in a 4-backtick outer fence (```` ````markdown … ```` ````) so inner ``` stays literal — see wechat-formatting.md "Prompt blocks with nested fences".
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

### Extraction output is mojibake (Chinese shows as `æ...` / `ç...`)

The script occasionally decodes UTF-8 bytes as latin-1, so `body_markdown` comes back as mojibake — every Chinese character becomes two `æ`/`ç`-style glyphs, while ASCII (AI, ChatGPT, URLs, digits) stays intact. This is NOT a broken extraction: title/date are fine and the body is structurally complete, so a naive "retry" wastes time.

**Fix**: re-encode the body from latin-1 back to UTF-8:

```python
body = data['body_markdown']
body = body.encode('latin-1').decode('utf-8')   # mojibake → correct Chinese
```

Verify the fix worked (`'好' in body` or any CJK substring) before proceeding. If the mojibake appeared in a terminal preview of the JSON, re-read the JSON in Python rather than trusting the shell — the file itself may be fine.

### Extraction script `--json` output key names

`--json` output keys are `body_markdown` and `body_length` — NOT `body`. Reading `data.get('body')` returns empty and can make a successful extraction look like a failure. Always check `data['body_length']` (or `data['body_markdown']`) instead.

⚠️ **You MUST pass `--json` to get machine-readable output.** Without the flag the script prints the human-readable `=== TITLE ===` / `=== BODY MARKDOWN ===` format to stdout, and `json.loads()` fails with `Expecting value: line 1 column 1`. Real case (2026-08): `python3 extraction-script.py --url "<url>" < article.html` produced the human format; re-running with `--json --url "<url>"` returned the JSON object. If you see that JSON parse error, you forgot the flag — do NOT re-fetch the article or suspect mojibake.

Note: when reading `--json` output, the body field is keyed `body_markdown` (not `body`). Reading `data.get('body')` returns None/0 and falsely looks like a failed extraction — always check `body_markdown` for content and `body_length` for the size.

### Extraction script returns mojibake (UTF-8 bytes mis-decoded as latin-1)

Sometimes `body_markdown` comes back as mojibake (`æä»¬ç»å¸¸ä¼æè§` instead of `我们经常会感觉`). This is UTF-8 bytes that got decoded as latin-1/cp1252 somewhere in the script's JSON output. The JSON itself is intact — fix by re-encoding:

```python
body = d['body_markdown']
fixed = body.encode('latin-1').decode('utf-8')
if 'AI' in fixed and '好' in fixed:   # sanity check the decode worked
    body = fixed
```

Try `latin-1` first, then `cp1252`. Detect by a mojibake signature (`æ`, `ç», `å` runs) or by checking that a known Chinese term from the title appears in the decoded text.

### Extraction body comes back mojibake (乱码) — latin-1 round-trip fix

Sometimes the `--json` body_markdown is garbled UTF-8 (e.g. `æä»¬ç»å¸¸ä¼æè§ï¼AIå·²ç»è¿ä¹ç«äº` which should read `我们经常会感觉，AI已经这么火了`). This happens when UTF-8 bytes were decoded as latin-1/cp1252 somewhere along the fetch/pipe path. Recovery is a one-line re-decode:

```python
body = body.encode('latin-1').decode('utf-8')
```

Try `latin-1` first, fall back to `cp1252`; sanity-check the result contains real Chinese and the article's key terms. Verified on a 数字生命卡兹克 piece (2026-08): title/account/date extracted clean, only the body was garbled — do NOT re-fetch the URL when this happens, the round-trip fix is sufficient. Note `len(body)` still reports the garbled byte-count, so run the round-trip BEFORE counting 摘要 length or trimming.

### Slide-based / image-heavy WeChat articles

Some WeChat articles are published as slide decks — the body is almost entirely `<img>` tags with minimal text (slide titles/bullets). The extraction script will produce a stream of `![image](url)` lines with sparse text between them.

**How to handle**:
1. Extract all available text framework (headings, bullet points) from between images.
2. Preserve all image links in the `## 原文` section so the visual content is not lost.
3. Note in the body: `> **注**：本文原为幻灯片形式发布，正文内容嵌入在图片中。以下为从页面中提取的文字框架。`
4. Write summaries from the text framework — don't fabricate detail not present in the extracted text.
5. Still run the full quality checklist; the template sections remain mandatory.

### Extraction script outputs mojibake (UTF-8 bytes decoded as latin-1)

Sometimes extraction "succeeds" (title/date/body_length all populated) but the body is garbage: `æä»¬ç»å¸¸ä¼æè§ï¼AIå·²ç»è¿ä¹ç«äº` instead of readable Chinese. The script emitted UTF-8 bytes that were decoded as latin-1/cp1252.

**Detection**: body is full of high-bit ASCII sequences (`æ`, `ç`, `å`, `è` runs) and no recognizable Chinese words.

**Fix** — round-trip the bytes back to UTF-8:

```python
body = body.encode('latin-1').decode('utf-8')
```

Verify after the fix that real Chinese appears (check for a title keyword). Fired on 数字生命卡兹克's `从0开始，12步学会用好AI。` (2026-08): the `--json` body was mojibake; the round-trip fixed it cleanly with no other repair needed. Note: `--json` may also emit the mojibake into the saved file if you pipe directly — always inspect a sample before building the article.

### Jianguoyun rejects `|` in filenames (HTTP 400 IllegalArgument)

A literal `|` in a WeChat title (e.g. `森马把AI塞进服装生意：1亿"确认回款"背后的转型方法论 | AI新组织观察`) is invalid on 坚果云 WebDAV even percent-encoded (`%7C`). PUT fails with:

```
<d:error ...><s:exception>IllegalArgument</s:exception><s:message>the nustore path is not valid /00知识库/AI知识/... | ....md</s:message></d:error>
```

HTTP 400 alone is ambiguous (other bad paths also 400), so read the response body — it echoes the decoded path. **Fix**: replace ` | ` with ` - ` in the FILENAME only (`...方法论 - AI新组织观察.md`), keep the original title with `|` in frontmatter `title` and the H1, and use the sanitized filename in entry-page wikilinks. Fired on the 中欧商业在线 森马 piece (2026-08).

### Republished WeChat article (same title, new sn URL) — update in place, don't duplicate

Accounts like 高绩效HR repost the same PPT deck under a new `mp.weixin.qq.com/s/<sn>` URL while keeping identical `mmbiz.qpic.cn` image URLs. The user may send the new link weeks later.

⚠️ **PROPFIND keyword hit ≠ duplicate. Verify title AND content before deciding update-in-place vs new file.** A grep match on a shared keyword (e.g. `麦肯锡`) often surfaces a *sister piece* — same author/series, different title and different content — not a repost. Real example (2026-08): `麦肯锡2026消费报告：4大变化，4大机会` (2026-07, →市场营销) vs `麦肯锡最新季刊：5大变化，5大机会` (2026-08, →战略管理) both live in 商业知识 and both match `grep '麦肯锡'`, but they are separate articles. Decision rule: **identical title + same body** → repost, update in place; **title differs in substance** (different 变化 count, different report, different content) → archive as a NEW file and add entry-page links normally.

**Before archiving, check the vault for an existing file with the same title** (PROPFIND the target folder):

```bash
curl -s -u 'USER:PASS' -X PROPFIND "https://dav.jianguoyun.com/dav/obsidian/00知识库/HR知识/" -H "Depth: 1" \
  | grep -oP '(?<=<d:href>)[^<]+' | grep -E '标题关键词'
```

⚠️ **PROPFIND hrefs are percent-encoded (lowercase hex)** — `grep -E '中文关键词'` against the raw href output silently returns nothing even when the file EXISTS, because the href is `%e9%ba%a6%e8%82%af...` not `麦肯锡...`. This makes a false "NOT FOUND" — you'd create a duplicate. Decode before grepping:

```bash
curl -s -u 'USER:PASS' -X PROPFIND "https://dav.jianguoyun.com/dav/obsidian/00知识库/HR知识/" -H "Depth: 1" \
  | grep -oP '(?<=<d:href>)[^<]+' \
  | python3 -c "import sys,urllib.parse; [print(urllib.parse.unquote(l.strip())) for l in sys.stdin]" \
  | grep -E '标题关键词'
```

Same trap applies to post-upload verification: to confirm a file landed in a folder, decode hrefs first (or grep the encoded tail of the known URL), then check. A raw grep of decoded Chinese against encoded hrefs is not evidence of absence.

⚠️ **PROPFIND hrefs are percent-encoded — decoded Chinese keywords silently match nothing.** Jianguoyun's PROPFIND response returns hrefs as lowercase percent-encoded UTF-8 (e.g. `%e9%ba%a6%e8%82%af%e9%94%a1...`), so `grep '麦肯锡'` or `grep '三支柱'` returns empty even when matching files exist (a false negative that can cause a duplicate archive). ASCII-only keywords like `HR`, `AI`, `PPT` DO match literally because they stay unencoded — which makes a mixed `grep -E 'HR|麦肯锡'` look like it works while only the ASCII alternative is matching. **Fix**: decode the hrefs before grepping:

```bash
curl -s -u 'USER:PASS' -X PROPFIND "https://dav.jianguoyun.com/dav/obsidian/00知识库/AI知识/" -H "Depth: 1" \
  | grep -oP '(?<=<d:href>)[^<]+' \
  | python3 -c "import sys,urllib.parse; [print(urllib.parse.unquote(l.strip())) for l in sys.stdin]" \
  | grep '标题关键词'
```

(Only relevant for duplicate-title checks — the PROPFIND listing itself works fine with either encoded or unencoded path in the request URL.)

If the file already exists: **update it in place** —
1. Refresh `url` (and `date`) in the frontmatter + footer to the new repost link.
2. Enrich the body if the old archive was thin (e.g. image-only, no text framework) — see `references/slide-articles.md` OCR workflow.
3. Do NOT create a second file, and do NOT add entry-page wikilinks: the title is almost certainly already linked (possibly inside `<mark class="conflict">` blocks from a merge). Verify before touching the entry page; leave conflict markers alone.

Use a `curl -T /tmp/file` PUT to overwrite the existing WebDAV path (same filename), then verify with GET — the file count in the folder must not increase.

### PROPFIND duplicate-check silently misses Chinese keywords (percent-encoded hrefs)

PROPFIND `Depth: 1` responses return `<d:href>` values that are **percent-encoded** (e.g. `%e9%ba%a6%e8%82%af%e9%94%a1...` for 麦肯锡...). Grepping that output for decoded Chinese keywords (`grep -E '麦肯锡|三支柱'`) **silently returns nothing even when the file exists** — it looks like "NOT FOUND / new file" when a duplicate actually exists. This produced a false "new file" verdict in a real archiving session (the McKinsey HR report already existed under a similar title in the target folder).

Fix — decode hrefs before grepping, or check the exact file URL:

```bash
# Option A: decode hrefs with python, then grep Chinese
curl -s -u 'USER:PASS' -X PROPFIND "https://dav.jianguoyun.com/dav/obsidian/00知识库/HR知识/" -H "Depth: 1" \
  | grep -oP '(?<=<d:href>)[^<]+' \
  | python3 -c "import sys,urllib.parse; [print(urllib.parse.unquote(l.strip())) for l in sys.stdin]" \
  | grep -E '麦肯锡|三支柱'

# Option B: GET the candidate file URL directly — 404 = truly new, 200 = exists
curl -s -o /dev/null -w '%{http_code}' -u 'USER:PASS' "https://dav.jianguoyun.com/dav/obsidian/00知识库/HR知识/候选标题.md"
```

When in doubt, prefer Option B (HTTP status on the exact encoded URL) — it is unambiguous and also verifies the exact filename matches.

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
- 🔍 **Check whether the conflict zone is at the END of the section first**: the break-on-conflict rule above is only correct when the conflict block is the last thing in the index section. If clean wikilinks exist AFTER the conflict block (conflict is mid-file — check the file tail: it ends with a `- [[...]]` wikilink line, not `</mark>`), breaking at the first conflict marker inserts the new link mid-index: still exactly 2 occurrences and outside conflicts, but out of the append-at-end order. In that case insert after the ABSOLUTE last wikilink of the section (append at end) instead of breaking at the conflict. Example: AI知识入口 has a mid-file conflict in both AI应用 and 全部文章索引 with clean links after it — append at end there. ⚠️ 卡兹克入口's structure has flipped multiple times — as of 2026-08-11 it HAS `## 全部文章索引` again, with conflict markers at the END of both `### AI资讯` and the index section, so a new article link appears there exactly **2×** (once in the subcategory, once in the index) and break-on-conflict insertion applies in BOTH sections — insert after the last clean wikilink, before the `<mark class="conflict"` line, in each section; check the live file before choosing 1× vs 2×.
- ♻️ **Fixing a misplaced mid-index insertion**: if a link already landed before a mid-file conflict zone, remove the index occurrence and re-append at end: split content at `## 全部文章索引`, remove the first occurrence of the link line in section2 (`section2.replace(LINK_LINE + '\n', '', 1)` — safe: the subcategory occurrence lives in section1), then append at the very end (`section2.rstrip('\n') + '\n' + LINK_LINE + '\n'`). Re-upload and verify: full-link count stays 2, conflict count unchanged.

Verify after upload that conflict marker count is unchanged (`grep -c 'conflict'` before and after) and the full wikilink appears exactly 2×.

⚠️ **Only break on conflict when the conflict block is the LAST thing in the index.** If clean wikilinks follow the conflict zone (conflict in the MIDDLE of the index), the break-on-conflict loop above lands the new link mid-index instead of at the end — out of order and confusing. This happened with `AI知识入口.md`, where the conflict block sat mid-index with 3 clean links after it. In that case, find the absolute last wikilink in the section and insert after it (no conflict break):

```python
last_idx = max(i for i, line in enumerate(s2_lines) if line.startswith('- [['))
s2_new = '\n'.join(s2_lines[:last_idx+1]) + '\n' + NEW_LINK + '\n' + '\n'.join(s2_lines[last_idx+1:])
```

If the misplaced link already landed (link appears 2× but one occurrence is mid-index), repair by removing that one occurrence from section2 (`section2.replace(LINK_LINE + '\n', '', 1)`) and appending at the file end (`section2.rstrip('\n') + '\n' + LINK_LINE + '\n'`).

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
| Author is 卡兹克 | Full-article archive in `卡兹克/<subfolder>/` (or `卡兹克/` root for personal-reflection 心得分享类 articles — see Classify Destination). (卡兹克's tutorials are archived like any other article — the user prefers full-body preservation.) |

### Knowledge card format

See `references/knowledge-card-format.md` for the template, frontmatter, and card-numbering rules. Only use when explicitly requested.

### Card numbering

Cards are numbered **by `card_tag` sequence**, not globally. Check the existing cards in `00知识库/00知识卡片/` to find the next number for the target tag.

Existing tags in use: `AI`, `GROWTH`, `STRATEGY`.

## Skill Maintenance (GitHub sync)

This skill's public home is `github.com/oceanzhang28/article-archiver-skill` (SSH push pre-configured via deploy key; remote `git@github.com:oceanzhang28/article-archiver-skill.git`). The installed local copy is the working superset — after improving it locally, push the changes back (`git add -A && git commit && git push origin main`) so the public repo stays current. Keep `README.md` and `agents/openai.yaml` in the repo. The 商业知识 (business) category is part of the installed skill (see Classify Destination).

## References

- `references/wechat-extraction.md`: Fetching WeChat article HTML, metadata extraction, and script usage.
- `references/wechat-formatting.md`: WeChat HTML-to-Markdown formatting rules and post-extraction checks. Includes account-specific artifacts: 润米商城/刘润 (第NNNN篇原创文章 tail marker, 最后的话 heading, promo footer collapse), TRAE.ai (plugin lists, 更多技巧 numbered items order-dependence, 小技巧 callouts), AI与组织领导力跃迁/罗明 (header strip, inline-###→bold incl. em-dash `——` continuation merges, section numbers, tail promo cut + sign-off re-append), 高绩效HR, AI组织进化论, 赛普咨询, 首席组织官, 麦肯锡, 书图与手记, 物业管理实践, 卡兹克.
- `references/summary-guidelines.md`: Summary and note-writing rules.
- `references/knowledge-card-format.md`: Knowledge card template, frontmatter, and numbering rules.
- `references/extraction-script.py`: Standalone WeChat extraction script.
- `references/ocr-fallback.md`: Tesseract OCR workflow for screenshots when the vision API is unavailable.
- `references/slide-articles.md`: Detailed guidance for slide-based / image-heavy WeChat articles.
- `references/classification-by-account.md`: Account-to-folder mapping for WeChat article classification. TRAE.ai/Trae-Real AI Engineer → AI知识/AI工具 (verified 2026-08-23).
