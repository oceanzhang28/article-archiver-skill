# Article Archiver Skill

Article Archiver is a Codex skill for archiving WeChat public-account articles, web articles, article links, and long text into an Obsidian knowledge base.

It is designed for an Obsidian vault organized under `00知识库/`, with complete original article preservation, structured reading notes, and automatically maintained entry-page links.

## What It Does

- Archives articles into Obsidian Markdown files.
- Preserves the complete original body instead of replacing it with a summary.
- Adds structured note sections before the original text:
  - `摘要`
  - `核心要点`
  - `这篇解决什么问题`
  - `快速判断`
  - `原文`
- Classifies articles into the proper knowledge folder.
- Updates the matching Obsidian entry page with wikilinks.
- Supports batch imports from Excel or CSV files.
- Includes WeChat-specific extraction and formatting rules to reduce common Markdown conversion errors.

## Supported Knowledge Areas

The skill currently supports four top-level Obsidian knowledge areas:

| Area | Folder | Entry Page |
| --- | --- | --- |
| HR知识 | `00知识库/HR知识/` | `00知识库/HR知识入口.md` |
| AI知识 | `00知识库/AI知识/` | `00知识库/AI知识入口.md` |
| 商业知识 | `00知识库/商业知识/` | `00知识库/商业知识入口.md` |
| 卡兹克 | `00知识库/卡兹克/` | `00知识库/卡兹克入口.md` |

For 卡兹克 articles, the author collection takes priority over topical classification.

## WeChat Article Handling

WeChat public-account articles often lose formatting when converted directly from rendered text. This skill therefore instructs Codex to:

- Extract article HTML from `div#js_content` or `content_noencode`.
- Preserve paragraph, quote, list, code, table, and image order.
- Repair common WeChat conversion artifacts such as broken bold markers, collapsed paragraphs, malformed quote blocks, and empty image links.
- Run a final formatting checklist before writing the Markdown file.

The reusable extraction helper lives at:

```text
references/extraction-script.py
```

## Summary Quality

The skill requires summaries to synthesize the full article, not simply copy the opening paragraphs.

For each archived article, Codex should read enough of the beginning, headings, middle examples, and conclusion to understand the author's actual argument. Batch mode follows the same standard as single-article mode.

Commercial articles get one extra requirement: summarize the business question, the author's judgment, the company or industry evidence, the causal logic, and the transferable lesson.

## Repository Layout

```text
article-archiver-skill/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
└── references/
    ├── extraction-script.py
    ├── summary-guidelines.md
    ├── wechat-extraction.md
    └── wechat-formatting.md
```

## Installation

Clone this repository into a Codex skill directory:

```bash
git clone https://github.com/oceanzhang28/article-archiver-skill.git ~/.codex/skills/article-archiver
```

Then ask Codex to use `$article-archiver` when saving articles into Obsidian.

## Notes

- The Hermes deployment assumes the Obsidian vault is available at `/mnt/obsidian/`.
- In Jianguoyun WebDAV environments, the skill instructs Codex to write through WebDAV and verify with a read-back check.
- WebDAV credentials should come from deployment secrets or environment variables, not from this repository.
