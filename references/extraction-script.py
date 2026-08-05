#!/usr/bin/env python3
"""
Extract a WeChat public-account article as metadata + Markdown body.

Usage:
    python3 extraction-script.py <url>
    curl -s -L -A "<UA>" "<url>" | python3 extraction-script.py --url "<url>"

The script intentionally converts body HTML to Markdown instead of stripping
all HTML tags first. This preserves paragraph breaks, images, quotes, lists,
and code-like blocks better for Obsidian archiving.
"""

import argparse
import html
from html.parser import HTMLParser
import json
import re
import subprocess
import sys
from datetime import datetime
from urllib.parse import unquote


DESKTOP_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def extract_var(name, content):
    patterns = [
        rf"var\s+{re.escape(name)}\s*=\s*'((?:\\'|[^'])*)'(?:\.html\(false\))?",
        rf'var\s+{re.escape(name)}\s*=\s*"((?:\\"|[^"])*)"(?:\.html\(false\))?',
        rf"{re.escape(name)}\s*=\s*'((?:\\'|[^'])*)'",
        rf'{re.escape(name)}\s*=\s*"((?:\\"|[^"])*)"',
    ]
    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            return html.unescape(match.group(1)).strip()
    return ""


def extract_meta_property(content, prop):
    pattern = rf'<meta[^>]+(?:property|name)=["\']{re.escape(prop)}["\'][^>]+content=["\']([^"\']*)["\']'
    match = re.search(pattern, content, re.I)
    return html.unescape(match.group(1)).strip() if match else ""


def parse_date(content):
    create_date = extract_var("create_date", content)
    if create_date:
        return create_date

    ct = extract_var("ct", content)
    if ct:
        try:
            return datetime.fromtimestamp(int(ct)).strftime("%Y-%m-%d")
        except ValueError:
            return ""
    return ""


def extract_footer_author(content):
    patterns = [
        r">/\s*作者[：:]\s*(.+?)(?:[<\n]|$)",
        r"作者[：:]\s*([^<\n]{1,80})",
    ]
    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            author = re.sub(r"\s+", " ", html.unescape(match.group(1))).strip()
            if author and "投稿" not in author and "邮箱" not in author:
                return author
    return ""


def extract_js_content_div(content):
    idx = content.find('id="js_content"')
    if idx < 0:
        idx = content.find("id='js_content'")
    if idx < 0:
        return ""

    div_start = content.rfind("<div", 0, idx)
    if div_start < 0:
        return ""

    depth = 0
    pos = div_start
    while pos < len(content):
        next_open = content.find("<div", pos)
        next_close = content.find("</div", pos)

        if next_close < 0:
            break
        if 0 <= next_open < next_close:
            depth += 1
            pos = next_open + 4
            continue

        depth -= 1
        close_end = content.find(">", next_close)
        if depth == 0 and close_end >= 0:
            return content[div_start : close_end + 1]
        pos = close_end + 1 if close_end >= 0 else next_close + 6

    return ""


def extract_content_noencode(content):
    patterns = [
        r'var\s+content_noencode\s*=\s*"((?:\\.|[^"\\])*)"',
        r"var\s+content_noencode\s*=\s*'((?:\\.|[^'\\])*)'",
        r'content_noencode\s*:\s*"((?:\\.|[^"\\])*)"',
        r"content_noencode\s*:\s*'((?:\\.|[^'\\])*)'",
    ]
    match = None
    for pattern in patterns:
        match = re.search(pattern, content, re.S)
        if match:
            break
    if not match:
        return ""
    raw = match.group(1)
    try:
        decoded = bytes(raw, "utf-8").decode("unicode_escape")
    except UnicodeDecodeError:
        decoded = raw
    return html.unescape(decoded)


def attrs_to_dict(attrs):
    return {k.lower(): (v or "") for k, v in attrs}


def is_quote_like(attrs):
    attr = attrs_to_dict(attrs)
    style = attr.get("style", "").lower()
    klass = attr.get("class", "").lower()
    data = " ".join(f"{k}={v}" for k, v in attr.items()).lower()

    if any(word in klass or word in data for word in ("quote", "blockquote", "rich_media_tool")):
        return True
    if "border-left" in style:
        return True
    if "background" in style and "padding" in style:
        return True
    return False


class WeChatMarkdownConverter(HTMLParser):
    block_tags = {"p", "div", "section", "article", "main", "figure", "figcaption"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.tag_stack = []
        self.quote_depth = 0
        self.pre_depth = 0
        self.list_stack = []
        self.link_stack = []
        self.line_start = True

    def append(self, text):
        if not text:
            return
        parts = text.split("\n")
        for i, part in enumerate(parts):
            if i:
                self.out.append("\n")
                self.line_start = True
            if part:
                if self.line_start and self.quote_depth and not self.pre_depth:
                    self.out.append("> ")
                self.out.append(part)
                self.line_start = False

    def newline(self, count=1):
        current = "".join(self.out)
        existing = len(current) - len(current.rstrip("\n"))
        needed = max(0, count - existing)
        if needed:
            self.out.append("\n" * needed)
            self.line_start = True

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attr = attrs_to_dict(attrs)
        quote = tag == "blockquote" or (tag in {"section", "div"} and is_quote_like(attrs))
        self.tag_stack.append((tag, quote))

        if quote:
            self.newline(2)
            self.quote_depth += 1
        elif tag in self.block_tags:
            self.newline(2)
        elif tag == "br":
            self.newline(1)
        elif tag in {"strong", "b"}:
            self.append("**")
        elif tag in {"em", "i"}:
            self.append("*")
        elif tag == "pre":
            self.newline(2)
            self.append("```")
            self.newline(1)
            self.pre_depth += 1
        elif tag == "code" and not self.pre_depth:
            self.append("`")
        elif tag == "a":
            href = attr.get("href", "").strip()
            self.link_stack.append(href)
            if href:
                self.append("[")
        elif tag == "img":
            src = attr.get("data-src") or attr.get("src") or attr.get("data-original")
            src = html.unescape(unquote(src.strip())) if src else ""
            alt = (attr.get("alt") or attr.get("title") or "image").strip()
            if src:
                self.newline(2)
                self.append(f"![{alt}]({src})")
                self.newline(2)
        elif tag == "ul":
            self.list_stack.append({"type": "ul", "n": 0})
            self.newline(1)
        elif tag == "ol":
            self.list_stack.append({"type": "ol", "n": 0})
            self.newline(1)
        elif tag == "li":
            self.newline(1)
            if self.list_stack:
                current = self.list_stack[-1]
                current["n"] += 1
                marker = "-" if current["type"] == "ul" else f"{current['n']}."
            else:
                marker = "-"
            indent = "  " * max(0, len(self.list_stack) - 1)
            self.append(f"{indent}{marker} ")
        elif tag == "table":
            self.newline(2)
            self.append("<table>")
            self.newline(1)
        elif tag in {"tr", "thead", "tbody", "th", "td"}:
            self.append(f"<{tag}>")

    def handle_endtag(self, tag):
        tag = tag.lower()

        if tag in {"strong", "b"}:
            self.append("**")
        elif tag in {"em", "i"}:
            self.append("*")
        elif tag == "pre":
            self.pre_depth = max(0, self.pre_depth - 1)
            self.newline(1)
            self.append("```")
            self.newline(2)
        elif tag == "code" and not self.pre_depth:
            self.append("`")
        elif tag == "a":
            href = self.link_stack.pop() if self.link_stack else ""
            if href:
                self.append(f"]({href})")
        elif tag in {"ul", "ol"}:
            if self.list_stack:
                self.list_stack.pop()
            self.newline(2)
        elif tag == "li":
            self.newline(1)
        elif tag == "table":
            self.newline(1)
            self.append("</table>")
            self.newline(2)
        elif tag in {"tr", "thead", "tbody", "th", "td"}:
            self.append(f"</{tag}>")
        elif tag in self.block_tags or tag == "blockquote":
            self.newline(2)

        while self.tag_stack:
            open_tag, quote = self.tag_stack.pop()
            if quote:
                self.quote_depth = max(0, self.quote_depth - 1)
            if open_tag == tag:
                break

    def handle_data(self, data):
        if self.pre_depth:
            self.append(data.rstrip())
            return
        text = re.sub(r"[ \t\r\f\v]+", " ", data)
        self.append(text)

    def get_markdown(self):
        text = "".join(self.out)
        text = html.unescape(text)
        text = re.sub(r"[ \t]+\n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"^\s*!\s*$\n?", "", text, flags=re.M)
        text = re.sub(r"^\s*-\s*$\n?", "", text, flags=re.M)
        return text.strip()


def html_to_markdown(body_html):
    parser = WeChatMarkdownConverter()
    parser.feed(body_html)
    parser.close()
    return repair_markdown(parser.get_markdown())


def repair_markdown(text):
    text = re.sub(r"\*\*([^*\n]{1,80})\*\*(?=\S)", r"### \1\n\n", text)
    text = re.sub(
        r"^\*\*((?:[一二三四五六七八九十]+|[0-9]+)[.、．]\s*[^*\n]{1,60}|写在最后)\*\*$",
        r"### \1",
        text,
        flags=re.M,
    )
    text = re.sub(r"^\*\*\s*$\n?", "", text, flags=re.M)
    text = re.sub(r"^\*{4}###\s*(.+)$", r"### \1", text, flags=re.M)
    text = re.sub(r"^\*{4}\s*$\n?", "", text, flags=re.M)
    text = re.sub(r"^>/\s*", "> / ", text, flags=re.M)

    known_sections = [
        "关于我",
        "第一性原理",
        "约束先行",
        "交互设计原则",
        "工作方式",
        "开发习惯",
        "Git",
        "部署",
        "CLAUDE.md",
        "AGENTS.md",
    ]
    for section in known_sections:
        text = re.sub(rf"^## ({re.escape(section)}[^\n]*)", r"> **\1**", text, flags=re.M)

    lines = text.split("\n")
    repaired = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("## ") and len(line) > 63:
            block = [line]
            j = i + 1
            while j < len(lines) and lines[j].startswith("## ") and len(lines[j]) > 63:
                block.append(lines[j])
                j += 1
            if len(block) >= 3:
                repaired.append("```markdown\n" + "\n".join(block) + "\n```")
                i = j
                continue
        repaired.append(line)
        i += 1
    text = "\n".join(repaired)
    text = repair_embedded_agents_guidelines(text)

    return re.sub(r"\n{3,}", "\n\n", text).strip()


def repair_embedded_agents_guidelines(text):
    """Repair compressed AGENTS.md-style guidance copied from WeChat code blocks."""
    if "Behavioral guidelines to reduce common LLM coding mistakes" not in text:
        return text

    text = text.replace(
        "\n```\n```\nBehavioral guidelines to reduce common LLM coding mistakes",
        "\n```markdown\nBehavioral guidelines to reduce common LLM coding mistakes",
    )
    text = re.sub(
        r"(\*\*These guidelines are working if:\*\*.*?clarifying questions come before implementation rather than after mistakes\.)\n```\n\n```",
        r"\1\n```",
        text,
        flags=re.S,
    )

    start = text.find("```markdown\nBehavioral guidelines to reduce common LLM coding mistakes")
    if start < 0:
        return text
    end = text.find("\n```", start + len("```markdown\n"))
    if end < 0:
        return text

    block = text[start + len("```markdown\n"):end]
    block = block.replace("\u00a0", " ")
    replacements = [
        (r"mistakes\. Merge", "mistakes.\nMerge"),
        (r"\*\*Tradeoff:\*\*", "\n**Tradeoff:**"),
        (r"## 1\. ", "\n## 1. "),
        (r"## 2\. ", "\n## 2. "),
        (r"## 3\. ", "\n## 3. "),
        (r"## 4\. ", "\n## 4. "),
        (r"### Don't assume", "\n### Don't assume"),
        (r"### Minimum code", "\n### Minimum code"),
        (r"### Touch only", "\n### Touch only"),
        (r"### Define success", "\n### Define success"),
        (r"Before implementing:- ", "Before implementing:\n- "),
        (r"When editing existing code:- ", "When editing existing code:\n- "),
        (r"When your changes create orphans:- ", "\nWhen your changes create orphans:\n- "),
        (r"For multi-step tasks, state a brief plan:1\. ", "For multi-step tasks, state a brief plan:\n1. "),
        (r"2\. \\[Step\\]", "\n2. [Step]"),
        (r"3\. \\[Step\\]", "\n3. [Step]"),
        (r"---\*\*These guidelines", "\n---\n\n**These guidelines"),
    ]
    for pattern, repl in replacements:
        block = re.sub(pattern, repl, block)
    block = re.sub(r"(?<=[。.!?])-\s+", "\n- ", block)
    block = re.sub(r"(?<=it\.)Ask yourself", "\n\nAsk yourself", block)
    block = re.sub(r"(?<=asked\.)Ask yourself", "\n\nAsk yourself", block)
    block = re.sub(r"(?<=asked\.)The test:", "\n\nThe test:", block)
    block = re.sub(r"(?<=mistakes\.)\s+", "\n", block)
    block = re.sub(r"\n{3,}", "\n\n", block).strip()

    return text[:start] + "```markdown\n" + block + text[end:]


def extract_article(content, url=""):
    title = extract_var("msg_title", content) or extract_meta_property(content, "og:title")
    account = extract_var("nickname", content) or extract_var("nick_name", content)
    author = extract_footer_author(content) or account
    date = parse_date(content)
    description = extract_var("msg_desc", content) or extract_meta_property(content, "description")

    body_html = extract_js_content_div(content) or extract_content_noencode(content)
    body_markdown = html_to_markdown(body_html) if body_html else ""
    footer_author = re.search(r"^>?\s*/\s*作者[：:]\s*([^\n<]{1,80})", body_markdown, re.M)
    if footer_author:
        author = footer_author.group(1).strip()
    elif "\\x3c" in author or len(author) > 80:
        author = account

    return {
        "title": title,
        "author": author,
        "account": account,
        "date": date,
        "description": description,
        "url": url,
        "body_markdown": body_markdown,
        "body_length": len(body_markdown),
    }


def fetch_url(url):
    result = subprocess.run(
        ["curl", "-s", "-L", "-A", DESKTOP_UA, url],
        capture_output=True,
        text=True,
        timeout=45,
        check=False,
    )
    return result.stdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url_arg", nargs="?")
    parser.add_argument("--url", default="")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of readable Markdown.")
    args = parser.parse_args()

    url = args.url or args.url_arg or ""
    if not sys.stdin.isatty():
        content = sys.stdin.read()
    elif url:
        content = fetch_url(url)
    else:
        parser.error("provide a URL or pipe HTML on stdin")

    article = extract_article(content, url=url)

    if args.json:
        print(json.dumps(article, ensure_ascii=False, indent=2))
        return

    print("=== TITLE ===")
    print(article["title"])
    print("=== AUTHOR ===")
    print(article["author"])
    print("=== DATE ===")
    print(article["date"])
    print("=== DESCRIPTION ===")
    print(article["description"])
    print("=== BODY LENGTH ===")
    print(article["body_length"])
    print("=== BODY MARKDOWN ===")
    print(article["body_markdown"])


if __name__ == "__main__":
    main()
