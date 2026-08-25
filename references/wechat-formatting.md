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

⚠️ **Verbatim repeated paragraphs are often ORIGINAL content — verify before "fixing"**: some WeChat articles (e.g. 猎聘人才官's 张一鸣人力成本 piece, 2026-08) genuinely repeat a paragraph word-for-word mid-body (`如今，不少公司都面临预算吃紧的情况。` appeared twice with a slightly expanded second copy — an editorial quirk of the original, not an extraction artifact). Before deleting or merging what looks like a duplicate, grep the raw HTML to confirm the repetition is really there:

```bash
grep -c '如今，不少公司都面临预算吃紧' /tmp/wx_article.html   # 2 = original, keep as-is
```

Only "fix" duplicates when the raw HTML has ONE occurrence (extraction duplicated it); when the raw HTML has N occurrences, preserve all of them in `## 原文`.

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

Variant (fired 2026-08-23 on 《如何通过一场谈话，快速说服对方？》): after the `**###` prefix is stripped, the heading survives as `### 当对方有替代方案，就慎用` and the bolded concept lands on the NEXT line (blank line between) with `****X**` markup (4 asterisks + text + 2): `### 当对方有替代方案，就慎用\n\n****极端锚定法**`. Keep the concept as inline bold INSIDE the heading: `### 当对方有替代方案，就慎用**极端锚定法**`. (Same class as the 咨询公司 case, but the continuation is a single concept term that belongs in the heading, not a full heading subtitle.)

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

### Bare `01` marker with subtitle on the NEXT line (blank line between) — merge, don't leave split

Some accounts (e.g. `猎聘人才官`) emit the numbered section marker and its subtitle as TWO separate paragraphs — `01` alone on a line, blank line, then the subtitle line, then blank line, then body. This differs from the AI组织进化论 `01 ` (trailing-space) case where subtitle follows on the next non-blank line. Fix by merging both into one heading:

```python
for num, title in [('01', '只会省钱，迟早把人也省没了'),
                   ('02', '人力成本的核心，不是总额，而是比例')]:
    old = f'\n{num}\n\n{title}\n'
    new = f'\n### {num} {title}\n'
    if old in body:
        body = body.replace(old, new)
    else:
        print(f'NOT FOUND {num}')
```

Do NOT use `re.sub(r'^(\d{2})\s*$', ...)` first then try to merge — a `### 01`-already-applied body will not match the `\n01\n\n` pattern and the merge silently no-ops. Apply the merge directly against the raw extracted body (bare digits + blank line + subtitle), then verify `### 01 只会省钱` etc. are present and no bare `^\d{2}$` lines remain.

### `1）` / `2）` / `3）` numbered sub-headings → `###` (keep the prefix)

Chinese-paren numbered sub-titles extract as plain lines like `1）人力成本最低线：撑起公司运转的底限`. Convert to `###` keeping the full line (same rule as 第X部分/一、 prefixes — do not drop the number):

```python
body = re.sub(r'^([123]）[^\n]+)$', r'### \1', body, flags=re.M)
```

Verify with `[l for l in body.split('\n') if l.startswith('### 1）')]`.

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

**Generalized fix for extraction output** (the script emits `<td>\n\n### 定岗\n\n</td>` — the `###` lands on its own line inside the cell, so a same-line `sed` misses it). One regex pass handles both `<td>` and `<th>` regardless of line breaks:

```python
body = re.sub(r'(<t[dh]>)\s*###\s*([^<\n]+)', r'\1**\2**', body)
```

This fired on the 物业管理实践 定岗定编 article (2026-08): cells like `<td>### 定岗\n\n</td>` and `<td>### 它要解决什么问题？\n\n</td>` became `<td>**定岗**</td>` etc. Same article also had an inline `###` mid-sentence (`顺序很重要：### 先定岗，再定编，最后定员。` → bold) and a `### 注意\n\n：参考值...` split label — same replace-list treatment as other accounts. Verify afterwards with `grep -n '###' article.md | grep -v '^[0-9]*:### '`.
```

**Generic fix for table cells** (verified 2026-08 on 物业管理实践's 定岗定编 piece, which had `###` inside every `<td>`/`<th>` of its comparison tables — works for both tags in one regex, handles `\n` after the opening tag):

```python
body = re.sub(r'(<t[dh]>)\s*###\s*([^<\n]+)', r'\1**\2**', body)
```

Run this BEFORE any standalone-punctuation or inline-### checks — the `###` inside `<td>### 定岗\n</td>` cells is easy to miss and leaks `###` into the preserved HTML table.
**Python one-pass regex for HTML tables (preferred over many sed calls)**: table-heavy articles (e.g. 物业管理实践's 定岗定编 piece) emit `###` inside EVERY `<td>`/`<th>` cell, often with surrounding blank lines from the cell paragraph structure. One regex fixes all cells regardless of the cell's label text:

```python
import re
body = re.sub(r'(<t[dh]>)\s*###\s*([^<\n]+)', r'\1**\2**', body)
```

Then fix the accompanying label artifacts in the same article:
- `### 注意\n\n：参考值是"体检指标"` → `**注意**：参考值是"体检指标"` (inline-### label + continuation punctuation split on the next line — merge like the `**bold**\n\n，` pattern, but the marker is `###` not `**`)
- bare closing word `结语` on its own line → `### 结语` (same as the `最后的话` / `> 结语` rules — also covers plain-text 结语 lines)
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

**Bulk table-cell fix (generic, one regex)**: articles with Markdown-tabulated content extracted from `<table>` keep HTML table markup, and each `<td>/<th>` cell with a bold label extracts as `### 定岗` / `### 它要解决什么问题？` / `### 第一步：盘点现状`. Fix all table cells at once — do this BEFORE the standalone-inline `###` checks so those labels don't count as false positives:

```python
body = re.sub(r'(<t[dh]>)\s*###\s*([^<\n]+)', r'\1**\2**', body)
```

⚠️ This converts a whole `<table>` cell's bold label; if a cell has `### ` mid-text inside the cell (e.g. `顺序很重要：### 先定岗...` appears OUTSIDE the table), handle that separately as a normal inline-`###`→bold replace. Verified 2026-08 on 物业管理实践's 定岗定编 article (three `<table>` blocks, 9 cell labels, 1 inline occurrence).

**Continuation punctuation split after bold**: after inline `###`→bold fixes, the article may still have `<br>`-split continuations where the punctuation (`"` `。` `，` `：` `；` `——`) sits alone on the next line after a bold phrase:

```markdown
需要配置怎样的**人+AI能力组合**

\"。
```

Merge them with a generic loop (also do this for `**bold**\n\n"`-style splits):

```python
import re
for punct in ['\"', '。', '，', '：', '；', '——']:
    body = re.sub(r'(\*\*[^*\n]{1,80}\*\*)\n\n' + re.escape(punct), r'\1' + punct, body)
body = re.sub(r'\n{3,}', '\n\n', body)
```

Then re-run the standalone-punctuation check (list lines whose stripped content is exactly `"` `。` `，` `：` `；` `——`) to confirm nothing remains.

**`###` label + continuation on next line (物业管理实践 style, 经济账 piece 2026-08)**: the same `<br>`-split appears with a `###` label instead of `**bold**`, and the continuation can be EITHER punctuation or a whole sentence on the next line:

```markdown
### 人工成本是最大的那一块

，通常占项目总成本的一半到三分之二。
### 能源费用是最容易被忽视的"隐形大头"。

以某写字楼项目为例，全年能源费约312万…
四类收入里，### 物业服务费是最大头，也是最容易算错的

。
```

Fix with a generic regex for the punctuation case, plus a replace-list for the sentence-split case (each anchor differs):

```python
# Punctuation continuation: "### X\n\n，" -> "**X**，"
body = re.sub(r'^### ([^\n]{1,60})\n\n(，|。|：|；)', r'**\1**\2', body, flags=re.M)
# Sentence continuation: merge "### X。\n\n以某…" -> "**X**。以某…" (per-instance anchors)
m = re.search(r'### 能源费用是最容易被忽视的"隐形大头"。\n\n以某写字楼项目为例', body)
if m:
    body = body.replace(m.group(0), '**能源费用是最容易被忽视的"隐形大头"**。以某写字楼项目为例')
```

Also in the same 经济账 piece: `四类收入里，### 物业服务费是最大头，也是最容易算错的\n\n。` → `四类收入里，**物业服务费是最大头，也是最容易算错的**。` and `利润的算法很简单：### 收入 - 支出 - 税金 = 利润\n\n。` → `利润的算法很简单：**收入 - 支出 - 税金 = 利润**。` — the `###` mid-sentence becomes bold, and the standalone `。` on the next line merges back into the sentence.

### Mid-sentence inline `###` variant (物业管理实践 实操指南 piece, 2026-08-16)

The companion 实操指南 article (《物业公司定岗定编实操指南》) repeats a slightly different shape: the `###` sits **mid-line** (after `：`/`=`/`≈`), NOT at line start, and the continuation on the next line can be **`。` + a full sentence** (not just the bare punctuation), or plain text (no leading punct):

```markdown
记住几个关键数：### 1200户、15万㎡、4万㎡公区、24部电梯、2个门、600个车位

。后面每个岗位的算法，都绕不开这几个数。
秩序岗合计：7+5+4=### 16人

。如果项目外包了部分秩序（比如夜班外包），扣掉对应人数就行。
这篇我们只拿### 中档普通商品房住宅

做样板，算的是"二级标准"下的编制。
工程岗合计：2+1.5≈### 4人

（含1名综合维修班长）。
```

The line-start regexes in the 经济账 section (`^### ...\n\n(，|。|：|；)`) do NOT fire because the `###` is mid-line. Also some inline `###` appear **with no line break at all** (mid-paragraph emphasis, no split): `...够养半个人了。### 冗余系数不是"多余人头"，是用来对冲年休、病假、培训的。` → bold. Fix with a per-anchor replace-list (assert each is found, print NOT FOUND):

```python
fixes = [
    ('这篇我们只拿### 中档普通商品房住宅\n\n做样板，算的是"二级标准"下的编制。',
     '这篇我们只拿**中档普通商品房住宅**做样板，算的是"二级标准"下的编制。'),
    ('记住几个关键数：### 1200户、15万㎡、4万㎡公区、24部电梯、2个门、600个车位\n\n。后面每个岗位的算法，都绕不开这几个数。',
     '记住几个关键数：**1200户、15万㎡、4万㎡公区、24部电梯、2个门、600个车位**。后面每个岗位的算法，都绕不开这几个数。'),
    ('秩序岗合计：7+5+4=### 16人\n\n。如果项目外包了部分秩序', '秩序岗合计：7+5+4=**16人**。如果项目外包了部分秩序'),
    ('保洁的算法简单：### 人数=保洁面积÷人均保洁面积\n\n。但这里有个大坑', '保洁的算法简单：**人数=保洁面积÷人均保洁面积**。但这里有个大坑'),
    ('这个项目取### 14人\n\n。如果外包一部分', '这个项目取**14人**。如果外包一部分'),
    ('工程岗合计：2+1.5≈### 4人\n\n（含1名综合维修班长）', '工程岗合计：2+1.5≈**4人**（含1名综合维修班长）'),
    ('够养半个人了。### 冗余系数不是"多余人头"', '够养半个人了。**冗余系数不是"多余人头"'),
    ('品质直线下滑。### 人房比只适合住宅', '品质直线下滑。**人房比只适合住宅'),
]
for old, new in fixes:
    if old in body:
        body = body.replace(old, new)
    else:
        print('NOT FOUND:', old[:40])
```

Note the last two are mid-sentence no-break variants — use short unique anchors ending at the `###` so the replace doesn't need the full sentence.

### Callout split `> **一个常见错误**\n\n> ：` (物业管理实践 style)

Both 经济账 and 实操指南 pieces emit the warning callout as a bold label on its own blockquote line, then the content on a SEPARATE blockquote line starting with `：`:

```markdown
> **一个常见错误**

> ：很多人算秩序只算"在岗人数"，不算冗余系数。...
```

Merge into one line (fires on every occurrence, no count needed — the label text is identical across callouts):

```python
body = body.replace('> **一个常见错误**\n\n> ：', '> **一个常见错误**：')
```

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

**Multi-author variant** (润米商城 "AI表演" article): 主笔 can be two names joined with 、 (`景九、歌平`), and the `### 版面` + `\n\n/ 黄静` split still appears:

```python
m = re.search(r'观点\s*/\s*刘润\s*主笔\s*/\s*景九、歌平\s*###\s*版面\s*\n\n/\s*黄静', body)
if m:
    body = body.replace(m.group(0), '观点 / 刘润 · 主笔 / 景九、歌平 · 版面 / 黄静')
```

Also in that same article, the split-heading fusion took the form `**### AI\n\n真正的金矿，不是toC，不是toB，而是"toO"**` — heading text, blank line, then the first body line all inside one bold run ending with `**`. Merge into a single heading line with a targeted regex (the `[“"]` class is required because the quote may be straight or curly):

```python
body = re.sub(r'^### AI\n真正的金矿，不是toC，不是toB，而是[“"]toO[”"]\*\*$', '### AI真正的金矿，不是toC，不是toB，而是“toO”', body, flags=re.M)
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

**Reversed order variant (`### ▸ X：`)**: some accounts (e.g. AI与组织领导力跃迁) emit the bullet AFTER the `###` marker on the same line: `### ▸ 中层以下完全按行业走：`, `### ▸ 方向A：聚焦执行层`, `### ▸ 固薪拉通、浮薪按行业：`. Same fix, reversed regex — capture the full line and keep the trailing colon:

```python
body = re.sub(r'^### ▸ (.+?)(：?)$', lambda m: '▸ **' + m.group(1) + '**' + m.group(2), body, flags=re.M)
```

**Detection**: `grep -n '^### ▸' article.md`.

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

### 刘润重发（repost）文章 artifacts

`刘润商业频道` 和 `润米商城` 常重发旧文。重发版有独特的提取噪声，区别于首发版的 `**01**`/`**###` 系列：

1. **重发提示 banner 断行**：`> **### 本文首发于2022年06\n月****`（banner 里 `###` 与加粗混在一起且日期被 `<br>` 截断）。合并成一行：`> 本文首发于2022年06月`。
2. **重发链接噪声**：`[《](wechat_redirect_url)[不要和没有逻辑的人讨论业务](wechat_redirect_url)[》](wechat_redirect_url)` —— 书名号被拆成三个 `[]()` 包裹同一 URL。压缩为 `《不要和没有逻辑的人讨论业务》`（regex：`\[《\]\(https://[^)]+\)\[TITLE\]\(https://[^)]+\)\[》\]\(https://[^)]+\)`，注意 URL 含 `&`/`#` 但 `[^)]+` 能覆盖）。
3. **未闭合的行尾加粗**：`**祝你拥有结构化的能力……成为真正的高手。\nPS：` —— 加粗在行尾未闭合（原文是 `<br>` 截断）。补上 `**` 闭合。
4. **章节标题在 blockquote 内**：`> **论：结论先行**`、`> **证：以上统下**`、`> **类：归类分组**`、`> **比：逻辑递进**`、`> **没有逻辑的人多可怕**` 等是文章章节标题 → 转 `### 标题`。注意个别标题可能没有 `>` 前缀（如 `**比：逻辑递进**` 裸行）——替换后必须逐个验证 5 个标题都变成 `### `，缺失的单独补。
5. **订阅推广 PS 块**：`**祝你……高手。**\nPS：关注 "刘润商业频道" 获取每日必读……` → 保留加粗结语行，删掉 PS 订阅推广段。
6. **推荐阅读导航块**：`> [推荐阅读：](...)` 到正文结束之间的一组 `[《》(url)]` 链接 + 关注公众号图 + gif → 从 `> [推荐阅读：]` 处截断（删导航，保留正文到「祝你……」结语）。

验证：重发文也跑完整 checklist——5 个 `###` 章节标题齐全、无未闭合 `**`（逐行 `l.count('**') % 2`）、无 `[《](url)` 残留、无孤立 `> **` 装饰行。

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

### Bare numbered headers + separate title line (猎聘人才官/张一鸣 style, 2026-08)

Some articles extract numbered section markers as BARE `01` on its own line, followed by the plain-text title on the NEXT line (no `**` bold, no trailing space — distinct from both the `**01**` bold pattern and AI组织进化论's `01 ` trailing-space pattern):

```markdown
01

只会省钱，迟早把人也省没了
```

Merge number + title into one heading (assert each is found, print NOT FOUND otherwise):

```python
for num, title in [('01', '只会省钱，迟早把人也省没了'),
                   ('02', '人力成本的核心，不是总额，而是比例'),
                   ('03', '管控人力成本，有三条隐形红线')]:
    old = f'\n{num}\n\n{title}\n'
    new = f'\n### {num} {title}\n'
    if old in body:
        body = body.replace(old, new)
    else:
        print('NOT FOUND:', num)
```

Verify afterwards: `re.findall(r'^\d{2}$', body, re.M)` must be empty (no bare numbered lines left).

### Inline `###` inside blockquote lines (书图与手记 style, 2026-08)

Blockquote-heavy articles (书图与手记's 任职资格 series) emit inline `###` inside `>` lines with the continuation punctuation on the NEXT line:

```markdown
> 一个生活化比喻帮你记牢：### 它就像企业内部的"驾照考试"

。
> 一句话总结：它对公司是一套### 识人用人的基础设施

，对员工是一张### 看得见的成长地图
```

Fix inline `###` → bold (replace-list), then run the standard continuation-punctuation merge (`**...**\n\n标点` → `**...**标点`):

```python
fixes = [
    ('：### 它就像企业内部的"驾照考试"', '：**它就像企业内部的"驾照考试"**'),
    ('起到的### "梯子、尺子和镜子"三重作用', '起到的**"梯子、尺子和镜子"三重作用**'),
    ('一套### 识人用人的基础设施', '一套**识人用人的基础设施**'),
    ('一张### 看得见的成长地图', '一张**看得见的成长地图**'),
    ('直接产出是### 能力等级', '直接产出是**能力等级**'),
]
for old, new in fixes:
    if old in body:
        body = body.replace(old, new)
    else:
        print('NOT FOUND:', old[:40])
# then: body = re.sub(r'(\*\*[^*\n]{1,80}\*\*)\n\n' + punct, r'\1' + punct, body) for each punct
```

⚠️ **`> ### ① ...` list-item label inside blockquote → `> **① ...**`** (keep the blockquote, convert `###` to bold): `> ### ① 规范人才培养和选拔` becomes `> **① 规范人才培养和选拔**`. Same for any numbered-label lines `> ② ...` etc. — those are already plain text, keep them.

### 书图与手记 (阿涂) blockquote-table structure

书图与手记's 任职资格 series renders each card as blockquote-wrapped HTML tables: `> <table>\n> <tbody><tr><td>\n\n> 内容...` — the whole table stays inside `>` lines. Preserve as-is (blockquote + HTML table); it reads fine in Obsidian. Also `\u3000` (full-width space) appears between items in table cells (`① ...\u3000② ...`) — replace with a regular space. Series metadata line `任职资格·从0到1｜第01篇/共33篇` at the top of the body is original content — keep it in `## 原文`.

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

### Fused heading+content swallowed by the `N.\n\n` collapse

车厘子's 出海组织观察日记·第二季 (2026-08) emits bold sub-section labels FUSED with their body text on one line — the raw extraction has `匹配一：高不确定性环境 × AI的模式识别能力 出海企业面临的市场环境充满了不确定性—...` (label + full paragraph, no separator). Two steps combine to corrupt it:

1. Heading conversion turns the label prefix into `### 匹配一：...` on the SAME line as the content.
2. The `N.\n\n` list collapse then treats that whole fused line as list item content → `1. ### 匹配一：... 出海企业面临...判断框架。`

Fix — after the collapse pass, split any `N. ### ` line back into heading + paragraph:

```python
m = re.search(r'1\. ### 匹配一：高不确定性环境 × AI的模式识别能力 (出海企业面临[^\n]+判断框架。)', body)
if m:
    body = body.replace(m.group(0), '### 匹配一：高不确定性环境 × AI的模式识别能力\n\n' + m.group(1))
```

Generalized rule: run heading conversion BEFORE the list-number collapse; afterwards scan for lines matching `^\d+\. ### ` and split at the heading/content boundary (per-instance anchors work best since each fused line's boundary differs). Also: a heading-conversion candidate line longer than ~40 chars is usually a fused label+content line — split it (or convert the label to bold instead of `###`) before running the collapse.

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

### Prompt blocks with nested code fences (卡兹克 prompt collections, 2026-08-21)

Long prompts whose text itself contains a literal ```` ```markdown ```` marker (role prompts like 挖掘隐藏天赋 / 人生设计术 in 卡兹克's 12-prompt collection) extract with **broken nested fences** — the inner ```` ```markdown ```` line closes the outer ```` ``` ```` fence, and the rest renders as headings instead of code. The extraction emits 4 fence lines for a block that should have 2, and a naive count looks "balanced" while Obsidian renders it wrong.

**Fix — rebuild with a 4-backtick outer fence** so the inner 3-backtick markers stay literal:

```python
start = body.find('```\n# Role：深度天赋挖掘机')
end = body.find('2. 人生设计术', start)
block = body[start:end]
new_block = block.replace('```\n# Role：深度天赋挖掘机', '````markdown\n# Role：深度天赋挖掘机', 1)
# block ends "...\n```\n```\n\n" -> inner close ``` + outer close, convert LAST to 4-backticks:
m = re.search(r'\n```\n```\n\n$', new_block)
new_block = new_block[:m.start()] + '\n```\n````\n\n'
body = body[:start] + new_block + body[end:]
```

Apply the same pattern to each affected block (find its `start` on ```` ```\n# Role：<name> ````, its `end` on the next section marker). Then verify fence balance with a state-stack parse (each `^```+` line toggles; final stack must be empty) — this catches unclosed fences that a plain `count() % 2 == 0` misses when 4-backtick and 3-backtick fences interleave.

⚠️ Also run `body.count('\xa0')` BEFORE any replace and fix `\xa0`→space AFTER the fence rebuild (the `\xa0` is inside the rebuilt blocks and also precedes inline `###` markers elsewhere — see the HR实名俱乐部 `\xa0###` variant below).

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

### 卡兹克 product-review / tutorial artifacts (DeepSeek Harness piece, 2026-08)

Product-launch reviews from 卡兹克 (e.g. the DeepSeek Harness 速通 piece) repeat these extraction artifacts:

- **Feature-name headings with `，也就是`/`，` continuation**: `### Temporal composability，时间可组合性，也就是\n\n一个插件卸载之后…` → merge to `### Temporal composability（时间可组合性）\n\n一个插件卸载之后…` (English name + Chinese gloss → `（…）`, drop the dangling `，也就是`). Same for `### Spatial composability，空间可组合性，`.
- **Numbered mode names → headings**: `1. 标准模式\n\n` → `### 1. 标准模式` (loop over mode names like 标准模式/PTC模式/极简模式/创造模式).
- **Numbered plugin list with URL + description on separate lines**: `1. dsh-at-file\n\nhttps://github.com/…\n\n装完后…` → `1. **dsh-at-file**：https://github.com/…\n   装完后…` (name → bold, URL inline after `：`, description indented as the item body). Also fix stray inline-code artifacts like `一个持久Bash，一个\`文件编辑器。\`` → `一个持久 Bash、一个文件编辑器。` and `\`但是没事别日常用…\`` → plain text with `……` for `。。。`.
- **Trailing `。` in title**: 卡兹克 titles can end with `。` (e.g. `从0到1带你速通DeepSeek Harness。`) — keep it in the filename, frontmatter, and H1 (matches vault convention `一夜之间，DeepSeek V4 Pro…斩杀线。.md`; full-width punct survives WebDAV fine).
- **Footer**: keep the standard `### 以上，既然看到这里了…` + `> / 作者：卡兹克` + `> / 投稿或爆料…` convention (documented in the section below).

### Nested code fences in prompt-collection articles → 4-backtick outer fence

卡兹克 prompt-collection articles (e.g. 《都Agent时代了，我还是想分享给你这12个我最常用的Prompt。》 2026-08-21) embed prompts whose TEXT itself contains literal ```` ```markdown ```` / ```` ``` ```` markers (the prompt is markdown with an inner code block). The extraction script then emits UNBALANCED nested fences for these blocks:

```
```
# Role：深度天赋挖掘机
## 角色...
## 目标...
```markdown
## 核心理念...
...
## 开始...
```
```
```

The inner ```` ```markdown ```` line closes the outer ```` ``` ```` early and a dangling ```` ``` ```` is left. Fix: rebuild each such block with a 4-backtick outer fence so the inner 3-backtick lines stay literal:

````markdown
# Role：深度天赋挖掘机
## 角色...
## 目标...
```markdown
## 核心理念...
...
## 开始...
```
````

Per-block fix pattern (find `'```\n# Role：<名>'` start, rebuild leading fence to ```` ```markdown ```` and trailing fence to ```` ````). **Verify afterwards with a fence-parse simulation** — walk lines matching `re.match(r'^(```+)(.*)$', line)` toggling a stack (close when `n >= top`), assert final stack empty. In the 12-prompts piece: 10 short prompts were already balanced (20× ```` ``` ````), the 2 long ones needed the 4-backtick rebuild (4× ```` ```` + inner literals) — final counts were 24× 3-backtick (paired) + 4× 4-backtick (paired). Also: the article's numbered sub-headings (`1. 双层解释法` … `2. 人生设计术`) convert to `### 1. …` (same rule as 速通-style mode headings), and `\xa0` appears ~146× from `&nbsp;` in code blocks — replace globally with regular space, then RE-READ the file and confirm count == 0 (a first replace pass can silently not persist if the write cell is skipped — always verify by fresh read, not by trusting the in-memory value).

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

### Generic-account header & cross-promo modules (AI与组织领导力跃迁 / 罗明 style)

Accounts like `AI与组织领导力跃迁` (罗明) emit header boilerplate and tail promo modules that should NOT be preserved in `## 原文`:

- **Header to DROP** (top of body): account name line, slogan (深度思考 · 专业洞察 …), 栏目 label (管 理 洞 察), the duplicate in-body title, and 点击关注公众号 CTA. Keep the subtitle (`—— … ——`) and the author line (`文 / 罗明 · …`).
- **Tail modules to DROP**: 相关文章推荐块 (`欢迎阅读人才管理精选文章` + link list), TOPICS 话题标签行, 商务合作 CTA (`对本次话题感兴趣…`), 关注/转发/留言 CTA (`如果这篇文章对你有启发…`). Keep the final author sign-off (name + 头衔, e.g. `罗明` / `资深管理咨询顾问与企业实践者 · 咨询公司合伙人`).
- **Rationale**: these are navigation/promo, not article content — the H1 and frontmatter already carry title/account; the footer convention above applies to the account's own sign-off lines.

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

### Closing "最后的话" line → heading

刘润/润米商城 articles end with a bare-text closing line `最后的话` (no bold, no heading tag) right before the summary-list of changes. Convert it to a heading so it matches the deck structure and the reference-article convention:

```python
body = body.replace('\n最后的话\n', '\n### 最后的话\n')
```

Verify it converted (`'### 最后的话' in body`); variants may emit `最后的话` with trailing whitespace — fall back to a regex (`re.sub(r'^最后的话\s*$', '### 最后的话', body, flags=re.M)`) if the plain replace misses.

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

## AI与组织领导力跃迁 (罗明) Account Artifacts

Articles from `AI与组织领导力跃迁` (author 罗明, e.g. the 集团薪酬改革 piece) repeat a consistent structure:

### Header block — strip boilerplate, keep subtitle + author line

The extraction emits the account's header banner. Drop these lines, then normalize:

```python
for line in ['AI与组织领导力跃迁\n', '深度思考 · 专业洞察 · 实践落地 · 成长探索\n',
             '管 理 洞 察\n', '点击关注「AI与组织领导力跃迁」公众号，获取持续洞察\n']:
    body = body.replace(line, '')
```

- The in-body H1 title (e.g. `集团薪酬改革，换张表能解决吗？`) often differs slightly from `var msg_title` (`集团型企业的薪酬改革，换张表能解决吗？`). Use msg_title for frontmatter/filename; drop the in-body title from 原文 since the template H1 already carries it.
- Keep the `—— {subtitle} ——` line and the `文 / 罗明    资深管理咨询顾问与企业实践者` author line. Normalize the author whitespace with a regex (the run is mixed spaces/`\u3000`, so literal replace can miss): `re.sub(r'文 / 罗明\s*资深管理咨询顾问与企业实践者', '文 / 罗明 · 资深管理咨询顾问与企业实践者', body)`.
- Also keep (they are content, not boilerplate): the series label line `组织效能系列 · 第N篇` when present, the `> ◆ 本文导读` blockquote, and the closing `**下一篇预告**` line (verified 2026-08-24 on 组织效能系列·第二篇《做好了一件事，还远不够，效能提升需要组织效能魔方》).
- **Series label line is informative — KEEP it** (verified 2026-08-24 on the 组织效能魔方 piece): the account prefixes series articles with `组织效能系列 · 第二篇` (also seen: 组织效能系列 第一篇 referencing 四层根因/冰山). It is NOT boilerplate like the slogan/CTA lines — keep it in 原文 header above the subtitle.

### Body artifacts

```python
# Section numbers WITHOUT bold: "01  两套“薪酬地图”的选择" -> "### 01 两套…"
body = re.sub(r'^(\d{2})\s{1,3}(.+)$', r'### \1 \2', body, flags=re.M)
# Plain-line sub-headings -> ###
for sub in ['第一张地图：一体化逻辑','第二张地图：多套体系逻辑','跨单元调动的薪酬处理策略',
            '两种完全不同的激励哲学','第一步：薪酬治理顶层设计','第二步：薪酬体系重构',
            '第三步：激励机制专项设计','第四步：配套体系补课']:
    body = body.replace('\n'+sub+'\n', '\n### '+sub+'\n')
# Variant (2026-08 激励 piece): sub-headings use 第一个维度/第二个维度/第一个问题/第二个问题 prefixes
for sub in ['第一个维度：薪酬','第二个维度：发展','第三个维度：环境','第四个维度：长期绑定',
            '第一个问题：薪酬构成','第二个问题：薪酬定位','第三个问题：薪酬一致性','第四个问题：薪酬与绩效的挂钩方式']:
    body = body.replace('\n'+sub+'\n', '\n### '+sub+'\n')
# Variant (2026-08-17 销售激励 piece): sub-headings use 成熟业务/增长业务/孵化业务 + 坑一/坑二/坑三 prefixes
for sub in ['成熟业务：高固定 + 过程绩效','增长业务：中低固定 + 高浮动佣金','孵化业务：高固定 + 中长期激励',
            '坑一：新旧方案的过渡没有设计好','坑二：考核指标“能考的都考了”','坑三：兑现节奏与业务节奏不匹配']:
    body = body.replace('\n'+sub+'\n', '\n### '+sub+'\n')
# Variant (2026-08-17 销售激励 piece): sub-headings are business-stage labels + 坑N pitfall labels — verified all 6 fired
for sub in ['成熟业务：高固定 + 过程绩效','增长业务：中低固定 + 高浮动佣金','孵化业务：高固定 + 中长期激励',
            '坑一：新旧方案的过渡没有设计好','坑二：考核指标“能考的都考了”','坑三：兑现节奏与业务节奏不匹配']:
    body = body.replace('\n'+sub+'\n', '\n### '+sub+'\n')
# Decorative separator -> ---
body = body.replace('— · — · — · — · — · — · —', '---')
# "### ▸ 内容：" bullet artifact -> "▸ **内容**："
body = re.sub(r'^### ▸ (.+?)(：?)$', lambda m: '▸ **'+m.group(1)+'**'+m.group(2), body, flags=re.M)
# "如果是### 偏执行角色" inline artifact -> bold
body = body.replace('如果是### 偏执行角色', '如果是**偏执行角色**')
body = body.replace('如果是### 完全利润中心角色', '如果是**完全利润中心角色**')
# Callout label + content on separate blockquotes -> merge into one
body = re.sub(r'(> \*\*♦[^*\n]+\*\*)\n\n(> )', r'\1\n\2', body)
```

### Inline `###` mid-sentence -> bold (with split-continuation merge)

The account bolds concept names inline: `一派主攻「硬」的部分——### 控编制、管薪酬、算人效。` → `**控编制、管薪酬、算人效**。` A two-pass fix works:

```python
# Pass 1: merge continuation when it's PUNCTUATION (，。；、：) — the common case:
#   "第一面是### 战略共识\n\n，解决方向问题" -> "第一面是**战略共识**，解决方向问题"
body = re.sub(r'###\s*([^\n]+?)\n\n([，。；、：])', r'**\1**\2', body)
# Pass 2: general inline ### -> bold for the rest
body = re.sub(r'###\s*([^\n]+)', r'**\1**', body)
```

⚠️ **Continuation can be a WORD, not just punctuation** (verified 2026-08-24 on the 组织效能魔方 piece): `剩下的空间只有靠### 人的能力和技能升级\n\n来打开。` — the `([，。；、：])` class misses `来打开。`, leaving an awkward paragraph split `靠**人的能力和技能升级**\n\n来打开。`. Add a targeted merge for known splits (or a general `re.sub(r'\*\*([^*\n]+?)\*\*\n\n(来|以|再|才|就|从|这)', ...)` pass). Real case: `body.replace('靠**人的能力和技能升级**\n\n来打开。', '靠**人的能力和技能升级**来打开。')`.

Also: run inline-###→bold BEFORE the section-number→`###` regex (`^(\d{2})\s{1,3}(.+)$` → `### \1 \2`), otherwise the bold pass converts the freshly-made `### 01 标题` headings into bold lines.

Callout labels are `> **♦ 现象**` / `> **♦ 洞察**` / `> **♦ 关键判断**` / `> **♦ 实践心得**` with content on `>  …` lines; merging keeps each callout a single blockquote. `🔍 …` question lines and `▲ 图N · caption` caption lines are body content — keep them.

**Generic inline-`###` cleanup (组织效能系列 pieces, verified 2026-08-24)**: essays like 《做好了一件事，还远不够，效能提升需要组织效能魔方》 have inline `###` scattered through prose (`——### 控编制、管薪酬、算人效。`, `第一面是### 战略共识`, `### 六面合在一起，才是一个从诊断到落地…的完整闭环。`) that a specific replace-list can't cover. Use a generic pass. ⚠️ **ORDER MATTERS: run the generic inline-`###`→bold regex BEFORE the `^(\d{2})\s{1,3}(.+)$` → `### NN` heading regex.** If bold runs after, `###\s*([^\n]+)` matches the just-created `### 01 组织效能…` headings and flattens them into `**01 组织效能…**` paragraphs. Sequence:

```python
body = re.sub(r'###\s*([^\n]+?)\n\n([，。；、：])', r'**\1**\2', body)  # merge split continuation punct FIRST
body = re.sub(r'###\s*([^\n]+)', r'**\1**', body)                       # then generic inline ### -> bold
body = re.sub(r'^(\d{2})\s{1,3}(.+)$', r'### \1 \2', body, flags=re.M)  # section numbers LAST
```

Non-punctuation continuations need a manual merge: `靠### 人的能力和技能升级\n\n来打开。` → `靠**人的能力和技能升级**来打开。` — after the generic pass, scan each former inline-### spot for an orphaned continuation word/`——` on the following line and splice it back. Then re-run the standard checklist (no inline `###` at line start, no standalone `###` lines).

Optional image-alt improvement: the caption follows each image, so `![image](url)` + `▲ 图N · cap` can become `![图N · cap](url)` in one regex pass:

```python
body = re.sub(r'!\[image\]\((https://[^)\s]+)\)\n\n▲ 图(\d+) · ([^\n]+)',
              r'![图\2 · \3](\1)\n\n▲ 图\2 · \3', body)
```

### Footer blocks to drop (keep author sign-off)

- `欢迎阅读相关精选文章` / `欢迎阅读组织与人才管理精选文章` / `欢迎阅读人才管理精选文章` + the related-article link list (pure cross-promo navigation) — ⚠️ **the promo header VARIES by article** (verified 2026-08: 激励 piece used `欢迎阅读相关精选文章`, 领导力发展 piece used `欢迎阅读人才管理精选文章`). Search for the first of the three variants, or just search for the common substring `欢迎阅读` and cut there:
- `TOPICS` + hashtag line
- `对本次话题感兴趣，希望进一步讨论或商务合作…` (business CTA)
- `如果这篇文章对你有启发，欢迎：关注/转发/留言…` (follow CTA)

Keep the trailing sign-off lines (`罗明` / `资深管理咨询顾问与企业实践者 · 咨询公司合伙人`) — they are the preserved author footer.

⚠️ **The sign-off sits AFTER all promo blocks in extraction order.** Cutting the tail at `欢迎阅读` with `body = body[:tail_start].rstrip()` silently deletes the sign-off too (verified 2026-08 on 领导力发展 article). Re-append it after the cut:

```python
tail_start = body.find('欢迎阅读')   # first promo header — varies between posts
if tail_start != -1:
    body = body[:tail_start].rstrip() + '\n'
if '罗明\n\n资深管理咨询顾问' not in body:   # sign-off was cut with the promos
    body = body.rstrip() + '\n\n罗明\n\n资深管理咨询顾问与企业实践者 · 咨询公司合伙人\n'
```

⚠️ **Tail-cut trap (fired 2026-08 on the 领导力发展 piece)**: cutting at `body.find('欢迎阅读')` with `body = body[:tail_start].rstrip()` removes EVERYTHING after that marker — including the 罗明 sign-off that must be preserved. The sign-off comes AFTER the promo block, so after the cut you must re-append it:

```python
tail_start = body.find('欢迎阅读')   # first promo header — varies between posts
if tail_start != -1:
    body = body[:tail_start].rstrip()
    body += '\n\n罗明\n\n资深管理咨询顾问与企业实践者 · 咨询公司合伙人\n'
```

Verify the sign-off landed in the tail (`body.rstrip().endswith('合伙人')`); the author line at the head also contains `罗明` so a plain `'罗明' in body` check is not sufficient.

⚠️ **The sign-off sits AFTER the promo block in extraction order** (verified 2026-08 on the 领导力发展 piece). Body order is: …正文 → `🔍 …` question → `欢迎阅读…` promo + link list → `TOPICS` → business CTA → follow CTA → `罗明` → title line. A naive `body[:body.find('欢迎阅读')]` cut deletes the sign-off too. Fix: cut the promo, then re-append the two sign-off lines:

```python
tail_start = body.find('欢迎阅读')   # first promo header — varies between posts
if tail_start != -1:
    body = body[:tail_start].rstrip() + '\n'
body = body.rstrip() + '\n\n罗明\n\n资深管理咨询顾问与企业实践者 · 咨询公司合伙人\n'
```

## 卡兹克 速通-style Tutorial Artifacts (numbered modes + plugin lists)

卡兹克's "从0到1速通X" tutorials (verified 2026-08 on DeepSeek Harness) repeat two extraction patterns:

### Numbered mode headings `1. 标准模式\n\n` → `### 1. 标准模式`

```python
for m in ['标准模式', 'PTC模式', '极简模式', '创造模式']:
    body = re.sub(r'^(\d)\. (' + m + ')\n\n', r'### \1. ' + m + r'\n\n', body, flags=re.M)
```

### Plugin lists split across paragraphs → collapse to numbered list with URL + indented description

`N. name\n\nhttps://github.com/...\n\n描述` extracts as three separate paragraphs. Collapse each into `N. **name**：url` + indented description so the list stays a real list:

```python
plugin_fixes = [
    ('1. dsh-at-file\n\nhttps://github.com/omdsh-dev/dsh-at-file\n\n装完后直接在输入框@就可以调用文件了，很方便。',
     '1. **dsh-at-file**：https://github.com/omdsh-dev/dsh-at-file\n   装完后直接在输入框 @ 就可以调用文件了，很方便。'),
    # ... one entry per plugin
]
for old, new in plugin_fixes:
    if old in body:
        body = body.replace(old, new)
    else:
        print("NOT FOUND:", old[:40])
```

### Inline feature-name artifacts `### Temporal composability，时间可组合性，也就是\n\n` 

Bold concept names inside a numbered explanation extract as `### 名称，中文名，也就是` + continuation. Merge to a clean `### 名称（中文名）` heading and drop the dangling `也就是`:

```python
body = body.replace('### Temporal composability，时间可组合性，也就是\n\n一个插件卸载之后，它之前产生的副作用能不能完整撤销。',
                    '### Temporal composability（时间可组合性）\n\n一个插件卸载之后，它之前产生的副作用能不能完整撤销。')
```

### Stray inline-code backticks around Chinese

`一个持久Bash，一个`文件编辑器。`` and `` `但是没事别日常用…` `` — WeChat bold/quote around CJK extracts with misplaced backticks; strip them:

```python
body = body.replace('一个持久Bash，一个`文件编辑器。`', '一个持久 Bash、一个文件编辑器。')
body = body.replace('`但是没事别日常用，你会发现根本没法用。。。`', '但是没事别日常用，你会发现根本没法用……')
```

## 赛普咨询 (赛普研究院) Account Artifacts

Articles from `赛普咨询` (author 李欣禹, e.g. 房地产AI全场景实战 piece 2026-08) repeat a distinctive structure worth normalizing:

### Header/title artifacts

- `> **引言**` blockquote heading → convert to `## 引言` (plain `##`, not blockquote).
- Scattered multi-line titles: `AI 3E价值模型：\n\n效率、\n\n效益、效能` → merge to one `## AI 3E价值模型：效率、效益、效能`.
- Split bold section titles: `**房地产企业AI全景规划及**\n\n**行业标杆实践**` → `## 房地产企业AI全景规划及行业标杆实践`; `三个具象化场景，\n\n不同AI工作链` → `## 三个具象化场景，不同AI工作链`.

### Numbered sub-headings → `###`

```python
body = re.sub(r'^(\d)\.([^\n]{5,60})$', r'### \1.\2', body, flags=re.M)   # "1.效率：..." -> "### 1.效率：..."
body = re.sub(r'^(场景[一二三]：[^\n]{5,80})$', r'### \1', body, flags=re.M)  # "场景一：..." -> "### 场景一：..."
```

- `**结  语**` (bold with full-width space) → `## 结语`.

### Tail — cut survey promo, keep author line

The article ends with a survey CTA (`为进一步了解企业与个人用户对AI的使用频率…` + questionnaire image + 期待反馈…) followed by the author line (`作者：李欣禹；来源：赛普研究院。`) and a hotline ad (`赛普咨询全国统一热线：400-9669-209`). Cut from the survey marker; the author line is BELOW the cut point (same trap as 罗明 sign-off) so re-append it:

```python
tail = body.find('为进一步了解企业与个人用户对AI的使用频率')
if tail != -1:
    body = body[:tail].rstrip() + '\n\n作者：李欣禹；来源：赛普研究院。\n'
```

Heading convention matches AI知识 folder: main sections `##`, sub-sections `###`.

## 首席组织官 Account Artifacts

Articles from `首席组织官` (e.g. 十大组织系统 2026年8月版) repeat a distinctive numbered-section structure: each system is `> **01**` + `**系统名**` + `### 功能：` + `### 典型子系统：` (bold labels), with category headers like `** 任务协同类系统 **`.

### Header artifact

```python
# "*### 正文字数：4800字\n\n*" — drop the word-count banner
body = body.replace('*### 正文字数：4800字\n\n*\n', '')
```

### Inline ### mid-prose → bold

```python
body = body.replace('### 不仅能看到表层的“人”，还能看到底层的“系统”，\n\n从而',
                    '**不仅能看到表层的“人”，还能看到底层的“系统”**，从而')
```

### Numbered sections: `> **01**` + `**title**` + `### 功能：` → `### 01 title` + `**功能**：`

⚠️ **The fix_section replacement MUST return a trailing `\n\n`.** Without it, the heading fuses with the next label: `### 01 核心业务流程/机制**功能**：` (heading + label glued on one line). Real case fired 2026-08 on the 十大组织系统 piece — first draft produced fused headings for all 10 sections.

```python
def fix_section(m):
    return f'### {m.group(1)} {m.group(2)}\n\n'   # ← the \n\n is essential
body = re.sub(r'> \*\*(\d{2})\*\*\n\n\*\*([^*\n]+)\*\*\n\n', fix_section, body)
body = body.replace('### 功能：', '**功能**：')
body = body.replace('### 典型子系统：', '**典型子系统**：')
```

### Category headers `** 任务协同类系统 **` → `### 任务协同类系统`

```python
for cat in ['任务协同类系统', '人才及知识类系统', '激励及文化类系统', '战略及变革类系统']:
    body = re.sub(r'\*\*\s*' + cat + r'\s*\*\*', '### ' + cat, body)
```

### Tail promo — drop

Cut at `*### #首席组织官` (drops the mission statement + hashtag line):

```python
tail_start = body.find('*### #首席组织官')
if tail_start != -1:
    body = body[:tail_start].rstrip() + '\n'
```

**Verification**: after cleanup, `len(re.findall(r'^### \d{2} ', body, re.M)) == 10` and `body.count('**功能**：') == 10` / `body.count('**典型子系统**：') == 10`.

## 高绩效HR Account Artifacts

Articles from `高绩效HR` (e.g. HRBP成长顺序文章、70页PPT课件) repeat a consistent promo layout that should NOT be preserved in full:

### Header banner — drop entirely

Every article opens with an ad banner: `**超级会员年卡**` / `扫码回复"福利"领资料` / `[了解](...)` / `企业定制内训欢迎联系` / `梁老师 15018431136（微信同号）` plus promo images. This is pure promotion, not article content. Drop the whole banner up to the first real sentence (e.g. `想成为合格的业务伙伴...` or `来源：木先生iPPT`).

```python
banner_start = body.find('![image](https://mmbiz.qpic.cn/mmbiz_jpg/N5hX4ywNBk9EQkXYNOhvAesgzCXB8FJ9MYQ7NFTqLYictNGicFoP1ScF2IrWlczlqY4GusdPA8lj0W4E5CMXS9DA/640?wx_fmt=jpeg&from=appmsg)')
banner_end = body.find('想成为合格的业务伙伴')
if banner_start != -1 and banner_end != -1:
    body = body[:banner_start] + body[banner_end:]
```

### Tail course-promotion block — compress to one line

The article ends with a large training-camp ad: `> **《...实战训练营》**` + 课程收益/大纲/讲师简介 + 报名二维码 + `长按二维码或点击"阅读原文"报名课程` + `*以上内容包含广告`. For prose articles, cut everything after the real closing line (e.g. `欢迎在评论区聊聊你的看法。`) and replace with one compressed line:

```markdown
> （文末为《业务为基：战略HRBP实战训练营》课程推广：9月4-5日上海，4680元/人，含课程收益、大纲与讲师简介，已省略）
```

For slide-deck articles (70页PPT), the trailing ad slides (出海课程/线上课程/内训主题) are kept as images but flagged:

```markdown
> **注**：以下为文末课程推广页（出海人力资源管理GLOBAL模型实战强化班、线上课程系列、高绩效HR精品内训主题），非课件正文。
```

### Inline `###` artifacts

Extraction produces inline `###` noise specific to this account:

```python
# "至关重要：### 先懂业务，再懂人，最后才是用专业解决问题\n\n。" → bold
body = body.replace('：### 先懂业务，再懂人，最后才是用专业解决问题\n\n。', '：**先懂业务，再懂人，最后才是用专业解决问题**。')
# "长按二维码或点击"### 阅读原文" → bold
body = body.replace('长按二维码或点击"### 阅读原文', '长按二维码或点击"**阅读原文**')
```

### General: inline-`###` regex must LOOP until stable

A single `re.sub(r'###\s+([^\n]+?)\s*\n\n([^\n]*)', …)` pass is NOT enough for accounts with heavy inline `###` noise (高绩效HR, 卡兹克, 书图与手记…). group2 `[^\n]*` greedily eats the rest of the continuation line, swallowing any later `### X` marker on that same line (`### 4月至9月\n\n推进，…未来### 3～5年\n\n的发展…` → the `### 3～5年` survives as literal text). The survivors sit at end-of-line, so loop until stable:

```python
while True:
    new = re.sub(r'###\s+([^\n]+?)\s*\n\n([^\n]*)',
                 lambda m: f"**{m.group(1).strip()}**{m.group(2)}", body)
    if new == body:
        break
    body = new
```

Then assert no non-heading `###` lines remain: `re.findall(r'^.*###.*$', body, re.M)` should only list legit `### `/`#### ` headings.

Also: list-label merge colon check must strip `**` first — `'**问题一：**'.endswith('：')` is False (ends in `**`); use `label.strip('*').endswith('：')` to avoid a second colon.

## 麦肯锡 Account Artifacts

Articles from `麦肯锡` (e.g. 智能体商业的演进曲线 piece, 2026-08-21) repeat these extraction artifacts — distinct from the 高绩效HR promo-banner pattern:

### Blockquote section headers → `###`

Top-level sections extract as blockquotes: `> 智能体商业的自动化曲线：六级演变`, `> 自动化发展曲线如何延伸？`, `> 智能体商业中，价值池如何变迁？` → strip `> ` to `### 标题`.

### Level headings split across TWO bold lines → merge to `###`

Each automation level is `**0级：程序化便利**` on one line + `**（"傻瓜式设置"）**` on the NEXT line (parenthetical subtitle). Merge to one heading: `### 0级：程序化便利（"傻瓜式设置"）`. Applies to all six levels; the 5级 subtitle uses full-width parens `（多智能体协同）`. Also bold category headers `**委托比例加速增加的购物类型：**` → `### 委托比例加速增加的购物类型：`.

### Author block `###` noise → bold inside blockquote

`> ### Deepa Mahajan\n\n、### Hannah Mayer\n\n和### Roger Roberts\n\n是麦肯锡全球董事合伙人…` → merge into `> **Deepa Mahajan**、**Hannah Mayer**和**Roger Roberts**是麦肯锡全球董事合伙人，常驻湾区分公司；…`. Also drop stray `> **\n> **` decoration lines after `> **作者介绍：**`.

### Tail promo — cut, keep author lines

Cut from the gif image right before `欢迎关注麦肯锡中国` through the end (公众号/视频号 channel lists, 业务咨询/媒体垂询 emails, 版权声明). Keep `> **作者介绍：**` + the 感谢 line above the cut.

## Misc Extraction Artifacts (HR实名俱乐部 style, 2026-08)

- **`\xa0###` inline concept names (Builder/FDE piece, 2026-08-21)**: bold concept names mid-sentence extract as `\xa0### Name` (U+00A0 BEFORE the `###`) with the continuation punctuation on the NEXT line: `未来更像\xa0### Builder\n\n，而不是\xa0### FDE\n\n。`. A literal-space `replace()` silently no-ops — use `\s*` regex (Python `\s` matches `\xa0`):
  ```python
  body = re.sub(r'未来更像\s*### Builder\s*\n\n，而不是\s*### FDE\s*\n\n。', '未来更像**Builder**，而不是**FDE**。', body)
  body = re.sub(r'本质是### "创造"\s*\n\n；', '本质是**"创造"**；', body)
  body = re.sub(r'HR 转型\s*### Builder\s*\n\n，不是跨界', 'HR 转型**Builder**，不是跨界', body)
  ```
  Detection: `grep -n '###' article.md | grep -v '^[0-9]*:### '` catches them; the `\xa0` shows up as a visible space in terminal output so repr() the region to confirm.
- **Tail promo marker variants**: the 线下活动 promo block opens with EITHER `✅最新AI线下活动日程` OR `【最近线下活动】` (both followed by 城市+日期 lines + `✅ 扫码报名`/`扫码咨询` + QR image) — cut from whichever marker appears; the `> 文章链接` recommendation list above it is KEPT.

- **Em-dash `——` → `---- ` (four ASCII hyphens + space)**: some accounts (HR实名俱乐部 周鸿祎 piece) emit `AI 时代不一样了 ---- 技术迭代按周算` where the original is `——`. Fix with a plain replace: `body = body.replace(' ---- ', '——')` (check the exact spacing variant before replacing; assert the anchor was found).
- **Trailing punctuation run `。，、` at sentence end**: the closing sentence can extract with glued noise (`技术不断向前，人与人的真诚链接却永远珍贵。，、` — original ends at `。`). Fix: `body = body.replace('。，、', '。')`. Run the standalone-punct check afterwards to confirm no stray punctuation lines remain.

### 大厂AI native实践类文章 (淘天集团 piece, 2026-08-19)

HR实名俱乐部's 大厂AI组织实践报道 (e.g. 《淘天集团：AI native团队的构想与实践》) repeats these artifacts — distinct from the 周鸿祎 piece's `---- `/`。，、` noise:

- **Inline `###` mid-sentence bold concepts**: concept names bolded mid-paragraph extract as `### X` → convert to `**X**` with a replace-list. Real anchors from the 淘天 piece: `但### 人均需求交付数没涨、交付周期没缩短`, `书牧把所有业务切成两侧：### 消费侧`, `；### 生产侧`, `答案一直是### 人`, `> ### AI辅助` / `> ### AI Native` (inside blockquotes), `WorkBuddy这样的### 通用助手`, `真正的硬骨头是### 存量业务`, `几乎### 对着书牧的"三道坎"逐一作答`, `三类结构化知识——### pitfall（踩坑与修复）、decision（方案选型）、faq（高频问答）`, `隐性经验＝### 特定场景＋边缘情况＋官方文档不会涵盖`.
- **Bold continuation split**: after converting to bold, the continuation (`。` `，` `——` or a whole clause) sits in the NEXT paragraph — merge with a per-anchor list, e.g. `**消费侧**\n\n直接面向人…；**生产侧**\n\n则完全…` → one merged sentence; `答案一直是**人**\n\n。` → `答案一直是**人**。`; `> **AI辅助**\n\n：` → `> **AI辅助**：`.
- **Section titles** `一、…五、` + `写在最后` → `###` (standard `^([一二三四五]、[^\n]+)$` / `^(写在最后)$` regex).
- **Sub-headings** `1. 从超级个体到超级团队` / `2. 信号驱动：…` / `3. 云端统一下发…` / `### 4.小结` → normalize all to `### N. …` (make `4.小结` → `4. 小结` for consistency).
- **Tail promo to drop**: the `✅最新AI线下活动日程` block (dates `8-22上海，8-23深圳，8-29北京` + `扫码咨询，备注：城市+AI活动` + QR image) is a course-promo — cut from that marker to end.
- **KEEP the `> 文章链接` recommendation list** (美团AI转型经验 / 快手三年经验复盘 links) — it sits ABOVE the promo and matches vault convention for this account; cut at `✅`, not at `文章链接`.

## TRAE.ai Account Artifacts

Articles from `TRAE.ai` (author TRAE, 字节 AI 编程产品官方号; `var nickname = htmlDecode("TRAE.ai")`, extraction `account` = `Trae-Real AI Engineer`, e.g. 《咨询行业实战指南｜用好 TraeWork，海量信息高效分析》 2026-08-23) repeat a distinctive structure worth normalizing — tool-guide with 5 consulting scenarios, each with 如何做 numbered steps + Prompt 示例 blockquote + 小技巧 callout.

### Carousel captions — drop

`左右滑动查看更多精彩内容` appears between image groups (swipe hint, not content) — drop all occurrences:

```python
body = re.sub(r'^左右滑动查看更多精彩内容\n\n', '', body, flags=re.M)
```

### Blockquote plugin list `> 1.\n\n> ### Name\n\n：desc` → `> N. **Name**：desc`

Official plugin intros extract as `> 1.` + `> ### 行业全景研究` + plain-text `：适合...` on separate lines. Merge to one blockquote line; if the source numbering restarts (1,2 / 1,2,3), renumber sequentially (1–5 in the TraeWork piece):

```python
body = re.sub(r'> (\d+)\.\n\n> ### ([^\n]+)\n\n：([^\n]+)', r'> \1. **\2**：\3', body)
```

### Bold scenario headers → `###`

`**场景一：行业与竞品研究**` (一/二/三/四/五) standalone bold → `### 场景一：...`; same for `**更多技巧介绍**` → `### 更多技巧介绍`.

### `###` heading + `：` continuation split

`### 使用流程也很简单\n\n：先在插件市场...` — strip the dangling `：` (the heading already ends with 简单, the colon belongs to the sentence):

```python
body = re.sub(r'(### 使用流程也很简单)\n\n：', r'\1\n\n', body)
```

### Numbered steps split

`1.\n\n搭建研究框架：...` → `1. 搭建研究框架：...`. The `(?![>\n])` guard keeps blockquote lines untouched:

```python
body = re.sub(r'^(\d+)\.\n\n(?![>\n])', r'\1. ', body, flags=re.M)
```

### ⚠️ ORDER: fix 更多技巧 numbered items BEFORE the generic numbered-collapse

The 更多技巧 items extract as `1.\n\n### 先确定分析框架，再展开内容\n\n。建议先...` (number, blank, `###` title, blank, `。` continuation). If the generic `^(\d+)\.\n\n` collapse runs FIRST, they become `1. ### 先确定...` and the `\n\n###` pattern no longer matches — the replace silently no-ops (fired 2026-08-23 on the TraeWork piece; required a second pass with the post-collapse pattern). Fix either BEFORE the collapse:

```python
body = re.sub(r'^(\d+)\.\n\n### (.+)\n\n。', r'\1. **\2**。', body, flags=re.M)
```

or AFTER the collapse with the fused form:

```python
body = re.sub(r'^(\d+)\. ### (.+)\n\n。', r'\1. **\2**。', body, flags=re.M)
```

Also inside item 3: `### 移动端\n\n：适合碎片化...` → `**移动端**：适合碎片化...` and `### 网页端 / 桌面端\n\n：` → `**网页端 / 桌面端**：` (inline `###` → bold, drop the `\n\n：` split).

### Inline `###` mid-sentence → bold + merge

`增加### 「用户标签」「访谈状态」「文档链接」「访谈负责人」\n\n等字段` → `增加**「用户标签」「访谈状态」「文档链接」「访谈负责人」**等字段`; `点击### 阅读原文\n\n，探索` → `点击**阅读原文**，探索`.

### Blockquote `> ### 小技巧\n\n：` → `> **小技巧**：`

Every scenario's tip callout extracts as `> ### 小技巧` + `：...` — merge into one blockquote line:

```python
body = re.sub(r'> ### 小技巧\n\n：', '> **小技巧**：', body)
```

### 润米商城 tail marker: 第NNNN篇原创文章

刘润/润米商城 articles end with `这是刘润公众号第{NNNN}篇原创文章。` + 未经授权禁止抓取 line, then 关注公众号 image (`> ![图片]`), a decorative gif run + linked banner, then the promo block (`> ### 品牌推广 ... 请在公众号后台回复 合作`). Cut at the 第NNNN篇 marker, keep the 关注公众号 image, DROP the decorative gif/linked-banner run, collapse the promo block to one line:

```python
tail_marker = '这是刘润公众号第3040篇原创文章。'   # NNNN varies per article
idx = body.find(tail_marker)
if idx != -1:
    core = body[:idx].rstrip() + '\n\n' + tail_marker + '\n'
    after = body[idx+len(tail_marker):]
    m_img = re.search(r'\n\n(> !\[图片\]\(https://[^)]+\))\n\n', after)   # 关注公众号 image
    m_promo = re.search(r'> ### 品牌推广.*?请在公众号后台回复\s*\*\*\s*合作\s*\*\*', body, re.S)
    if m_img and m_promo:
        body = core + '\n' + m_img.group(1) + '\n\n' + '> 品牌推广 / 培训合作 / 商业咨询 / 转载开白，请在公众号后台回复“合作”' + '\n'
```

Also: a section heading can be followed by a bolded term on the next line (`### 当对方有替代方案，就慎用\n\n****极端锚定法**` — 4-asterisk artifact) — merge as `### 当对方有替代方案，就慎用**极端锚定法**` (heading + bold term, keep the bold).

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
