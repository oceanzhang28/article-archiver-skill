# WeChat Article Extraction Reference

Use this reference when archiving `mp.weixin.qq.com` articles. The goal is not just to extract text; the goal is to preserve the article's reading structure in Markdown.

## Principle

Extract the article body as HTML first, then convert the HTML to semantic Markdown. Do not strip all tags at the beginning. Early tag stripping destroys WeChat paragraph boundaries, quote modules, image positions, code blocks, lists, and tables.

## Fetch HTML

Try browser access first if available. If the browser hits a captcha or abnormal-environment page, use curl.

Primary request:

```bash
curl -s -L \
  -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  "https://mp.weixin.qq.com/s/ARTICLE_SN"
```

If the primary request returns a captcha page (small HTML, contains `环境异常` or `验证码`), try a mobile UA first — this often bypasses the captcha without needing cookies:

```bash
curl -s -L \
  -A "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36" \
  -H "Accept: text/html,application/xhtml+xml" \
  -H "Accept-Language: zh-CN,zh;q=0.9" \
  -H "Referer: https://weixin.qq.com/" \
  "https://mp.weixin.qq.com/s/ARTICLE_SN"
```

If the captcha persists, fall back to the cookie-based approach:

Fallback request with mobile UA and cookie reuse:

```bash
curl -s -L -b /tmp/wx_cookies.txt -c /tmp/wx_cookies.txt \
  -A "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36" \
  -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" \
  -H "Accept-Language: zh-CN,zh;q=0.9,en;q=0.8" \
  -H "Referer: https://mp.weixin.qq.com/" \
  "https://mp.weixin.qq.com/s/ARTICLE_SN"
```

Heuristic: captcha wrappers are often much smaller than real article pages (~18KB vs 3MB+ for a real article). If the page contains `环境异常`, `验证码`, or no `js_content`, don't give up — try the mobile UA bypass above. It resolves most captcha cases without cookies.

## Extract Metadata

Try both single and double quotes for JavaScript variables:

| Field | Preferred Source | Fallback |
| --- | --- | --- |
| title | `var msg_title` | `<meta property="og:title">` |
| account | `var nickname` / `var nick_name` | `<meta name="author">` → footer text |
| author | footer pattern `作者：...` | `<meta name="author">` → account name |
| date | `var create_date` | `var ct` Unix timestamp |
| description | `var msg_desc` | `<meta name="description">` / `<meta property="og:description">` |

Some articles do not emit `var nickname` / `var nick_name` at all (e.g. the `AI组织进化论` account), but the `<meta name="author">` tag is populated. Always check the meta tag when JS variables come back empty.

Another miss: when the page emits `var nickname = htmlDecode("...")` (e.g. `HR实名俱乐部`), the script's plain `var nickname = "..."` pattern returns empty for BOTH account and author even though title/body extracted fine. If account/author are empty but the body is good, grep the raw HTML instead of re-extracting:

```bash
grep -oP 'var\s+nickname\s*=\s*htmlDecode\("([^"]*)"\)' /tmp/wx_article.html
grep -oP '<meta[^>]*name="author"[^>]*content="([^"]*)"' /tmp/wx_article.html
```

Important patterns:

```python
r"var\s+msg_title\s*=\s*'([^']+)'(?:\.html\(false\))?"
r'var\s+msg_title\s*=\s*"([^"]+)"(?:\.html\(false\))?'
r'>/\s*作者[：:]\s*(.+?)(?:[<\n]|$)'
r'<meta[^>]*name="author"[^>]*content="([^"]+)"'
```

If `ct` is present, convert it with local time:

```python
datetime.fromtimestamp(int(ct)).strftime("%Y-%m-%d")
```

## Extract Body HTML

Primary body source: the full `<div id="js_content">...</div>` element.

Use a small parser or balanced-div scan. Avoid a single regex that assumes fixed attribute ordering.

Fallback body source: `content_noencode`.

```python
m = re.search(r'var\s+content_noencode\s*=\s*"((?:\\.|[^"\\])*)"', html_content, re.S)
if m:
    raw = bytes(m.group(1), "utf-8").decode("unicode_escape")
    body_html = html.unescape(raw)
```

Do not decode entities before parsing attributes unless the body came from `content_noencode`; premature decoding can break image URLs and tag boundaries.

## Convert HTML to Markdown

After body HTML is extracted, apply the rules in `wechat-formatting.md`.

Minimum conversion requirements:

- `p`, `section`, `div`: block boundaries with blank lines between meaningful blocks
- `br`: line break
- `strong`, `b`: `**text**`
- `em`, `i`: `*text*`
- `a`: `[text](url)` when the text is meaningful
- `img`: `![alt](data-src or src)` in the original position
- `ul`, `ol`, `li`: Markdown lists
- `blockquote` and quote-like styled sections: Markdown blockquotes
- `pre`, `code`: fenced code blocks or inline code
- `table`: preserve HTML table if Markdown table conversion is unreliable

## Reusable Script

Use `references/extraction-script.py` for a standalone extraction pass:

```bash
python3 references/extraction-script.py "https://mp.weixin.qq.com/s/ARTICLE_SN" > /tmp/article.md
```

or:

```bash
curl -s -L -A "<UA>" "https://mp.weixin.qq.com/s/ARTICLE_SN" \
  | python3 references/extraction-script.py --url "https://mp.weixin.qq.com/s/ARTICLE_SN" \
  > /tmp/article.md
```

The script prints metadata and a Markdown body. Still run the final checklist in `wechat-formatting.md`; WeChat's HTML variants change often.

## Common Failures

- Body length is tiny: likely captcha or extraction failed.
- Body is mojibake (`æ...`/`ç...` where Chinese should be): the script decoded UTF-8 bytes as latin-1. Fix with `body.encode('latin-1').decode('utf-8')` — title/date/body_length will look fine, so don't mistake this for a captcha failure.
- Images become standalone `!`: image URL extraction failed; retry with `data-src`.
- Whole article becomes one paragraph: block tags were stripped too early.
- Quote modules become normal text: style-based quote detection was not applied.
- Embedded config or `CLAUDE.md` content becomes many `##` headings: convert that block back to fenced code or blockquote.
- Section title and first sentence merge, such as `**一. 标题**正文`: split into heading plus paragraph.
- Images silently missing after conversion: WeChat wraps many images in bare `<section><img ...></section>`. If using a DOM-based converter (e.g. BeautifulSoup), `tag.get_text(strip=True)` returns empty for such sections — they are easy to mis-filter as "empty" tags. Before skipping a tag, check for `<img>`, `<video>`, `<audio>`, `<iframe>`, or `<canvas>` children. The `references/extraction-script.py` uses a streaming `HTMLParser` and does not have this problem.
