# WeChat Formatting Rules

Use this reference after extracting the WeChat article body HTML and before writing the Obsidian file.

## Non-Negotiable Rule

Preserve the article's reading structure. A clean but structureless plain-text dump is a failed archive.

## HTML-to-Markdown Mapping

| WeChat HTML Pattern | Markdown Output |
| --- | --- |
| `<p>`, meaningful `<section>`, meaningful `<div>` | Separate paragraphs or blocks with blank lines |
| `<br>` | Line break |
| `<strong>`, `<b>` | `**text**` |
| `<em>`, `<i>` | `*text*` |
| `<a href>` | `[text](href)` if text is meaningful; otherwise keep text |
| `<img>` | `![alt](data-src or src)` at the original position |
| `<ul>/<ol>/<li>` | Markdown list |
| `<blockquote>` | `>` blockquote |
| `<pre>` | fenced code block |
| `<code>` inside prose | inline code |
| `<table>` | Preserve as HTML unless conversion is clearly correct |

Treat `section` and `div` as structural blocks. Many WeChat articles use them instead of semantic paragraph, quote, or callout tags.

## Quote and Callout Modules

WeChat quote blocks are often styled `section` or `div`, not real `blockquote`.

Convert a block to Markdown quote when it has any of these signals:

- style contains `border-left`
- style contains a light background plus padding/margin, commonly `background`, `background-color`, `padding`, `margin`
- class or data attributes include `quote`, `blockquote`, `rich_media_tool`, or similar wording
- the visual/content role is clearly a cited paragraph, aside, author comment, or external excerpt

Conversion:

```markdown
> first line
> second line
```

For lists inside quotes:

```markdown
> - item one
> - item two
```

Do not merge quote blocks into neighboring paragraphs.

## Images

For each `<img>`:

1. Prefer `data-src`.
2. Fallback to `src`.
3. Preserve the image at its original location.
4. Use `alt`, `data-w`, `data-ratio`, or nearby caption text only when useful.
5. Delete broken standalone `!` lines.

Remote WeChat image links such as `mmbiz.qpic.cn` may expire. If long-term image preservation is required, download images into a local assets folder and rewrite links, but do this only when the user or deployment expects local assets.

## Paragraph Repair

Paragraph repair is a fallback, not the main extraction strategy.

Only split long text when all are true:

- The text is ordinary prose.
- A paragraph or line exceeds roughly 500 Chinese characters.
- It is not inside a code block, blockquote, table, list, or image-caption cluster.

Split at Chinese sentence endings `。！？` and prefer natural transition boundaries such as `但是`, `不过`, `其实`, `所以`, `然而`, `同时`, `因此`.

Never remove all whitespace with `\s+ -> ""`; that can destroy English terms, code, URLs, and list indentation.

## Merged Heading Repair

Repair patterns like:

```markdown
**一. Frontend Design**大名鼎鼎的...
```

Preferred output:

```markdown
### 一. Frontend Design

大名鼎鼎的...
```

Also repair bold standalone section names such as `**写在最后**` when they are clearly headings.

Also repair standalone numbered bold headings:

```markdown
**一. 安装Codex**
```

to:

```markdown
### 一. 安装Codex
```

Delete standalone `**` lines left by WeChat nested bold/image markup.

## Embedded Files and Code-Like Blocks

Some articles embed config files, prompts, `CLAUDE.md`, `AGENTS.md`, or code snippets. Extraction can accidentally turn them into many Markdown headings or collapse the whole file into a few very long prose lines.

Treat a block as embedded file/code content when any signal appears:

- 3 or more consecutive `##` lines with no blank line separator
- a `## ` line longer than about 60 characters
- content includes known config headings such as `关于我`, `第一性原理`, `约束先行`, `交互设计`, `工作方式`, `开发习惯`, `Git`, `部署`, `CLAUDE.md`, `AGENTS.md`
- many lines contain indentation, braces, shell commands, YAML, JSON, or Markdown instructions
- text contains AGENTS.md-style phrases such as `Behavioral guidelines to reduce common LLM coding mistakes`, `Simplicity First`, `Surgical Changes`, or `Goal-Driven Execution`
- one or more lines exceed 500 characters because Markdown headings/lists were collapsed, especially patterns like `## 1. ...### ...Before implementing:- ...`

Prefer fenced code blocks for config/code:

````markdown
```markdown
## 关于我
...
```
````

Use blockquote only when the original looks like quoted prose rather than file content.

When a copied AGENTS.md block is collapsed, restore line breaks inside the fenced block before archiving:

- split before `## 1.`, `## 2.`, `## 3.`, `## 4.`
- split before `###`
- split `Before implementing:-` into `Before implementing:` plus list items
- split numbered plan examples `1. [Step]`, `2. [Step]`, `3. [Step]` onto separate lines

Also clean common WeChat footer artifacts:

- `****### 以上...` -> `### 以上...`
- standalone `****` lines -> delete
- `>/ 作者：...` -> `> / 作者：...`

## Final WeChat Checklist

- Body came from `js_content` or `content_noencode`, not from whole-page boilerplate.
- Paragraphs have blank lines between blocks.
- Quote/callout modules use `>`.
- Lists are real Markdown lists.
- Images are not all moved to the end.
- No standalone `!` remains.
- Code/config blocks are fenced and have balanced backticks.
- Tables are readable.
- The original article order is preserved.
- The summary and notes are added before `## 原文`, not mixed into the body.
