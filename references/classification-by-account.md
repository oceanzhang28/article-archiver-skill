# Classification by WeChat Account

Classify articles by their **WeChat public account** (the `nickname` / `nick_name` JavaScript variable), not just by the article topic. The account's publishing domain is the most reliable signal for destination folder.

## Known Accounts

| Account (nickname) | Destination | Notes |
| --- | --- | --- |
| `HR实名俱乐部` | `00知识库/HR知识/` | Author is 陈祖鑫. Covers HR tools, AI in HR, HR trends. All HR知识 regardless of AI angle. |
| `AI与组织领导力跃迁` | `00知识库/HR知识/` | Author 罗明. Covers org development, change management, leadership. Goes to HR知识/组织发展 or HR的AI应用. |
| `麦肯锡` | `00知识库/HR知识/` | Author varies (余天雯等). HR/AI/org content from McKinsey China. Goes to HR知识/HR的AI应用 or 组织发展. |
| `润米商城` | `00知识库/AI知识/` | Author 刘润. Business/industry analysis with a strong AI angle (FDE/consulting evolution, McKinsey consumer report, brand GEO). Goes to AI知识/AI应用. Article footer carries the 润米商城 promo block (品牌推广/培训合作/商业咨询/转载开白) — see wechat-formatting.md cleanup. |
| `数字生命卡兹克` | `00知识库/卡兹克/` | Author is 卡兹克. Check subfolder: AI资讯 / claude code / codex / prompt / skills / workbuddy. |
| `AI组织进化论` | `00知识库/AI知识/` | Emits `var nickname = htmlDecode("AI组织进化论")` — grep raw HTML for the htmlDecode pattern when plain `var nickname = "..."` comes back empty; `<meta name="author">` also populated. Subcategory by topic: org/team AI-agent case studies → AI应用. |
| `高绩效HR` | `00知识库/HR知识/` | Author 曼妮AI. HR content, often PPT-preview articles (华为薪酬体系PPT etc.). Subcategory by topic (薪酬绩效 etc.). |
| `车厘子随便写写` | `00知识库/HR知识/` | Author 车厘子. Publishes the 出海组织观察日记 series → mostly HR知识/组织发展. No `nickname` JS var; meta author tag populated. |
| `高绩效HR` | `00知识库/HR知识/` | HR tools, salary/compensation, performance management, training courses. Subcategory: 薪酬绩效 when salary/comp/finance-centric; otherwise follow topic. |
| `润米商城` | `00知识库/AI知识/` | 刘润公司公众号 (刘润 + 主笔署名). 商业/行业分析、AI落地组织案例 → AI应用; 个人转型方法论 → AI个人发展. E.g. "在这家美国公司的身上…"(Palantir/FDE/咨询行业) → AI应用. |
| `润米商城` | `00知识库/AI知识/` | 刘润（润米咨询）官方公众号。商业/行业分析类文章：AI 相关组织与行业案例归 **AI应用**（如 FDE/Palantir、咨询行业进化），个人成长类归 AI个人发展。页脚有固定推广块（品牌推广/培训合作/商业咨询/转载开白），归档时压缩成单行。 |

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

## Practical Example

Article: "实操：手把手教你用AI扒招聘数据，做岗位地图和人才能力模型"
- `nickname` = `HR实名俱乐部` → HR知识/
- Topic = AI recruitment tools → subcategory: HR的AI应用
- Correct: `00知识库/HR知识/` under `### HR的AI应用`
