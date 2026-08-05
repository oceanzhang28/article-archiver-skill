---
name: article-archiver
description: "Use when the user asks to archive, save, transfer, or batch-import WeChat public-account articles, web articles, article links, or long text into Obsidian knowledge folders with complete original body, summaries, and entry-page links."
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
5. In the Jianguoyun WebDAV environment, write through WebDAV PUT and verify with WebDAV GET. Do not rely on the FUSE mount for persistence.

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

### Excel or CSV Batches

If the user provides a batch file, read article title and URL columns, extract each article independently, then update entry pages after all article files are ready. Do not add duplicate links if the same title or path already exists.

Batch mode must not lower note quality. For every article, read enough of the full body to understand the thesis, evidence, examples, middle sections, and conclusion before writing `## 摘要` and `## 核心要点`. Never generate summaries by copying the opening paragraphs or using a generic template such as `文章围绕“标题”展开`. If there is not enough time to write real summaries for the full batch, archive fewer articles and continue later rather than writing low-quality notes.

## Classify Destination

| Destination | Use When | Path |
| --- | --- | --- |
| HR | HR, OD, talent, compensation, performance, recruiting, HRBP, SSC, workforce effectiveness | `00知识库/HR知识/` |
| AI | AI tools, AI workflows, prompt, agent, AI products, AI applications, AI-era personal development | `00知识库/AI知识/` |
| 商业知识 | business strategy, business models, growth, marketing, product strategy, operations, finance, capital markets, company cases, entrepreneurship, industry analysis | `00知识库/商业知识/` |
| 卡兹克 | Author is 卡兹克 / 数字生命卡兹克, or the article belongs to that author collection | `00知识库/卡兹克/` |

Priority: if an article is authored by 卡兹克 / 数字生命卡兹克, classify it under 卡兹克 first. If an article is both AI and HR, classify by the main reader problem: AI tool/workflow/product learning goes to AI; HR organization/talent/workforce problems go to HR. If an article is both business and HR or AI, classify by the dominant topic, not by incidental examples.

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

1. Read the full entry page.
2. Add one wikilink to the selected subcategory section.
3. Add one wikilink to the all-articles index section if that section exists.
4. Keep existing order if the page already has one. Otherwise append to the relevant list.
5. Check for existing same-title or same-path links before adding.

Wikilink format:

```markdown
- [[relative/path/filename|display title]]
```

Use the path relative to the vault when the file is in a nested folder or when duplicate titles may exist. Omit `.md`.

## WebDAV Writing

`/mnt/obsidian/` is a Jianguoyun WebDAV FUSE mount. Writes through the mount may appear successful but fail to persist. Upload files with WebDAV PUT, then verify with WebDAV GET.

Do not hardcode credentials in this skill. Read credentials from `/etc/davfs2/secrets` or environment variables provided by the deployment.

Required write flow:

1. Convert `/mnt/obsidian/{relative path}` to WebDAV URL path under `https://dav.jianguoyun.com/dav/obsidian/`.
2. URL-encode each path segment.
3. Upload with `curl -T`.
4. Treat HTTP `201` and `204` as success.
5. Read the same URL back and verify the expected title/frontmatter exists.

## Final Quality Checklist

Before writing the final file:

- Frontmatter starts and ends with `---`.
- `## 摘要`, `## 核心要点`, `## 快速判断`, and `## 原文` are present.
- The original body is complete and not summarized away.
- WeChat articles pass `references/wechat-formatting.md`.
- No standalone `!`, empty image links, or empty list items remain.
- Code blocks have balanced triple backticks.
- Paragraph repair did not modify code blocks, tables, lists, or blockquotes.
- Entry-page links are not duplicated.
- WebDAV GET confirms the uploaded content.

## References

- `references/wechat-extraction.md`: Fetching WeChat article HTML, metadata extraction, and script usage.
- `references/wechat-formatting.md`: WeChat HTML-to-Markdown formatting rules and post-extraction checks.
- `references/summary-guidelines.md`: Summary and note-writing rules.
- `references/extraction-script.py`: Standalone WeChat extraction script.
