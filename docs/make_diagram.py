"""Generate docs/architecture.excalidraw (open at excalidraw.com) and a preview SVG.

Run: python3 docs/make_diagram.py
"""
import json
import random
from pathlib import Path

OUT = Path(__file__).parent
random.seed(7)

# Colors (Excalidraw palette)
BLUE, GREEN, ORANGE, PURPLE, GREY, RED = "#a5d8ff", "#b2f2bb", "#ffec99", "#d0bfff", "#e9ecef", "#ffc9c9"

boxes = []   # (id, x, y, w, h, fill, text, dashed)
arrows = []  # (points [(x,y),...], label, dashed)
labels = []  # (x, y, text, size, color)


def box(id, x, y, w, h, fill, text, dashed=False):
    boxes.append((id, x, y, w, h, fill, text, dashed))
    return dict(x=x, y=y, w=w, h=h, cx=x + w / 2, cy=y + h / 2, b=y + h, r=x + w)


def arrow(points, label="", dashed=False):
    arrows.append((points, label, dashed))


def label(x, y, text, size=16, color="#495057"):
    labels.append((x, y, text, size, color))


# ---- layout ---------------------------------------------------------------
label(40, 10, "Morning Market Brief: multi-agent architecture", 28, "#1e1e1e")
label(40, 50, "Orchestrator-worker + parallel fan-out per category + sequential merge", 16)

cron = box("cron", 40, 100, 220, 70, GREY, "cron (weekdays 7:00)\nrun_brief.sh")
cli = box("cli", 320, 100, 300, 70, GREY, "claude -p (headless)\n--allowedTools allow-list")
arrow([(cron["r"], cron["cy"]), (cli["x"], cli["cy"])])

orch = box("orch", 200, 220, 760, 80, BLUE,
           "ORCHESTRATOR: morning-brief skill (main agent)\nplans stages, launches workers in parallel, handles failures")
arrow([(cli["cx"], cli["b"]), (cli["cx"], orch["y"])])

# Parallel frame
frame = box("frame", 40, 340, 1080, 440, "transparent", "", dashed=True)
label(60, 350, "PARALLEL: one lane per category in sources.yaml (issued in the same message)", 16, "#1971c2")

lanes = {}
for i, (cat, n) in enumerate([("general", "~110 items / 6 sources"), ("semis", "~8 items / 3 sources")]):
    x0 = 80 + i * 520
    f = box(f"fetch_{cat}", x0, 390, 400, 70, GREEN, f"fetch.py --category {cat}\n-> data/{cat}.json  ({n})")
    w = box(f"write_{cat}", x0, 510, 400, 70, ORANGE, f"market-analyst ({cat})\nwrites section | Read, Write")
    c = box(f"check_{cat}", x0, 630, 400, 70, PURPLE, f"brief-checker ({cat})\nfact-checks vs data/{cat}.json | Read, Grep")
    arrow([(f["cx"], f["b"]), (w["cx"], w["y"])], "JSON path, focus, budget")
    arrow([(w["cx"], w["b"]), (c["cx"], c["y"])], "section path + JSON path only")
    # revise loop (FAIL -> analyst, max 1)
    arrow([(c["r"], c["cy"]), (c["r"] + 30, c["cy"]), (w["r"] + 30, w["cy"]), (w["r"], w["cy"])],
          "FAIL: issues\n(max 1 revision)", dashed=True)
    arrow([(orch["cx"] - 200 + i * 400, orch["b"]), (f["cx"], f["y"])])
    lanes[cat] = c

editor = box("editor", 310, 830, 540, 80, ORANGE,
             "editor\nmerges sections, removes duplicates, cuts to 300 words | Read, Write")
for cat, c in lanes.items():
    arrow([(c["cx"], c["b"]), (editor["cx"] + (-120 if cat == "general" else 120), editor["y"])],
          "PASS section")

final = box("final", 310, 960, 540, 70, PURPLE, "brief-checker (final)\nvs ALL data/*.json: catches editor changes")
arrow([(editor["cx"], editor["b"]), (final["cx"], final["y"])])
arrow([(final["r"], final["cy"]), (final["r"] + 40, final["cy"]), (editor["r"] + 40, editor["cy"]), (editor["r"], editor["cy"])],
      "FAIL: 1 fix", dashed=True)

out = box("out", 380, 1080, 400, 60, BLUE, "briefs/YYYY-MM-DD.md\n(+ briefs/sections/*)")
arrow([(final["cx"], final["b"]), (out["cx"], out["y"])])

# Side: human-triggered skill + config
src = box("src", 1180, 390, 300, 70, GREEN, "sources.yaml\ncategories = top-level keys")
add = box("add", 1180, 230, 300, 70, BLUE, "add-news-source skill\n(human-triggered, + check_feed.py)")
arrow([(add["cx"], add["b"]), (src["cx"], src["y"])], "verified entries")
arrow([(src["x"], src["cy"]), (frame["r"], src["cy"])])
label(src["x"], src["b"] + 6, "<- read by fetch.py", 13)

fail = box("fail", 1180, 540, 300, 440, RED,
           "FAILURE HANDLING\n\n"
           "Source fails: retry fetch x3,\nthen continue + list as missing\n\n"
           "Category has 0 items: drop it,\n'Not included' in footer\n\n"
           "Check still FAILs after revision:\nkeep section + warning line\n\n"
           "Writer wrote no file: retry once,\nthen drop category\n\n"
           "Editor fails: orchestrator\nconcatenates sections\n\n"
           "All categories fail: write\n'Brief not generated' + errors")

W, H = 1520, 1170

# ---- Excalidraw -------------------------------------------------------------
def base(id, type, x, y, w, h, **kw):
    e = dict(id=id, type=type, x=x, y=y, width=w, height=h, angle=0, strokeColor="#1e1e1e",
             backgroundColor="transparent", fillStyle="solid", strokeWidth=2, strokeStyle="solid",
             roughness=1, opacity=100, groupIds=[], frameId=None, roundness=None,
             seed=random.randint(1, 2**31), version=1, versionNonce=random.randint(1, 2**31),
             isDeleted=False, boundElements=None, updated=1, link=None, locked=False)
    e.update(kw)
    return e


def text_el(id, x, y, w, h, text, size, container=None, align="left", color="#1e1e1e"):
    return base(id, "text", x, y, w, h, text=text, originalText=text, fontSize=size, fontFamily=2,
                textAlign=align, verticalAlign="middle" if container else "top", containerId=container,
                lineHeight=1.25, autoResize=True, strokeColor=color)


els = []
for id, x, y, w, h, fill, text, dashed in boxes:
    r = base(id, "rectangle", x, y, w, h, backgroundColor=fill, roundness={"type": 3},
             strokeStyle="dashed" if dashed else "solid",
             strokeColor="#1971c2" if dashed else "#1e1e1e")
    els.append(r)
    if text:
        lines = text.split("\n")
        size = 15 if id != "fail" else 14
        th = len(lines) * size * 1.25
        tid = id + "_t"
        r["boundElements"] = [{"type": "text", "id": tid}]
        els.append(text_el(tid, x + 8, y + (h - th) / 2, w - 16, th, text, size, container=id, align="left" if id == "fail" else "center"))
for n, (pts, lab, dashed) in enumerate(arrows):
    x0, y0 = pts[0]
    rel = [[px - x0, py - y0] for px, py in pts]
    xs, ys = [p[0] for p in rel], [p[1] for p in rel]
    a = base(f"a{n}", "arrow", x0, y0, max(xs) - min(xs), max(ys) - min(ys), points=rel,
             lastCommittedPoint=None, startBinding=None, endBinding=None, startArrowhead=None,
             endArrowhead="arrow", strokeStyle="dashed" if dashed else "solid",
             strokeColor="#e03131" if dashed else "#1e1e1e", roundness={"type": 2})
    els.append(a)
    if lab:
        mx = (pts[0][0] + pts[-1][0]) / 2 if len(pts) == 2 else pts[1][0] + 8
        my = (pts[0][1] + pts[-1][1]) / 2 if len(pts) == 2 else (pts[1][1] + pts[2][1]) / 2
        lines = lab.split("\n")
        els.append(text_el(f"a{n}_l", mx + 8, my - len(lines) * 8, max(len(l) for l in lines) * 7.5,
                           len(lines) * 16, lab, 13, color="#e03131" if dashed else "#495057"))
for n, (x, y, t, size, color) in enumerate(labels):
    els.append(text_el(f"l{n}", x, y, len(t) * size * 0.55, size * 1.25, t, size, color=color))

(OUT / "architecture.excalidraw").write_text(json.dumps(
    {"type": "excalidraw", "version": 2, "source": "https://excalidraw.com", "elements": els,
     "appState": {"viewBackgroundColor": "#ffffff", "gridSize": None}, "files": {}}, indent=1))

# ---- SVG preview (same layout) ------------------------------------------------
DASH8 = 'stroke-dasharray="8 6"'
DASH6 = 'stroke-dasharray="6 5"'


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif">',
       '<defs><marker id="h" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 z" fill="#1e1e1e"/></marker>'
       '<marker id="hr" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 z" fill="#e03131"/></marker></defs>',
       f'<rect width="{W}" height="{H}" fill="#ffffff"/>']
for id, x, y, w, h, fill, text, dashed in boxes:
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{"none" if fill == "transparent" else fill}" '
               f'stroke="{"#1971c2" if dashed else "#1e1e1e"}" stroke-width="2" {DASH8 if dashed else ""}/>')
    if text:
        lines = text.split("\n")
        size = 15 if id != "fail" else 14
        y0 = y + h / 2 - (len(lines) - 1) * size * 1.25 / 2 + size * 0.35
        for k, l in enumerate(lines):
            anchor, tx = ("start", x + 16) if id == "fail" else ("middle", x + w / 2)
            svg.append(f'<text x="{tx}" y="{y0 + k * size * 1.25}" font-size="{size}" text-anchor="{anchor}" '
                       f'font-weight="{"bold" if k == 0 else "normal"}">{esc(l)}</text>')
for pts, lab, dashed in arrows:
    d = " ".join(f"{px},{py}" for px, py in pts)
    col = "#e03131" if dashed else "#1e1e1e"
    svg.append(f'<polyline points="{d}" fill="none" stroke="{col}" stroke-width="2" marker-end="url(#{"hr" if dashed else "h"})" '
               f'{DASH6 if dashed else ""}/>')
    if lab:
        mx = (pts[0][0] + pts[-1][0]) / 2 if len(pts) == 2 else pts[1][0] + 8
        my = (pts[0][1] + pts[-1][1]) / 2 if len(pts) == 2 else (pts[1][1] + pts[2][1]) / 2
        for k, l in enumerate(lab.split("\n")):
            svg.append(f'<text x="{mx + 8}" y="{my - len(lab.split(chr(10))) * 8 + 12 + k * 16}" font-size="13" fill="{col}">{esc(l)}</text>')
for x, y, t, size, color in labels:
    svg.append(f'<text x="{x}" y="{y + size}" font-size="{size}" fill="{color}" font-weight="{"bold" if size > 20 else "normal"}">{esc(t)}</text>')
svg.append("</svg>")
(OUT / "architecture.svg").write_text("\n".join(svg))
print("wrote", OUT / "architecture.excalidraw", "and", OUT / "architecture.svg", f"({len(els)} elements)")
