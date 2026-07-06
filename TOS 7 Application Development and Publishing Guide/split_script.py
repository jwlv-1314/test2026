#!/usr/bin/env python3
"""Split the TOS 7 development guide into chapter files with navigation (English edition)."""

import re
import os

# Paths — adjust these to match your environment
SOURCE = "/Volume1/public/apptest/TOS 7 应用开发与上架指南.md"
OUTDIR = "/Volume1/public/apptest/应用开发指南单独章节-英文版/docs"

# Chapter metadata: (number, short_name, filename)
CHAPTERS = [
    (1,  "Overview",                  "01_Overview.md"),
    (2,  "Architecture Strategy",     "02_Architecture_Strategy.md"),
    (3,  "Quick Start",               "03_Quick_Start.md"),
    (4,  "Package Specification",     "04_Package_Specification.md"),
    (5,  "ABI Compatibility",         "05_ABI_Compatibility.md"),
    (6,  "Development Environment",   "06_Development_Environment.md"),
    (7,  "Application Types",         "07_Application_Types.md"),
    (8,  "Deb Development",           "08_Deb_Development.md"),
    (9,  "Docker Development",        "09_Docker_Development.md"),
    (10, "Permission Model",          "10_Permission_Model.md"),
    (11, "Package Signing Security",  "11_Package_Signing.md"),
    (12, "Best Practices",            "12_Best_Practices.md"),
    (13, "Local Testing & Debugging", "13_Local_Testing.md"),
    (14, "CI/CD Guide",               "14_CICD_Guide.md"),
    (15, "Publishing Process",        "15_Publishing_Process.md"),
    (16, "Review Standards",          "16_Review_Standards.md"),
    (17, "Operations & Delisting",    "17_Operations_Delisting.md"),
    (18, "Commercialization & Donations", "18_Commercialization_Donations.md"),
    (19, "FAQ",                       "19_FAQ.md"),
    (20, "Appendix",                  "20_Appendix.md"),
]

def read_source():
    """Read the full source document."""
    with open(SOURCE, 'r', encoding='utf-8') as f:
        return f.read()

def find_chapter_boundaries(content):
    """Find start and end line of each chapter in the source document."""
    lines = content.split('\n')

    # Locate all chapter heading lines (## N. ...)
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
        parts.append(f"← [Previous: {prev_ch[1]}]({prev_ch[2]})")

    if current < total:
        next_ch = CHAPTERS[current]
        parts.append(f"[Next: {next_ch[1]}]({next_ch[2]}) →")

    parts.append(f"[📖 Return to Contents](../README.md)")

    return "\n\n---\n\n" + " &nbsp;&nbsp;|&nbsp;&nbsp; ".join(parts) + "\n"

def process_chapter(num, title, content_lines):
    """Process a chapter: ensure proper H1 heading and append navigation."""
    lines = content_lines.split('\n')

    # Replace original ## heading with # heading
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
    """Generate the English README.md index file."""
    lines = []
    lines.append("# TOS 7 Application Development and Publishing Guide")
    lines.append("")
    lines.append("**Version:** v2.7  ")
    lines.append("**Last Updated:** 2026-05-27  ")
    lines.append("**Applicable Platform:** TOS 7.0 and above  ")
    lines.append("**Target Audience:** Global third-party developers, independent developers, enterprise partners  ")
    lines.append("")
    lines.append("> 📢 This document is currently based on TOS 7.0. Compatibility with subsequent TOS 7.x versions will be maintained.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 🚀 Quick Start")
    lines.append("")
    lines.append("| Scenario | Recommended Reading |")
    lines.append("|------|---------|")
    lines.append("| First time with TOS app development | [📘 Chapter 3 · Quick Start](docs/03_Quick_Start.md) — Run through the process in 5 minutes |")
    lines.append("| Understanding the overall architecture | [📘 Chapter 2 · Architecture Strategy](docs/02_Architecture_Strategy.md) — Container-first strategy |")
    lines.append("| Developing Deb apps | [📘 Chapter 8 · Deb Development](docs/08_Deb_Development.md) — Complete specification |")
    lines.append("| Developing Docker apps | [📘 Chapter 9 · Docker Development](docs/09_Docker_Development.md) — Docker Compose guide |")
    lines.append("| Preparing for publishing | [📘 Chapter 15 · Publishing Process](docs/15_Publishing_Process.md) — Submit for review |")
    lines.append("| Encountering issues | [📘 Chapter 19 · FAQ](docs/19_FAQ.md) — Frequently asked questions |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 📑 Full Table of Contents")
    lines.append("")

    for num, title, filename in chapters:
        lines.append(f"| {num:02d} | [{title}](docs/{filename}) |")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 📂 Repository Structure")
    lines.append("")
    lines.append("```")
    lines.append("docs/")
    lines.append("├── README.md            ← You are here")
    for num, title, filename in chapters:
        lines.append(f"├── {filename}")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 🔗 Related Resources")
    lines.append("")
    lines.append("- [TNAS Developer Platform](https://developer.terra-master.com) (Coming soon)")
    lines.append("- [Deb App Template (Single Package)](https://github.com/terra-master/app-template-deb)")
    lines.append("- [Deb App Template (Dual Package)](https://github.com/terra-master/app-template-deb-dual)")
    lines.append("- [Docker App Template](https://github.com/terra-master/app-template-docker)")
    lines.append("- [TOS App Center](https://terra-master.com)")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*This document is generated by splitting [TOS 7 Application Development and Publishing Guide], with each chapter maintained independently.*")

    return '\n'.join(lines) + '\n'

def main():
    os.makedirs(OUTDIR, exist_ok=True)

    content = read_source()
    chapters_content = find_chapter_boundaries(content)

    print(f"Found {len(chapters_content)} chapters in source")

    # Write each chapter file (translated content goes here — this script only handles splitting;
    # actual translation must be done beforehand or via an external translation step.)
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
