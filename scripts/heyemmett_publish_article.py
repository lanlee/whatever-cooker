#!/usr/bin/env python3
"""Publish markdown into this repository's detected blog directory.

Created by HeyEmmett. The destination is intentionally recorded here so future
publishes do not need AI or repository rediscovery. ARTICLE_FORMAT_INSTRUCTIONS
records the user-approved format that the article writer must follow before this
deterministic script copies the finished article into the blog.
BLOG_STYLE_CONTRACT records the site-native renderer and visual rules captured
during the first publish. Later publishes reuse that renderer without calling an
AI API again for layout or styling.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

BLOG_DIR = Path('content/blog')
ARTICLE_EXTENSION = '.md'
ARTICLE_FORMAT_INSTRUCTIONS = ''
BLOG_STYLE_CONTRACT = {'version': 1,
 'framework': 'generic',
 'homepage': 'index.html',
 'style_reference_files': ['index.html'],
 'blog_route_files': ['blog/index.html', 'blog/blog.css', 'blog/posts.js', 'content/blog/ten-minute-meals.md'],
 'rules': ["Reuse the site's shared header, footer, layout, font, design tokens, and global stylesheet.",
           'Render all Markdown elements with explicit site-native typography, spacing, color, table, list, FAQ, and responsive styles.',
           'Render every Markdown table as one responsive table with a thead and tbody; never split its header from its body.',
           'Place one relevant image at a section boundary near the middle of the article body, separated from the top video by substantial article text; no '
           'duplicate image or headline placeholder.',
           'Start the article with its H1, then author/date and video; omit top tags and visible breadcrumbs. Do not enclose the article in a card, border, '
           'shadow or rounded box.',
           'Render exactly one site header, H1 and author/date block; strip duplicates from body when the layout owns them.',
           'Keep schema only in escaped application/ld+json scripts; remove legacy visible schema sections and code fences.',
           'Render the verified YouTube video once immediately below the title/byline and before the hero/body, with no Relevant video heading.',
           'Keep public article URLs at /blog/<slug> and reuse the existing /blog renderer for every later publish.',
           'Keep the canonical article URL in metadata and links that need it; do not repeat it visibly under the article title.'],
 'style_generation': 'first_publish_only',
 'future_publish': 'run scripts/heyemmett_publish_article.py; do not call an AI API for layout or styling'}


def slugify(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value or "article"


def _table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _is_table_row(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 2


def _is_table_separator(line: str) -> bool:
    cells = _table_cells(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def normalize_markdown_tables(markdown: str) -> str:
    """Normalize tables into contiguous header, separator, and body rows."""
    trailing_newline = markdown.endswith("\n")
    lines = markdown.splitlines()
    output: list[str] = []
    index = 0
    while index < len(lines):
        header = lines[index]
        if not _is_table_row(header):
            output.append(header)
            index += 1
            continue
        separator_index = index + 1
        while separator_index < len(lines) and not lines[separator_index].strip():
            separator_index += 1
        if separator_index >= len(lines) or not _is_table_separator(lines[separator_index]):
            output.append(header)
            index += 1
            continue
        headers = _table_cells(header)
        if len(_table_cells(lines[separator_index])) != len(headers):
            raise ValueError("Markdown table header and separator column counts do not match")
        row_index = separator_index + 1
        while row_index < len(lines) and not lines[row_index].strip():
            row_index += 1
        body: list[str] = []
        while row_index < len(lines) and _is_table_row(lines[row_index]):
            if len(_table_cells(lines[row_index])) != len(headers):
                raise ValueError("Markdown table rows must use the same number of columns")
            body.append(lines[row_index].strip())
            row_index += 1
        if not body:
            raise ValueError("Markdown table must include at least one body row")
        output.extend([
            header.strip(),
            "| " + " | ".join("---" for _ in headers) + " |",
            *body,
        ])
        index = row_index
    result = "\n".join(output)
    return result + ("\n" if trailing_newline else "")


def publish(title: str, content_file: str, slug: str = "") -> Path:
    source = Path(content_file)
    if not source.is_file():
        raise FileNotFoundError(source)
    BLOG_DIR.mkdir(parents=True, exist_ok=True)
    destination = BLOG_DIR / (slugify(slug or title) + ARTICLE_EXTENSION)
    content = normalize_markdown_tables(source.read_text(encoding="utf-8"))
    destination.write_text(content, encoding="utf-8")
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    parser.add_argument("--content-file", required=True)
    parser.add_argument("--slug", default="")
    args = parser.parse_args()
    print(publish(args.title, args.content_file, args.slug))
