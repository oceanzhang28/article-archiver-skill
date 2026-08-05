# 文章归档 Skill

这是一个用于把公众号文章、网页文章、飞书文档、截图/聊天记录等内容归档到 Obsidian 知识库的 Codex Skill。

它的核心目标不是“把文章总结一下”，而是把原文完整保存下来，同时在正文前补充可检索、可复用的阅读笔记，并维护对应知识库入口页。

## 主要功能

- 归档微信公众号文章、普通网页文章、长文本、Excel/CSV 批量链接。
- 保留完整原文，不用摘要替代正文。
- 在原文前生成固定笔记结构：
  - `摘要`
  - `核心要点`
  - `这篇解决什么问题`
  - `快速判断`
  - `原文`
- 按知识库分类自动落入对应 Obsidian 文件夹。
- 更新对应入口页的主题分类和全部文章索引。
- 支持截图、聊天记录、课程分享记录的 OCR 归档。
- 支持飞书文档通过 `lark-cli` 抓取后归档到 Obsidian。
- 支持显式 opt-in 的“知识卡片”格式。

## 当前支持的知识库分类

| 分类 | 文件夹 | 入口页 |
| --- | --- | --- |
| HR知识 | `00知识库/HR知识/` | `00知识库/HR知识入口.md` |
| AI知识 | `00知识库/AI知识/` | `00知识库/AI知识入口.md` |
| 商业知识 | `00知识库/商业知识/` | `00知识库/商业知识入口.md` |
| 卡兹克 | `00知识库/卡兹克/` | `00知识库/卡兹克入口.md` |

其中卡兹克文章按作者优先归入 `卡兹克` 集合，再按主题进入 `AI资讯`、`claude code`、`codex`、`prompt`、`skills`、`workbuddy` 等子目录。

## 公众号账号分类

Skill 支持按微信公众号账号优先分类，而不是只看文章主题。

账号到目录的映射见：

```text
references/classification-by-account.md
```

例如：

- `数字生命卡兹克` → `00知识库/卡兹克/`
- `HR实名俱乐部`、`高绩效HR` → `00知识库/HR知识/`
- `润米商城` / 刘润商业分析类文章 → `00知识库/商业知识/`

如果账号没有明确映射，再按文章主题判断。

## 微信公众号格式处理

微信公众号文章直接抽纯文本很容易丢格式。这个 skill 要求先提取 HTML，再转换为 Markdown，以尽量保留：

- 段落和换行
- 引用/卡片模块
- 图片位置
- 列表、表格、代码块
- 加粗标题和正文层级

相关规则见：

```text
references/wechat-extraction.md
references/wechat-formatting.md
references/extraction-script.py
```

已经纳入的微信提取增强包括：

- 遇到验证码/环境异常时优先尝试移动端 UA。
- 支持 `var nickname = htmlDecode("...")` 形式的公众号名提取。
- 支持 `<meta name="author">` 作为账号和作者兜底。
- 支持 `content_noencode` 作为正文 HTML 兜底来源。
- 针对刘润/润米商城、高绩效HR、卡兹克等账号的常见格式异常做了专项处理说明。

## 幻灯片型文章

有些微信公众号文章本质是 PPT 图集，正文主要藏在图片里。此类文章不能只保存一串图片链接。

处理规则见：

```text
references/slide-articles.md
```

核心要求：

- 保留所有关键图片链接。
- 如果页面提取出的文字框架很薄，要对幻灯片图片做 OCR。
- 摘要和核心要点必须来自 OCR 后可验证的内容，不能凭标题猜。

## 截图和聊天记录 OCR

当用户提供截图、聊天记录、课程分享截图时，如果视觉模型不可用或失败，可以使用 OCR 兜底。

处理规则见：

```text
references/ocr-fallback.md
```

归档时需要重建消息流、清理 OCR 噪声，并按内容主题放入对应知识库。

## 飞书文档归档

当用户提供飞书文档链接时，skill 使用 `lark-cli` 获取 Markdown 内容，再写入 Obsidian。

这类内容通常是工作文档，不默认套用公众号文章的摘要模板；应保留原始文档结构，并加上必要的 YAML 属性。

## 知识卡片

知识卡片是显式 opt-in 格式。只有用户明确说“知识卡片”、要求“卡片格式”，或指定 `card_tag` 时才使用。

默认的“转存 / 保存 / 归档文章”请求都应该使用完整文章归档格式，保留 `## 原文`。

知识卡片规则见：

```text
references/knowledge-card-format.md
```

## Hermes 和 WebDAV 注意事项

Hermes 部署中 Obsidian 通常挂载在：

```text
/mnt/obsidian/
```

坚果云 WebDAV/FUSE 场景有一些容易踩坑的地方：

- FUSE 挂载写入可能看似成功但没有持久化。
- WebDAV PUT 后，本地 FUSE 缓存可能是旧内容。
- 入口页编辑必须用 WebDAV GET 读回确认。
- 不能在执行环境里用 `curl -T /dev/stdin` 上传入口页，可能会把文件清空。
- 入口页可能存在 `<mark class="conflict">` 冲突标记，日常归档时不要顺手清理。
- 编辑入口页时优先用 split-at-index / 位置插入策略，避免 `replace()` 误替换多个相同链接。

这些坑位已经写入 `SKILL.md` 的 Entry Page Update、WebDAV Writing 和 Pitfalls 部分。

## 仓库结构

```text
article-archiver-skill/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
└── references/
    ├── classification-by-account.md
    ├── extraction-script.py
    ├── knowledge-card-format.md
    ├── ocr-fallback.md
    ├── slide-articles.md
    ├── summary-guidelines.md
    ├── wechat-extraction.md
    └── wechat-formatting.md
```

## 安装方式

把仓库克隆到 Codex skills 目录：

```bash
git clone https://github.com/oceanzhang28/article-archiver-skill.git ~/.codex/skills/article-archiver
```

之后可以在 Codex 中这样调用：

```text
使用 $article-archiver，把这篇公众号文章转存到 Obsidian。
```

## 质量原则

- 原文必须完整保留。
- 摘要必须基于全文，不允许只复制开头段落。
- 批量转存不能降低摘要质量。
- 微信格式问题要先按 reference 检查和修复，再写入 Obsidian。
- 入口页写入后必须验证链接没有重复、文件没有被清空、正文没有损坏。
