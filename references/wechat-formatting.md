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
**01**
```

to:

```markdown
### 01
```

Also repair combined `**###` artifacts where bold markup and a heading are fused on the same line (common on 刘润/润米商城 articles, which use `**01**` section numbers followed by `**### 标题` lines):

```markdown
**01**

**### 一家公司：三千亿美金的“咨询公司”
```

to:

```markdown
### 01

### 一家公司：三千亿美金的“咨询公司”
```

Fix with a replace-list (assert each anchor is found, print NOT FOUND otherwise) or a regex:

```python
body = re.sub(r'^\*\*(0\d)\*\*$', r'### \1', body, flags=re.M)   # **01** -> ### 01
body = re.sub(r'^\*\*### ', r'### ', body, flags=re.M)           # **### X -> ### X
```

For heading splits across two lines (`**### 咨询公司：` + `****从一单单的项目，变成长时间的陪伴**`), merge into one `###` heading line.

Also repair standalone numbered bold headings:

```markdown
**一. 安装Codex**
```

to:

```markdown
### 一. 安装Codex
```

Delete standalone `**` lines left by WeChat nested bold/image markup.

## Plain-Text Section Titles → `###` Headings

Many WeChat articles use bare-text section titles (no bold, no heading tag) that extraction emits as standalone lines:

```markdown
前言：一个很少被觉察的本质问题
第一部分：项目交付了，然后呢？
尾声：一个专业真正成熟的标志，不是越来越重要……
一、FDE到底是什么？
为什么AI越强，越需要这种人？
```

Convert these to `###` headings — but ALWAYS capture the whole line including the prefix:

```python
# ✅ Correct: capture the full line, keep the 第X部分：/前言：/尾声：/一、 prefix
body = re.sub(r'^(第[一二三四五六]部分：[^\n]+)$', r'### \1', body, flags=re.M)
body = re.sub(r'^(前言：[^\n]+)$', r'### \1', body, flags=re.M)
body = re.sub(r'^(尾声：[^\n]+)$', r'### \1', body, flags=re.M)
body = re.sub(r'^(一、[^\n]+)$', r'### \1', body, flags=re.M)
body = re.sub(r'^(二、[^\n]+)$', r'### \1', body, flags=re.M)

# ❌ Wrong: replacing just the matched prefix drops the section number
body = re.sub(r'^第[一二三四五六]部分：', '### ', body, flags=re.M)
# "第一部分：项目交付了，然后呢？" becomes "### 项目交付了，然后呢？" — prefix lost
```

Then merge any heading line directly followed by body text (no blank line between):

```python
body = re.sub(r'(### [^\n]+)\n([^\n])', r'\1\n\n\2', body)
```

Also strip leading full-width ideographic-space indentation (`\u3000`, WeChat's paragraph indent) at line starts — safe when paragraphs are already separated by blank lines, and it keeps Obsidian output clean:

```python
body = re.sub(r'^[\s\u3000]+', '', body, flags=re.M)
```

If consecutive numbered items were split into separate paragraphs (`1. xxx` blank line `2. xxx`), collapse them into one list after fixing the number splits:

```python
body = re.sub(r'^(\d+\. [^\n]+)\n\n(\d+\. [^\n]+)', r'\1\n\2', body, flags=re.M)  # repeat 2–3×
```

**Vault heading-level convention**: before choosing `##` vs `###`, check one existing archived article in the target folder. AI知识 archives (e.g. `企业AI工作流设计-Anthropic市场团队最新AI原生实践.md`) use `##` for the article's main sections and `###` for sub-steps — same level as the `## 原文` header. The generic `###` rule above is a floor, not a mandate; match the dominant convention of the target folder.

## Inline Bold Mis-tagged as `###` Headings

The extraction script sometimes converts WeChat `<strong>` blocks to `###` headings instead of `**bold**`, especially when the bold text appears mid-paragraph or functions as an emphasized concept name rather than a section heading. This produces artifacts like:

```markdown
理清权责，有一个简单实用的工具：### 三列权责清单
```

The fix is `sed`-based targeted replacement:

```bash
# Inline ### within paragraphs → **bold**
sed -i 's/：### 三列权责清单/：**三列权责清单**/' article.md
sed -i 's/——### 全球员工16万人/——**全球员工16万人**/' article.md

# Table cell ### markers → **bold**
sed -i 's/<td>### 关键词/<td>**关键词**/' article.md
```

**Detection**: after extraction, run `grep -n '###' article.md | grep -v '^[0-9]*:### '` to find `###` that are NOT at line start — these are almost always inline bold text that needs repair.

**Judgment call**: `###` at line start may be legitimate sub-headings (e.g. case-study company names like `### 中海物业`). Check context: if the line introduces a distinct sub-topic with multiple paragraphs following, keep it as `###`. If it's a short emphasized phrase embedded in the flow of a single paragraph, convert to `**text**`.

**Batch fix with a Python replace-list (preferred over many sed calls)**: articles with this artifact (especially 解读/拆解-style posts where the author bolds concept names mid-paragraph) have MANY instances. Collect them into a list and replace in one pass, printing NOT FOUND so a failed anchor doesn't silently skip:

```python
fixes = [
    ('本质是### "旧瓶装新酒"', '本质是**"旧瓶装新酒"**'),
    ('第一类是### 工具层回报', '第一类是**工具层回报**'),
    ('转向### 目标设定、复杂判断、资源整合、冲突处理和最终责任承担', '转向**目标设定、复杂判断、资源整合、冲突处理和最终责任承担**'),
    ('### 三支柱不会消失，但内涵会彻底变了。', '**三支柱不会消失，但内涵会彻底变了。**'),  # standalone ### bold-highlight line
    ('### ——', ''),  # broken standalone artifact
]
for old, new in fixes:
    if old in body:
        body = body.replace(old, new)
    else:
        print("NOT FOUND:", old[:40])
```

**Continuation punctuation split after bold**: after inline `###`→bold fixes, the article may still have `<br>`-split continuations where the punctuation (`"` `。` `，` `：` `；` `——`) sits alone on the next line after a bold phrase:

```markdown
需要配置怎样的**人+AI能力组合**

"。
```

Merge them with a generic loop (also do this for `**bold**\n\n"`-style splits):

```python
import re
for punct in ['"', '。', '，', '：', '；', '——']:
    body = re.sub(r'(\*\*[^*\n]{1,80}\*\*)\n\n' + re.escape(punct), r'\1' + punct, body)
body = re.sub(r'\n{3,}', '\n\n', body)
```

Then re-run the standalone-punctuation check (list lines whose stripped content is exactly `"` `。` `，` `：` `；` `——`) to confirm nothing remains.

### Numbered-stat bullets with `\xa0` (AI组织进化论-style)

Accounts like `AI组织进化论` emit numbered-stat bullets where a bold number/result sits after a non-breaking space, and the sentence continues after a `<br>` with NO blank line. Extraction yields:

```markdown
• 约\xa0### 4 万名英伟达员工
拥有 Codex 使用权限；
• 研究人员称，端到端机器学习研究流程获得了约\xa0### 10 倍提速
；
```

Two traps combine to make naive fixes fail silently:

1. The space before `###` is U+00A0 (`\xa0`), so a hand-typed literal-space `replace()` never matches — use `\s*` in the regex (Python `\s` matches `\xa0`).
2. The continuation is a SINGLE `\n` (no blank line), so the `\n\n`-based continuation-merge regexes in the previous section never fire. Match `\n` directly.

Fix (one pass, `\s*` everywhere):

```python
body = re.sub(r'约\s*###\s*4 万名英伟达员工\n拥有 Codex 使用权限；', '约 **4 万名英伟达员工**拥有 Codex 使用权限；', body)
body = re.sub(r'获得了约\s*###\s*10 倍提速\n；', '约 **10 倍提速**；', body)
body = re.sub(r'借助 Codex\s*###\s*几小时内完成搭建\n；', '借助 Codex **几小时内完成搭建**；', body)
body = re.sub(r'可达到约\s*###\s*20 倍\n。', '可达到约 **20 倍**。', body)
```

Then re-run the standalone-punctuation check (list lines whose stripped content is exactly `"` `。` `，` `：` `；` `——`) to confirm nothing remains.

## Metadata Line `###` Artifact

The extraction script sometimes produces `###` artifacts on author/header metadata lines, especially when the original WeChat article uses HTML structures like `<p>文 / <strong>姓名</strong></p>`:

```markdown
文 / ### 陈明

### ，华夏基石管理咨询集团高级合伙人
```

**Detection**: After extraction, search for `###` that appears after text on a line (e.g. `grep '###' article.md | grep -E '^(文|来源|作者|编辑|责编|图|摄)'`).

**Fix**: Merge these into a single clean line with **bold**:

```bash
# Fix "文 / ### 姓名" patterns
sed -i 's|文 / ### \(.*\)|文 / **\1**|' article.md
# Fix "### ，" continuation lines (merge into previous line)
sed -z 's|### ，||g' article.md
# Fix standalone ### followed by comma or Chinese text at line start that continues a metadata line
sed -i 's/^### ，//' article.md
```

Also check for the similar pattern in the article header area: `来源：` and `来源：### ` should become `**来源**：` with proper formatting.

### Metadata lines with `\xa0` (non-breaking space)

Some accounts (e.g. 刘润/润米商城) emit metadata lines where WeChat inserted U+00A0 non-breaking spaces, so `观点 / 刘润 主笔 / 二蔓  ### 版面` is actually `观点\xa0/ 刘润\xa0主笔\xa0/ 二蔓 \xa0### 版面\xa0` — and the pattern can contain BOTH a regular space AND `\xa0` adjacent (e.g. `二蔓 \xa0###`). A regex using literal `\xa0*` fails at that spot because `\xa0` does not match the regular space.

**Fix**: use `\s*` everywhere — Python's `\s` matches U+00A0, so it handles mixed space/`\xa0` runs:

```python
m = re.search(r'观点\s*/\s*刘润\s*主笔\s*/\s*二蔓\s*###\s*版面\s*\n\n/\s*黄静', body)
if m:
    body = body.replace(m.group(0), '观点 / 刘润 主笔 / 二蔓 版面 / 黄静')
```

**Detection**: if a metadata fix "silently" fails, print `repr(body[i:i+100])` around the anchor — literal `\xa0` shows up as `\\xa0` in the repr while regular spaces stay visible.

### Bullet-Prefixed ### Artifact (▸ pattern)

The extraction script sometimes mis-tags bold text inside list items prefixed with the Unicode bullet symbol `▸`, producing:

```markdown
▸ ### 3D：
▸ ### 功能一：
▸ ### 规则套改：
```

These should be converted to bold:

```markdown
▸ **3D**：
▸ **功能一**：
▸ **规则套改**：
```

Fix with Python regex:

```python
import re
body = re.sub(r'▸\s*### ([^：]+)：', r'▸ **\1**：', body)
```

**Detection**: `grep -n '###' article.md | grep '▸'` finds all `###` preceded by a Unicode bullet. The general detection check `grep -n '###' article.md | grep -v '^[0-9]*:### '` also catches these since `###` is not at line start.

### Bold-Prefixed Heading Artifacts (`**###` at line start)

Some articles (e.g. 刘润/润米商城) extract with a bold marker directly before a heading: `**### 一家公司：三千亿美金的“咨询公司”`. Strip the leading `**`:

```python
body = re.sub(r'^\*\*### ', '### ', body, flags=re.M)
```

Also convert standalone section numbers `**01**`–`**06**` (bold-only lines) into headings — they pair with the `**###` titles to form the deck's numbered-section structure:

```python
body = re.sub(r'^\*\*(0\d)\*\*$', r'### \1', body, flags=re.M)
```

If a heading was split across two artifacts (`**### 咨询公司：` + blank + `****从一单单的项目，变成长时间的陪伴**`), merge them after stripping: `### 咨询公司：从一单单的项目，变成长时间的陪伴`.

### 润米商城 Promotion Footer

The 润米商城 account appends a promotion block that extracts as scattered `> **`, `> ### 品牌推广 `, `| ### 培训合作 `, `|### 商业咨询 | 润米商城`, `** | 转载开白**`, `> 请在公众号后台回复 ** 合作 **` lines. Collapse the whole block into one footer line:

```markdown
> 品牌推广 / 培训合作 / 商业咨询 / 转载开白，请在公众号后台回复“合作”
```

Keep the trailing 关注公众号 image (`> ![图片]`) and any course-ad images; drop only the pure-decorative gif run between article end and promotion block when it adds nothing.

### `\xa0` Non-Breaking Spaces in Metadata Lines

WeChat metadata lines (e.g. `观点 / 刘润 主笔 / 二蔓  ### 版面 `) can contain U+00A0 non-breaking spaces (`\xa0`) interleaved with regular spaces. A `str.replace` using hand-typed spaces silently does nothing. Always use a regex with `\s*` — Python 3 `\s` matches `\xa0`:

```python
m = re.search(r'观点\s*/\s*刘润\s*主笔\s*/\s*二蔓\s*###\s*版面\s*\n\n/\s*黄静', body)
if m:
    body = body.replace(m.group(0), '观点 / 刘润 主笔 / 二蔓 版面 / 黄静')
```

**Rule**: when fixing metadata/footer lines, prefer `\s*` regex over literal-space `replace()`; if a replace unexpectedly fails, inspect the region with `repr()` — invisible `\xa0` is the usual culprit.

## Ordered List Number-Content Split

The extraction script sometimes converts WeChat `<ol>` / `<li>` structures into a pattern where the list number and its content body end up on separate paragraphs:

```markdown
1.

1000多条已经被SHL OPQ测评过的数据结果及其绩效和晋升信息；

2.

100多条去年制定标准时候的SHL OPQ测评过的数据结果及其绩效和晋升信息；
```

This typically happens when the original HTML uses `<li><p>content</p></li>` — the `<li>` produces the number, the `<p>` produces a separate block.

**Detection**: after extraction, run:

```bash
# Find numbered lines followed by blank line then content
grep -n '^[0-9]\.$' article.md | head -20
```

Or in Python:

```python
import re
# Find patterns like "1.\n\n[non-empty content]"
count = len(re.findall(r'^\d+\.\n\n', body, re.MULTILINE))
print(f"Split numbered items found: {count}")
```

**Fix** — collapse the number onto its content:

```python
import re
# Collapse "1.\n\n    content" to "1. content"
body = re.sub(r'(\d+\.)\n\n\s+', r'\1 ', body)
```

Or in bash with `sed`:

```bash
# Collapse numbered stubs into their content
sed -z 's/\([0-9]\.\)\n\n    /\1 /g' article.md
```

**Edge case**: A numbered bullet `N.` on its own line that is NOT followed by content (but by another `M.` or a heading) is likely a heading-level artifact rather than a list item — leave it alone. Only collapse when the numbered line is followed by `\n\n<content>`.

**Edge case**: Some articles use Chinese-style outline markers like `一.`, `1、`, `（1）`, `一、` that the extraction script also splits. Apply the same fix with adjusted regex:

```python
# Chinese-style outline markers
body = re.sub(r'(一\.|二\.|三\.|四\.|五\.|六\.|七\.|八\.|九\.|十\.)\n\n\s+', r'\1 ', body)
```

### Bold numbered-label fusion `**1.### \n\n 目标**`

When an ordered item is `<li><p><strong>1. 目标</strong>：...</p></li>`, extraction can split the bold label across lines with a `###` in the middle:

```markdown
**1.###  

目标**：最终要解决什么问题；
```

Fix by collapsing the whole run into a clean numbered list (single `re.S` search):

```python
m = re.search(r'\*\*1\.###\s*\n\n目标\*\*：最终要解决什么问题；\n\n\*\*2\.###\s*\n\n背景\*\*：现有系统、材料和用户是谁；\n\n\*\*3\.###\s*\n\n约束\*\*：隐私、安全、技术栈和不能改变的部分；\n\n\*\*4\.###\s*\n\n验收\*\*：哪些测试通过，结果才算完成。', body, re.S)
if m:
    body = body.replace(m.group(0),
        '1. **目标**：最终要解决什么问题；\n2. **背景**：现有系统、材料和用户是谁；\n3. **约束**：隐私、安全、技术栈和不能改变的部分；\n4. **验收**：哪些测试通过，结果才算完成。')
else:
    print('NOT FOUND: four-part block')
```

**Detection**: `grep -n '###' article.md | grep -E '^\*\*[0-9]'` or search for `\*\*[0-9]\.###` — the artifact appears when a bold label was fused with a `###` heading marker.

## Split Number/Percentage Continuation Lines

The extraction script sometimes splits inline text at `<br>` boundaries, producing artifacts where a bold number/percentage and its trailing Chinese punctuation end up on separate paragraphs:

```markdown
更精简的 System Prompt 让评分提高了约 **10%～15%**

，同时将总 Token 减少了 **41%～66%**

，成本降低了 **33%～67%**

。
```

The same pattern can affect blockquote text:

```markdown
> 他目前在 OpenAI 做 **Codex 开发者体验（DX）**

，此前打造过 **RepoPrompt**

，长期折腾的正是代码库上下文
```

A related artifact is a **standalone `。` on its own line** after a plain blockquote sentence (not after bold text, but after a complete Chinese sentence ending inside a blockquote). The extraction splits at `<br>` inside a single blockquote paragraph:

```markdown
> TCL 作为中国企业全球化的先行者……建有47个研发中心与41个制造基地，全球累计用户超13亿

。
```

Detection: after a blockquote line that ends without a period, if the next non-empty line is just `。`, it's a split period that belongs to the blockquote sentence. Also look for `\n\n。` after any `>` line that doesn't already end with `。`.

Fix — merge the standalone period into the preceding blockquote line:

```python
# Blockquote standalone period
body = re.sub(r'(>[^\n]*[^。])\n\n。', r'\1。', body)
```

Or in bash:

```bash
# Fix standalone 。after blockquote
sed -z 's/\(>[^\n]*[^。]\)\n\n。/\1。/g' article.md
```

**Detection**: After extraction, look for lines where a comma `，` or period `。` is the only significant content on an otherwise short standalone line — especially when preceded by a bold number/percentage or a blockquote.

**Fix**: Merge the continuation lines into the preceding paragraph. In Python:

```python
import re
# Merge number continuation lines
body = re.sub(r'(\*\*[0-9%～]+\*\*)\n\n，', r'\1，', body)
body = re.sub(r'(\*\*[0-9%～]+\*\*)\n\n。', r'\1。', body)
# Merge blockquote continuation: find > line \n\n，→ merge
body = re.sub(r'(> [^\n]+)\n\n，', r'\1，', body)
# Blockquote standalone period
body = re.sub(r'(>[^\n]*[^。])\n\n。', r'\1。', body)
```

Or in bash with `sed`:

```bash
# Fix number lines
sed -z 's/\*\*\([0-9%～]*\)\*\*\n\n，/**\1，/g' article.md
# Fix blockquote continuation
sed -z 's/\(>[^\n]*\)\n\n，/\1，/g' article.md
# Fix standalone 。after blockquote
sed -z 's/\(>[^\n]*[^。]\)\n\n。/\1。/g' article.md
```

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

### 润米商城/刘润 promotion footer block

刘润's account ends with a structured promotion block that extracts as broken bold/heading fragments:

```markdown
> **

> ### 品牌推广 

| ### 培训合作 

|###  商业咨询 | 润米商城

** | 转载开白**

> 请在公众号后台回复 ** 合作 **

> **
```

Compress the whole block into a single blockquote line (keeps the info, drops the markup noise):

```markdown
> 品牌推广 / 培训合作 / 商业咨询 / 转载开白，请在公众号后台回复“合作”
```

Find the block start with `body.find('> **\n\n> ### 品牌推广')` and cut to the final `> **\n` line before assembling. Keep any 关注公众号 image that precedes the block.

### Preserved footer convention (卡兹克 and most WeChat accounts)

The extracted footer lines are NOT deleted — they are preserved verbatim at the end of `## 原文`, in this order:

1. `### 以上，既然看到这里了...` — the promotional "点赞/在看/转发" line stays as a `###` heading (that's the established vault convention; do not convert to blockquote).
2. `> / 作者：<author>` — the author line as extracted (fix only the `>/` → `> /` spacing artifact).
3. `> / 投稿或爆料，请联系邮箱：...` — contact line.

Then, after a `---` separator, append the standard archive footer:

```markdown
---

> 来源：<account>（微信公众号）
> 原文链接：<url>
```

Multi-author articles put all names in the author line with `、` (e.g. `卡兹克、tashi`) and in frontmatter `author` as-is. When checking a reference article for convention, use WebDAV GET on an existing file in the same subfolder (e.g. the last archived 卡兹克/codex article) rather than guessing.

## 刘润 / 润米商城 Account Artifacts

Articles from 润米商城 (刘润, e.g. the FDE/consulting piece and the McKinsey 2026 consumer report) repeat the same extraction artifacts. Fix them in one pass:

### Non-breaking spaces in metadata lines

`观点 / 刘润 主笔 / 二蔓  ### 版面 ` uses `\xa0` (U+00A0) mixed with regular spaces. Regex with `\xa0*` FAILS because the line mixes regular spaces and `\xa0`; use `\s*` (Python's `\s` matches `\xa0`):

```python
m = re.search(r'观点\s*/\s*刘润\s*主笔\s*/\s*二蔓\s*###\s*版面\s*\n\n/\s*黄静', body)
body = body.replace(m.group(0), '观点 / 刘润 主笔 / 二蔓 版面 / 黄静')
```

### Standalone bold section numbers

`**01**` … `**06**` on their own lines are section markers, not emphasis:

```python
body = re.sub(r'^\*\*(0\d)\*\*$', r'### \1', body, flags=re.M)
```

### References block split across `###` lines

`1、McMinsey & Company ### State of the Consumer` + `### 2026: When tech` + `### acceleration and cost` + `**pressures collide**` should merge into one clean reference line (also fixes the McKinsey typo):

```python
body = re.sub(r'1、Mc[^\n]*?###\s*State of the Consumer\s*\n\n###\s*2026: When tech\s*\n\n###\s*acceleration and cost\s*\n\n\*\*pressures collide\*\*',
              '1、McKinsey & Company《State of the Consumer 2026: When tech acceleration and cost pressures collide》', body)
```

### 润米商城 promo footer block

The account's footer is a pile of `###`/`|`/`**` artifacts:

```
> ### 品牌推广
| ### 培训合作
|###  商业咨询 | 润米商城
** | 转载开白**
> 请在公众号后台回复 ** 合作 **
```

Collapse to a single line:

```python
m = re.search(r'> ### 品牌推广.*?> 请在公众号后台回复\s*\*\*\s*合作\s*\*\*', body, re.S)
body = body.replace(m.group(0), '> 品牌推广 / 培训合作 / 商业咨询 / 转载开白，请在公众号后台回复“合作”')
```

Keep the trailing decorative footer gifs and the 关注公众号 image as-is — they are part of the original body.

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
