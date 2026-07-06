#!/usr/bin/env python3
"""Split the TOS 7 development guide into chapter files with navigation."""

import re
import os

SOURCE = "/Volume1/public/apptest/TOS 7 应用开发与上架指南.md"
OUTDIR = "/Volume1/public/apptest/应用开发指南分开章节管理/docs"

# Chapter metadata: (number, short_name, filename)
CHAPTERS = [
    (1, "文档概述", "01_文档概述.md"),
    (2, "应用架构策略", "02_应用架构策略.md"),
    (3, "快速开始", "03_快速开始.md"),
    (4, "包规范", "04_包规范.md"),
    (5, "ABI兼容性", "05_ABI兼容性.md"),
    (6, "开发环境", "06_开发环境.md"),
    (7, "应用类型", "07_应用类型.md"),
    (8, "Deb开发规范", "08_Deb开发规范.md"),
    (9, "Docker开发", "09_Docker开发.md"),
    (10, "权限模型", "10_权限模型.md"),
    (11, "包签名安全", "11_包签名安全.md"),
    (12, "最佳实践", "12_最佳实践.md"),
    (13, "本地测试调试", "13_本地测试调试.md"),
    (14, "CICD指南", "14_CICD指南.md"),
    (15, "上架流程", "15_上架流程.md"),
    (16, "审核标准", "16_审核标准.md"),
    (17, "运维下架", "17_运维下架.md"),
    (18, "商业化捐赠", "18_商业化捐赠.md"),
    (19, "FAQ常见问题", "19_FAQ常见问题.md"),
    (20, "附录合集", "20_附录合集.md"),
]

def read_source():
    with open(SOURCE, 'r', encoding='utf-8') as f:
        return f.read()

def find_chapter_boundaries(content):
    """Find start and end line of each chapter in the source."""
    lines = content.split('\n')
    
    # Find all chapter heading lines
    boundaries = []
    for i, line in enumerate(lines):
        m = re.match(r'^## (\d+)\.\s+', line)
        if m:
            num = int(m.group(1))
            boundaries.append((num, i))
    
    boundaries.append((21, len(lines)))  # sentinel
    
    chapters_content = {}
    for idx in range(len(boundaries) - 1):
        ch_num = boundaries[idx][0]
        start = boundaries[idx][1]
        end = boundaries[idx + 1][1]
        ch_lines = lines[start:end]
        chapters_content[ch_num] = '\n'.join(ch_lines).strip()
    
    return chapters_content

def get_navigation(current, total, short_name):
    """Generate navigation footer with prev/next/TOC links."""
    parts = []
    
    if current > 1:
        prev_ch = CHAPTERS[current - 2]
        parts.append(f"← [上一章：{prev_ch[1]}]({prev_ch[2]})")
    
    if current < total:
        next_ch = CHAPTERS[current]
        parts.append(f"[下一章：{next_ch[1]}]({next_ch[2]}) →")
    
    parts.append(f"[📖 返回总目录](../README.md)")
    
    return "\n\n---\n\n" + " &nbsp;&nbsp;|&nbsp;&nbsp; ".join(parts) + "\n"

def build_chapter_header(num, title):
    """Build a chapter title matching original heading format, but with consistent H1."""
    return f"# {num}. {title}"

def process_chapter(num, title, content_lines):
    """Process a chapter: ensure proper heading and append navigation."""
    # Remove original TOC section if present (intro lines before real content)
    lines = content_lines.split('\n')
    
    # The first line is the original ## heading - replace with # heading
    if lines and re.match(r'^## \d+\.', lines[0]):
        lines[0] = f"# {num}. {title}"
    
    # Trim trailing horizontal rules and blank lines to avoid double ---
    while lines and lines[-1].strip() in ('', '---', '***', '___'):
        lines.pop()
    
    body = '\n'.join(lines)
    
    # Append navigation
    body += get_navigation(num, len(CHAPTERS), title)
    
    return body

def build_readme(chapters):
    """Generate the README.md index file."""
    lines = []
    lines.append("# TOS 7 应用开发与上架指南")
    lines.append("")
    lines.append("**版本号：** v2.7  ")
    lines.append("**最后更新：** 2026-05-27  ")
    lines.append("**适用平台：** TOS 7.0 及以上版本  ")
    lines.append("**面向对象：** 全球第三方开发者、独立开发者、企业合作伙伴  ")
    lines.append("")
    lines.append("> 📢 本文档当前基于 TOS7.0 Beta 版编写，后续 TOS7.x 版本兼容性将保持一致。")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 🚀 快速入口")
    lines.append("")
    lines.append("| 场景 | 推荐阅读 |")
    lines.append("|------|---------|")
    lines.append("| 第一次接触 TOS 应用开发 | [📘 第 3 章 · 快速开始](docs/03_快速开始.md) — 5 分钟跑通流程 |")
    lines.append("| 了解整体架构 | [📘 第 2 章 · 应用架构策略](docs/02_应用架构策略.md) — 容器优先策略 |")
    lines.append("| 开发 Deb 应用 | [📘 第 8 章 · Deb 开发规范](docs/08_Deb开发规范.md) — 完整规范 |")
    lines.append("| 开发 Docker 应用 | [📘 第 9 章 · Docker 开发](docs/09_Docker开发.md) — Docker Compose 指南 |")
    lines.append("| 准备上架 | [📘 第 15 章 · 上架流程](docs/15_上架流程.md) — 提交审核 |")
    lines.append("| 遇到问题 | [📘 第 19 章 · FAQ](docs/19_FAQ常见问题.md) — 常见问题 |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 📑 完整目录")
    lines.append("")
    
    for num, title, filename in chapters:
        lines.append(f"| {num:02d} | [{title}](docs/{filename}) |")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 📂 仓库结构")
    lines.append("")
    lines.append("```")
    lines.append("docs/")
    lines.append("├── README.md            ← 你在这里")
    for num, title, filename in chapters:
        lines.append(f"├── {filename}")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 🔗 相关资源")
    lines.append("")
    lines.append("- [TNAS 开发者平台](https://developer.terra-master.com)（即将上线）")
    lines.append("- [Deb 应用模板（单包）](https://github.com/terra-master/app-template-deb)")
    lines.append("- [Deb 应用模板（双包）](https://github.com/terra-master/app-template-deb-dual)")
    lines.append("- [Docker 应用模板](https://github.com/terra-master/app-template-docker)")
    lines.append("- [TOS 应用中心](https://terra-master.com)")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*本文档由 [TOS 7 应用开发与上架指南] 拆分生成，各章节独立维护。*")
    
    return '\n'.join(lines) + '\n'

def main():
    os.makedirs(OUTDIR, exist_ok=True)
    
    content = read_source()
    chapters_content = find_chapter_boundaries(content)
    
    print(f"Found {len(chapters_content)} chapters in source")
    
    # Write each chapter file
    for num, title, filename in CHAPTERS:
        if num in chapters_content:
            body = process_chapter(num, title, chapters_content[num])
            filepath = os.path.join(OUTDIR, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(body)
            print(f"  ✓ Wrote {filename} ({len(body)} chars, {body.count(chr(10))} lines)")
        else:
            print(f"  ✗ Chapter {num} not found in source!")
    
    # Write README.md (one level up from docs/)
    readme_content = build_readme(CHAPTERS)
    readme_path = os.path.join(os.path.dirname(OUTDIR), "README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"\n  ✓ Wrote README.md ({len(readme_content)} chars)")

if __name__ == '__main__':
    main()
