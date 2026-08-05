# Knowledge Card Format

Use when archiving a WeChat article as a **condensed structured summary** instead of a full-body archive. Knowledge cards go to `00知识库/00知识卡片/` in the Obsidian vault.

## Decision

Knowledge cards are for **tutorials, how-to guides, and condensed practical knowledge**. Full-article archive is for narrative long-form pieces, news, and industry reports where the original body nuance matters. See SKILL.md's "Knowledge Card Path" section for detailed decision rules.

## Frontmatter

```yaml
---
tags: [知识卡片, <domain-tag>, <topic-tag>]
alias: [<short-hand-title>]
created: <YYYY-MM-DD>
card_tag: <TAG>       # One of: AI, GROWTH, STRATEGY (extend as needed)
card_number: <NNN>     # Sequential per card_tag, check existing cards for next number
card_author: <author-name>
source: <original-URL>
---
```

- `card_tag`: groups cards by domain. `AI` = AI technology/concepts, `GROWTH` = personal development/skills, `STRATEGY` = strategy/tactics.
- `card_number`: **per tag**, not global. Check `00知识库/00知识卡片/` for existing cards with the same `card_tag` to find the next number.
- `source`: always the original WeChat article URL.

## Body Template

```markdown
# <Original Title>

> <Key pull-quote or subheading from the article>

`[<CARD_TAG>]` `NO.<NNN>`

## 📋 文章总结

### 摘要
<150-250 Chinese characters: what the article is about and why it matters>

### 解决什么问题
<One sentence: what decision, action, or understanding problem this article addresses>

### 快速判断
<One-two sentences: who should read it and for what purpose>

---

## 📊 核心发现 / 💡 核心洞见

<Structured presentation of key findings using tables, lists, or subsections as appropriate. Focus on extracting the actionable value.>

## 🛠 方法论 / 如何运用 (optional — for tutorial/how-to articles)

<Step-by-step methods or actionable guidance extracted from the article. Use numbered lists or subsections.>

## 💡 我的思考 (optional)

<Your own synthesis — what this means for the user's context. This is the value-add beyond summarization.>

---

> **原文链接：** [<title>](<url>)

---

*文章编号：<CARD_TAG> NO.<NNN> | 整理时间：<YYYY-MM-DD>*
```

## Mandatory Elements

Every knowledge card MUST include:
1. **YAML frontmatter** with at minimum: `tags`, `created`, `card_tag`, `card_number`, `source`
2. **`## 📋 文章总结`** section with `### 摘要`, `### 解决什么问题`, `### 快速判断` subsections
3. **Source link** in the footer (`> **原文链接：** [title](url)`)
4. **Card tag badge** and **number badge** near the top (`[CARD_TAG]` `NO.NNN`)

Missing any of these = redo.

## Example

See existing cards in `00知识库/00知识卡片/` for real examples:
- `AI NO.001 - Loop Engineering.md` — card_tag: AI, card_number: 001
- `用AI这三年9条心得.md` — card_tag: GROWTH, card_number: 002
- `6个Prompt心法.md` — card_tag: STRATEGY, card_number: 004
