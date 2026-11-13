"""Builds the Legal section's document pages from Markdown.

  python3 legal/build.py

Sources: legal/_src/<project>/<doc>.md (the first line is "# Title"; a line
"Effective: <date>" is shown under it). Output: legal/<project>/<doc>.html,
and legal/<project>/index.html lists them in DOCS order. Jekyll skips folders
that start with "_", so the sources are not published. Refuses to build while
a "[CONFIRM" marker is left: those are questions for the owner.
"""

import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).parent

PROJECTS = {
    "outta": {
        "name": "OUTTA",
        "lead": "Clubs, a Welcome Circle and new friends in a new city. Abu Dhabi first.",
        "contact": "alexmfv1@gmail.com",
        "docs": [
            ("privacy", "Privacy Policy", "What OUTTA collects, why, who sees it and your rights"),
            ("terms", "Terms of Use", "The rules for using OUTTA"),
            ("community-guidelines", "Community Guidelines", "How we treat each other, online and in person"),
            ("child-safety", "Child Safety Standards", "Our zero-tolerance standards against child sexual abuse and exploitation"),
            ("delete-account", "Delete your account", "How to delete your account and data, with or without the app"),
        ],
    },
    "simple-pong": {
        "name": "Simple Pong!",
        "lead": "Classic arcade Pong with single-player and local two-player modes.",
        "contact": "alexmfv1@gmail.com",
        "docs": [
            ("privacy", "Privacy Policy", "What Simple Pong! collects, why, and your rights"),
        ],
    },
}

HEAD = """<meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&family=Montserrat:wght@600&display=swap" rel="stylesheet">"""


def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(
        r"(?<![\w.:/\">])([\w.+-]+@[\w-]+\.[\w.]+\w)",
        r'<a href="mailto:\1">\1</a>',
        text,
    )
    text = re.sub(
        r'(?<![="\w>])(https?://[^\s<]+[^\s<.,;:)])',
        r'<a href="\1">\1</a>',
        text,
    )
    return text


def markdown(lines):
    out, para, i = [], [], 0

    def flush():
        if para:
            # Label lines ("**App:** OUTTA") stay one per line.
            joiner = "<br>" if all(l.startswith("**") for l in para) else " "
            out.append("<p>" + joiner.join(inline(l) for l in para) + "</p>")
            para.clear()

    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            flush()
            i += 1
            continue
        heading = re.match(r"^(#{2,4})\s+(.*)$", line)
        if heading:
            flush()
            level = len(heading.group(1))
            title = heading.group(2).strip()
            anchor = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
            out.append(f'<h{level} id="{anchor}">{inline(title)}</h{level}>')
            i += 1
            continue
        if re.match(r"^(-{3,}|\*{3,})$", line.strip()):
            flush()
            i += 1
            continue
        if line.lstrip().startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.match(r"^:?-+:?$", c) for c in cells):
                    rows.append(cells)
                i += 1
            table = ["<table>", "<thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in rows[0]) + "</tr></thead>", "<tbody>"]
            for row in rows[1:]:
                table.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>")
            out.append("\n".join(table + ["</tbody>", "</table>"]))
            continue
        item = re.match(r"^(\s*)([-*]|\d+[.)])\s+(.*)$", line)
        if item:
            flush()
            ordered = item.group(2)[0].isdigit()
            tag = "ol" if ordered else "ul"
            items = []
            while i < len(lines):
                m = re.match(r"^(\s*)([-*]|\d+[.)])\s+(.*)$", lines[i].rstrip())
                if m and m.group(2)[0].isdigit() == ordered and len(m.group(1)) < 2:
                    items.append([m.group(3)])
                    i += 1
                elif m and len(m.group(1)) >= 2 and items:
                    items[-1].append(("SUB", m.group(2)[0].isdigit(), m.group(3)))
                    i += 1
                elif lines[i].startswith("  ") and lines[i].strip() and items:
                    items[-1][0] += " " + lines[i].strip()
                    i += 1
                else:
                    break
            parts = [f"<{tag}>"]
            for entry in items:
                text, subs = entry[0], entry[1:]
                body = inline(text)
                if subs:
                    sub_tag = "ol" if subs[0][1] else "ul"
                    body += f"<{sub_tag}>" + "".join(f"<li>{inline(s[2])}</li>" for s in subs) + f"</{sub_tag}>"
                parts.append(f"<li>{body}</li>")
            parts.append(f"</{tag}>")
            out.append("".join(parts))
            continue
        if line.startswith(">"):
            flush()
            out.append("<p><strong>" + inline(line.lstrip("> ")) + "</strong></p>")
            i += 1
            continue
        para.append(line.strip())
        i += 1
    flush()
    return "\n".join(out)


def page(title, description, crumbs, body, css="../legal.css", home="../../"):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    {HEAD}
    <title>{html.escape(title)}</title>
    <meta name="description" content="{html.escape(description)}">
    <link rel="stylesheet" href="{css}">
</head>
<body>
    <header class="topbar"><div class="container">
        <a class="home" href="{home}">Alexandre Valente</a>
        <nav class="crumbs" aria-label="Breadcrumb">{crumbs}</nav>
    </div></header>
    <main><div class="container">
{body}
    </div></main>
    <footer><div class="container">© 2026 Alexandre Valente</div></footer>
</body>
</html>
"""


def build():
    problems = []
    for key, project in PROJECTS.items():
        out_dir = ROOT / key
        out_dir.mkdir(parents=True, exist_ok=True)
        src_dir = ROOT / "_src" / key
        cards = []
        for doc, title, desc in project["docs"]:
            source = src_dir / f"{doc}.md"
            if not source.exists():
                problems.append(f"missing {source}")
                continue
            text = source.read_text(encoding="utf-8")
            for n, line in enumerate(text.splitlines(), 1):
                if "[CONFIRM" in line:
                    problems.append(f"{source.name}:{n}: {line.strip()[:120]}")
            lines = text.splitlines()
            if lines and lines[0].startswith("# "):
                lines = lines[1:]
            effective = ""
            for n, line in enumerate(lines[:6]):
                m = re.match(r"^\*{0,2}(Effective|Last updated)[^:]*:\*{0,2}\s*(.+)$", line.strip(), re.I)
                if m:
                    effective = m.group(2).strip(" *")
                    lines.pop(n)
                    break
            meta = f'<span class="meta">{html.escape(title)}' + (f" · Effective {html.escape(effective)}" if effective else "") + "</span>"
            body = f"""        <div class="doc-head">
            <img src="icon.png" alt="" width="48" height="48">
            <div><div class="app">{project['name']}</div>{meta}</div>
        </div>
        <h1>{html.escape(title)}</h1>
        <article class="doc">
{markdown(lines)}
        </article>"""
            crumbs = f'<a href="../">Legal</a> › <a href="./">{project["name"]}</a> › {html.escape(title)}'
            (out_dir / f"{doc}.html").write_text(page(f"{title} · {project['name']}", f"{project['name']} {title}", crumbs, body), encoding="utf-8")
            cards.append(f"""            <li><a class="card" href="{doc}.html">
                <span><span class="title">{html.escape(title)}</span><span class="desc">{html.escape(desc)}</span></span>
                <span class="arrow" aria-hidden="true">›</span>
            </a></li>""")
        body = f"""        <div class="project-head">
            <img src="icon.png" alt="{project['name']} app icon" width="96" height="96">
            <div><h1>{project['name']}</h1><p class="lead">{html.escape(project['lead'])}</p></div>
        </div>
        <ul class="cards">
{chr(10).join(cards)}
        </ul>
        <p class="contact">Questions, requests or reports: <a href="mailto:{project['contact']}">{project['contact']}</a></p>"""
        crumbs = f'<a href="../">Legal</a> › {project["name"]}'
        (out_dir / "index.html").write_text(page(f"{project['name']} · Legal", f"Legal documents for {project['name']}.", crumbs, body), encoding="utf-8")
    if problems:
        print("Not built cleanly:\n  " + "\n  ".join(problems))
        sys.exit(1)
    print("Built.")


if __name__ == "__main__":
    build()
