# Classification by WeChat Account

Classify articles by their **WeChat public account** (the `nickname` / `nick_name` JavaScript variable), not just by the article topic. The account's publishing domain is the most reliable signal for destination folder.

## Known Accounts

| Account (nickname) | Destination | Notes |
| --- | --- | --- |
| `HR实名俱乐部` | `00知识库/HR知识/` | Author is 陈祖鑫. Covers HR tools, AI in HR, HR trends. All HR知识 regardless of AI angle. AI时代领导力/组织重塑/干部管理类解读（如《周鸿祎谈AI时代的领导力与组织重塑》2026-08-17）→ 组织发展. 大厂AI native团队实践报道（如《淘天集团：AI native团队的构想与实践》2026-08-19）→ 组织发展. HR职业转型/新角色类（如《对比FDE，我觉得Builder更像是HR的下一站》2026-08-21）→ 人才发展（与既有 FDE/Builder 文章同子类）. ⚠️ 文末常有线下活动推广块（「✅最新AI线下活动日程」或「【最近线下活动】」+ 城市+日期+扫码报名+二维码）→ 截断删除；其上方「> 文章链接」推荐列表保留. |
| `AI与组织领导力跃迁` | `00知识库/HR知识/` | Author 罗明. Covers org development, change management, leadership, compensation/governance. Subcategory by topic: 组织发展, HR的AI应用, 人才发展 (leadership/IDP/competency pieces like 领导力发展), or 薪酬绩效 (compensation/executive-incentive pieces like 集团薪酬改革, and 销售激励方案类 like 《销售激励，从"老板不满意、销售不买账"到"精准匹配"的方法论》 2026-08-17). 组织效能系列（《做好了一件事，还远不够，效能提升需要组织效能魔方》2026-08-24，六面框架：战略共识/组织耦合/能力进化/投产精准/效能运用/效能监控）→ 组织发展，与 人效/组织能力 文章同子类. 组织效能/组织有效性框架类（如《做好了一件事，还远不够，效能提升需要组织效能魔方》2026-08-24, 组织效能系列·第二篇）→ **组织发展**（与既有 美的集团组织与人才效能指标体系 同子类）。组织效能系列·第三篇《战略意图与战略损益表，让事想清楚，让团队可以做出来的几个方法》(2026-08-26, 拆解第一面「战略共识」：战略解码从业务开始/创新焦点/战略意图排序/组织能力扫描/投产解码/战略损益账三张纸) → **组织发展**（同第二篇先例）。 |
| `首席组织官` | `00知识库/HR知识/` | 组织方法论框架账号（房晟陶团队，3+1组织系统 / 十大组织系统 / 化玄学为工程）。组织设计、组织诊断、系统解构类文章 → 组织发展。Emits `var nickname` normally (2026-08 verified on 十大组织系统 2026年8月版). |
| `麦肯锡` | `00知识库/HR知识/` OR `00知识库/商业知识/` | Author varies (余天雯等). **Topic-based split — do NOT auto-route all 麦肯锡 to HR知识.** HR/AI/org content (AI时代HR转型、组织重塑、人才发展) → HR知识/HR的AI应用 or 组织发展. Business/consumer/commerce content (智能体商业、消费趋势、行业分析) → 商业知识, subcategory by theme: 智能体商业演进曲线 (六级自动化曲线、价值池迁移、零售启示, 2026-08-21) → 商业模式; 消费行为报告 → 市场营销. 麦肯锡 account extraction artifacts: blockquote section headers (`> 智能体商业的自动化曲线：六级演变`) → `###` heading; level headings split as `**0级：程序化便利**` + `**（"傻瓜式设置"）**` on two lines → merge to `### 0级：程序化便利（"傻瓜式设置"）`; author block `> ### Deepa Mahajan`、### Hannah Mayer noise → `> **Deepa Mahajan**、**Hannah Mayer**…`; tail promo (欢迎关注麦肯锡中国 + 公众号/视频号渠道 + 业务咨询/媒体垂询 + 版权声明) → cut, keep 作者介绍/感谢 lines. |
| `润米商城` | `00知识库/商业知识/` | 刘润（润米咨询）官方公众号。商业/行业分析、经营管理类文章 → 商业知识（subcategory by topic：经营管理/战略管理/行业案例等）。⚠️ 早期版本曾归 AI知识，用户已明确改为商业知识（商业知识目录建立后不再进 AI知识）。**刘润解读麦肯锡报告系列 subcategory precedents (verified 2026-08)**: `麦肯锡2026消费报告：4大变化，4大机会` (2026-07) → **市场营销**（消费行为主题）；`麦肯锡最新季刊：5大变化，5大机会` (2026-08) → **战略管理**（竞争/资源配置/赢与不输/FDI 主题）。Two McKinsey pieces both match `grep '麦肯锡'` but are SEPARATE articles with different subcategories — classify by the report's dominant theme, not by the shared keyword. 谈判/说服/沟通方法类（刘润读书会嘉宾分享，如《如何通过一场谈话，快速说服对方？》2026-08-23，北大光华马力教授《谈判：改变游戏规则》）→ **经营管理**（谈判方法论、说服技巧属经营与管理能力，非市场营销/战略管理）。 |
| `数字生命卡兹克` | `00知识库/卡兹克/` | Author is 卡兹克. Check subfolder: AI资讯 / claude code / codex / prompt / skills / workbuddy. ⚠️ **心得/观点/总结类文章（创业心得、AI使用心得、人才观等，不属于任何工具子分类）→ 卡兹克根目录**，且**不入入口页**——入口页只列子分类文章（verified 2026-08-20: 根目录已有《用AI的这三年，想跟你分享这9条心得。》《AI时代的人才，我觉得最重要的是这6点特质。》《上周做了场内部分享…》《创业2年半后，想跟你分享关于AI组织的这7点心得。》均无入口链接）。根目录文章 frontmatter tags 加 `khazix`（`- article / - wechat / - khazix`，参考《用AI的这三年》2026-02 的 frontmatter）。规则：工具教程→对应子文件夹；心得/观点/创业分享→根目录。**人物故事/采访随笔类（如《两个16岁的高中生，共享了自己的显卡和API，想让全校同学都免费用上AI。》2026-08-24——两位高中生自购显卡创办炼丹社、搭FreeAPI共享站让全校免费用AI，非工具教程非资讯）→ 根目录**，同样不入入口页、tags 加 khazix。**Prompt 合集/模板类文章（如《都Agent时代了，我还是想分享给你这12个我最常用的Prompt。》2026-08-21）→ prompt 子目录**——可复制即用的模板属于工具教程类，不是心得类（区别于 9条心得/6点特质 等 numbered-list reflections 与人物故事随笔）。 |
| `AI组织进化论` | `00知识库/AI知识/` | Emits `var nickname = htmlDecode("AI组织进化论")` — grep raw HTML for the htmlDecode pattern when plain `var nickname = "..."` comes back empty; `<meta name="author">` also populated. Subcategory by topic: org/team AI-agent case studies → AI应用. ⚠️ This account frequently interprets **McKinsey HR-transformation reports** (三支柱→产品与平台, HR work automation by 2030, agentic-era HR). Keep these in AI知识/AI应用 by account priority even though the topic is HR — near-duplicate-titled McKinsey HR articles from other accounts (麦肯锡, HR实名俱乐部) live in `00知识库/HR知识/`. When the user sends such a link, run the PROPFIND duplicate check against BOTH folders (decode hrefs first) so a same-title repost in the other folder isn't missed. |
| `高绩效HR` | `00知识库/HR知识/` | Author 曼妮AI. HR content, often PPT-preview articles (华为薪酬体系PPT etc.). Subcategory by topic (薪酬绩效 etc.). 战略体系/战略闭环类（BLM、DSTE，如《华为DSTE战略管理体系落地》2026-08-25）→ 组织发展（同 战略工具库 先例）。 |
| `车厘子随便写写` | `00知识库/HR知识/` | Author 车厘子. Publishes the 出海组织观察日记 series (第一季 组织观察；第二季《AI时代组织观察》2026-08 开篇《告别外部常模：AI时代，我们如何重新定义"人才"？》→ 组织发展) → mostly HR知识/组织发展. ⚠️ `var nickname` IS emitted, but as **`随便写写的地方`** (2026-08 verified) — `<meta name="author">` = `车厘子随便写写` is the reliable account identifier, not the nickname var. 正文段落用行首空格/全角空格缩进，提取后需 `re.sub(r'^[\s\u3000]+', '', body, flags=re.M)` 清理；列表项常提取为 `N.\n\n内容` 分裂（踩坑复盘/潜在解法/匹配清单），需按 Ordered List Number-Content Split 合并。 |
| `物业管理实践` | `00知识库/HR知识/` | Author 高尔基. 物业行业 HR/组织管理文章（如《物业公司如何做好定岗定编》→ 组织发展；同系列《物业公司如何做好流程优化》→ 组织发展）. 定岗定编/编制测算/流程类主题 → 组织发展. Emits `var nickname = htmlDecode("物业管理实践")` — grep raw HTML for the htmlDecode pattern. Series note (2026-08-16): 《物业公司定岗定编实操指南》 is the 实操 companion to 《物业公司如何做好定岗定编》 (方法论篇 → 实操篇: 样板项目从户数/面积参数一步步算到编制表 + 人力成本测算 + 三个坑) → 组织发展. |
| `物业管理实践` | `00知识库/HR知识/` | Author 高尔基. 物业行业HR/管理方法论系列（《物业公司如何做好流程优化》《物业公司如何做好定岗定编》等）→ 组织发展（组织设计、编制、流程方法）。Emits `var nickname = htmlDecode("物业管理实践")` — grep raw HTML for the htmlDecode pattern when plain extraction returns empty. |
| `穆胜咨询` | `00知识库/HR知识/` | Author 穆胜（人力资源效能/人效研究专家，穆胜咨询）。组织模式、人效管理、AI+组织评论类（如《热评 | 字节把TRAE、扣子塞进豆包，你却还在算人均营收》2026-08-25 → 组织发展）→ HR知识/组织发展。已有先例：《观点 - 穆胜：事业部制，就是双重金字塔》（标题 `|` 已替换为 ` - `）。Artifacts: 头部版权声明行（未经穆胜咨询许可禁止转载…）保留；章节标题提取为 `> **01**\n\n> **标题**` → 合并为 `### 01 标题`；行内 `###` 噪音 → bold（含跨行断裂如 `### 人效管理的对象，要从“\n\n人### ”扩展到“\n\n人机**”。**` → `**人效管理的对象，要从“人”扩展到“人机”**。`）；文末 iHRE 论坛推广图 + 延伸阅读图片卡片 + 点击阅读原文购买著作 → 删除，保留 `> **—END—**`。 |
| `物业管理实践` | `00知识库/HR知识/` | Author 高尔基. 物业行业 HR/组织管理方法论（定岗定编、流程优化等）→ HR知识/组织发展. No `nickname` JS var issue — emits `var nickname = htmlDecode("物业管理实践")`. |
| `润米商城` | `00知识库/商业知识/` | 刘润公司公众号 (刘润 + 主笔署名). 商业/行业分析、经营管理类 → 商业知识；个人转型方法论 → AI个人发展 (仅当文章核心是AI个人成长)。 |
| `刘润商业频道` | `00知识库/商业知识/` | 刘润的另一公众号，重发/精选旧文为主（如《谈业务，要有逻辑、有结构》→ 经营管理）。页脚有「关注刘润商业频道」订阅推广 + 推荐阅读导航块。按主题归商业知识 subcategory。 |
| `中欧商业在线` | `00知识库/AI知识/` | Author 姚音（前《中欧商业评论》主编）. Column《AI新组织观察》每期拆解一家企业的 AI 组织变革（真实案例：森马把AI塞进服装生意 → AI应用）。文章常转自「AI猫与机器狗」公众号。按主题归类：企业 AI 组织变革/转型案例 → AI应用；如主题偏商业则按内容判断。 |
| `猎聘人才官` | `00知识库/HR知识/` | 猎聘官方HR平台号（转自环球人力资源智库 ghrlib 为主）。人力成本/薪酬绩效/人才管理类 → 薪酬绩效或按主题（2026-08 验证：《张一鸣：为什么我不赞同控制人力成本？》→ 薪酬绩效）。作者取整理人（如 邱野）。Emits `var nickname = htmlDecode("猎聘人才官")`。头部有 `来 源｜/图 片｜/整 理｜` 元数据行保留。文末常带招聘专场广告（如「低空经济」专场）→ 从广告头图截断删除。 |
| `书图与手记` | `00知识库/HR知识/` | Author 阿涂. 任职资格主题 → 人才发展。连载《任职资格·从0到1》共33篇（2026-08 起），对用户任职资格标准工作强相关，值得跟进。文章为"图卡"卡片结构（图卡 0101/0202… + HTML 表格 + blockquote），提取后 inline `###` 转 bold、`\xa0` 转空格、表格保留。Emits `var nickname = htmlDecode("书图与手记")`。 |
| `物业管理实践` | `00知识库/HR知识/` | Author 高尔基. 物业行业HR/经营管理文章（定岗定编、流程优化等）→ HR知识，按主题归子类：定岗定编/组织管理/流程 → 组织发展（2026-08 验证：《物业公司如何做好定岗定编》→ 组织发展）。 |
| `赛普咨询` | `00知识库/AI知识/` | Author 李欣禹（赛普研究院）. 房地产行业 AI 应用/管理方法论（《房地产AI全场景实战：如何提升经营价值？》2026-08 → AI应用）。房地产 AI 落地案例/方法论 → AI应用；非 HR 内容（区别于同名的 /mnt/ 工作项目，公众号文章照常进知识库）。Emits `var nickname = htmlDecode("赛普咨询")`。 |
| `TRAE.ai` / `Trae-Real AI Engineer` | `00知识库/AI知识/` | Author TRAE（字节 AI 编程产品官方号，账号名 TRAE.ai）。`var nickname = htmlDecode("TRAE.ai")`，`<meta name="author">` = TRAE，extraction 的 `account` 字段返回 `Trae-Real AI Engineer`。工具/工作流实战指南类（如《咨询行业实战指南｜用好 TraeWork，海量信息高效分析》2026-08-23）→ **AI工具**（与既有 `Trae 完全使用指南` 同子类）。文章含官方插件介绍（TraeWork 场景插件：行业全景研究/战略增长罗盘/市场分析/天眼查/同花顺）+ 每个场景可复用 Prompt 模板。提取 artifacts 见 wechat-formatting.md「TRAE.ai Account Artifacts」节。 |
| `猎聘人才官` | `00知识库/HR知识/` | 猎聘官方HR平台账号，文章常转自环球人力资源智库（GHR，ID: ghrlib），作者/整理为邱野。人力成本、薪酬、人才管理主题 → 按主题归子类：人力成本管控/调薪/费用率（如《张一鸣：为什么我不赞同控制人力成本？》2026-08）→ 薪酬绩效。⚠️ 文末常有「低空经济」等招聘专场广告块（宣传图 + 扫码报名），归档时截掉。 |
| `书图与手记` | `00知识库/HR知识/` | Author 阿涂. 《任职资格·从0到1》系列（33篇连载，2026-08 已归档第01篇《一张图看懂任职资格》）。任职资格、职业通道、胜任力主题 → 人才发展。该系列与用户任职资格标准工作高度相关，后续同系列文章归 HR知识/人才发展。 |
| `猎聘人才官` | `00知识库/HR知识/` | 猎聘官方HR平台账号，作者/整理 邱野。常转发 环球人力资源智库（GHR, ID ghrlib）内容：正文头部有 `来 源｜环球人力资源智库（ID：ghrlib）` / `图 片｜...` / `整 理｜...` 元数据行（保留为正文头部）。人力成本、薪酬绩效、人才管理类 → HR知识；人力成本/薪酬/人效类主题 → 薪酬绩效（2026-08 验证：《张一鸣：为什么我不赞同控制人力成本？》→ 薪酬绩效）。尾部常见招聘专场广告（如「低空经济」人才招聘专场 + 扫码报名图）→ 从广告标题处回退到前一张 `![图片]` 截断删除。 |

## How to Determine the Account

1. **Primary**: `var nickname = htmlDecode("...")` in the page HTML
2. **Fallback**: `<meta name="author" content="...">` tag
3. **Last resort**: Footer text pattern `>/ 作者：...` or `来源：...`

## Classification Decision Tree

```
Is there a known `nickname` JS variable?
  ├── Yes → follow the table above
  └── No → check `<meta name="author">`
       ├── Matches a known account → use that
       └── Unknown → classify by article topic
            ├── HR/OD/talent → HR知识/
            ├── AI tools/workflows → AI知识/
            └── Tutorial on AI skill-building → AI知识（AI个人发展）
```

## Subcategory Selection

After choosing the destination folder, pick the subcategory by topic:

### HR知识 subcategories
- **HR的AI应用**: AI tools in HR, AI transforming HR roles, AI + organization
- **组织发展**: Change management, org design, OD models, leadership
- **人才发展**: Talent management, career development, competency
- **薪酬绩效**: Compensation, performance, HR efficiency
- **招聘**: Recruiting strategy, talent acquisition
- **hrBP相关**: HRBP practices
- **HR资讯**: Industry news, events

### 卡兹克 subfolders
- **AI资讯**: News, opinion, analysis (not tutorials)
- **claude code**: Claude Code tutorials/experiences
- **codex**: Codex tutorials/experiences  
- **prompt**: Prompt engineering
- **skills**: Skill development/usage
- **workbuddy**: WorkBuddy features/tutorials

**Root-level exception — personal-reflection / essay articles (心得分享类)**: 卡兹克's numbered-list reflections on AI work, organization, or career (9条心得 / 6点特质 / 7点心得 style) go to `00知识库/卡兹克/` ROOT, NOT a subfolder, and are NOT added to 卡兹克入口 (verified 2026-08-20 on 《创业2年半后，想跟你分享关于AI组织的这7点心得。》). Precedents: 《用AI的这三年，想跟你分享这9条心得。》(2026-02), 《AI时代的人才，我觉得最重要的是这6点特质。》(2026-05), 《上周做了场内部分享，关于我做AI这三年来总结的内容创作方法论。》 — all at root with no entry-page wikilink. 卡兹克入口 only indexes the 6 subfolder sections; root-level articles have no home there, so skip the entry-page update. Test: is the article a numbered-list of reflections/lessons rather than a tool tutorial or product/news piece? → root it.

Codex Security / OpenAI 安全插件等 Codex 生态工具教程 → `codex` 子目录（即使文章用 Claude Code 演示，按工具主生态归类）。

## Practical Example

Article: "实操：手把手教你用AI扒招聘数据，做岗位地图和人才能力模型"
- `nickname` = `HR实名俱乐部` → HR知识/
- Topic = AI recruitment tools → subcategory: HR的AI应用
- Correct: `00知识库/HR知识/` under `### HR的AI应用`
