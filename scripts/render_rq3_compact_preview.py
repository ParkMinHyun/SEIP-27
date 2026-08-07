"""Render reviewer-facing PNG previews of the current compact RQ3 artifacts.

The preview mirrors the content hierarchy but is not a final LaTeX render.
Definitions, timeout-measurement validity, the two-Draft target-or-next audit,
and the closed-loop counterfactual limit are documented in
docs/rq3-current.md.
"""

from __future__ import annotations

import csv
import html
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/rq3/policy"
COORD = ROOT / "data/rq3/coordination"
TMP = Path(tempfile.gettempdir())


def read_csv(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def text(x, y, value, size=16, anchor="middle", weight="normal", fill="#111", rotate=None):
    transform = f' transform="rotate({rotate} {x} {y})"' if rotate is not None else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" '
            f'font-weight="{weight}" fill="{fill}"{transform}>{html.escape(str(value))}</text>')


def line(x1, y1, x2, y2, stroke="#888", width=1, arrow=False):
    marker = ' marker-end="url(#arrow)"' if arrow else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{stroke}" stroke-width="{width}"{marker}/>')


def box(buffer, x, y, width, height, lines, fill="white"):
    buffer.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="5" '
                  f'fill="{fill}" stroke="#777" stroke-width="1.2"/>')
    start = y + height / 2 - (len(lines) - 1) * 9 + 5
    for index, value in enumerate(lines):
        buffer.append(text(x + width / 2, start + index * 18, value, 13))


def render_table():
    rows = [
        ("group", "Targeting", "", ""),
        ("row", "Analyzed / paced transitions", "1,920 / 411", "1,861 / 471"),
        ("row", "Activation with >40% retrospective spare, % [n]", "1.4 [652]", "1.0 [623]"),
        ("row", "Activation at projected overrun, % [n]", "77.2 [79]", "68.8 [141]"),
        ("group", "Admission–pacing coordination", "", ""),
        ("row", "Transitions with pacing-only d*exec > 0", "79", "140"),
        ("row", "Pacing covers realized-work envelope", "53/79 (67.1%)", "83/140 (59.3%)"),
        ("row", "Admission-flexible band", "26/79 (32.9%)", "43/140 (30.7%)"),
        ("row", "Observed demotion, target / target-or-next",
         "7/26 (26.9%) / 21/26 (80.8%)", "17/43 (39.5%) / 31/43 (72.1%)"),
        ("row", "Flexible-band realized margin, min / P5 (ms)", "134 / 183", "36 / 84"),
        ("row", "Below mandatory floor", "0/79 (0.0%)", "14/140 (10.0%)"),
        ("row", "Floor miss: zero delay / target demoted", "—", "11/14 / 14/14"),
        ("row", "Floor miss: backlog underestimated / headroom rose", "—", "14/14 / 12/14"),
        ("row", "Floor-miss outcome: target / next min margin (ms) / timeout", "—", "307 / 276 / 0/14"),
        ("row", "Potential delay avoided, P50 / P95 (ms)", "72 / 208", "131 / 443"),
        ("group", "Work conservation", "", ""),
        ("row", "Applied delay overlapping measured backlog (%)", "100.0", "98.7"),
        ("row", "Waits longer than the backlog, d > B", "0/411", "8/471"),
        ("group", "Responsiveness cost, P50 / P95", "", ""),
        ("row", "Per paced capture (ms)", "381 / 823", "278 / 1,180"),
        ("row", "Per 30-shot burst (% of elapsed time)", "18.1 / 24.5", "9.8 / 29.7"),
        ("row", "Bursts with no pacing", "19/70", "13/69"),
    ]
    body = []
    for kind, metric, normal, memory in rows:
        if kind == "group":
            body.append(f'<tr class="group"><th colspan="3">{html.escape(metric)}</th></tr>')
        else:
            body.append(f'<tr><td>{html.escape(metric)}</td><td>{html.escape(normal)}</td>'
                        f'<td>{html.escape(memory)}</td></tr>')
    output = f'''<!doctype html><html><head><meta charset="utf-8"><style>
      *{{box-sizing:border-box}}body{{margin:0;background:white;color:#111;font-family:"Times New Roman",serif}}
      .page{{width:900px;margin:0 auto;padding:24px 34px 30px}}.caption{{font-size:21px;line-height:1.18;text-align:center;margin-bottom:12px}}
      table{{width:100%;border-collapse:collapse;font-size:16px;line-height:1.08}}thead{{border-top:3px solid #111;border-bottom:1.7px solid #111}}
      thead th{{padding:7px}}thead th:first-child{{text-align:left;width:50%}}thead th:not(:first-child){{width:25%;text-align:center}}
      td{{padding:4px 6px;vertical-align:top}}td:first-child{{text-align:left}}td:not(:first-child){{text-align:center}}
      .group th{{text-align:left;padding:8px 0 3px;border-top:1.2px solid #777}}tbody tr:first-child th{{border-top:none}}tbody{{border-bottom:3px solid #111}}
      .note{{margin-top:9px;font-size:13px;line-height:1.16;text-align:justify}}
    </style></head><body><div class="page"><div class="caption"><b>Table X.</b> RQ3: Pacing targeting, admission-aware sizing and action,<br>
      work conservation, and responsiveness cost on the S26 Ultra.</div>
      <table><thead><tr><th>Metric</th><th>12MP<br>normal</th><th>24MP<br>memory pressure</th></tr></thead><tbody>{''.join(body)}</tbody></table>
      <div class="note">The deployed 2C horizon represents the Draft that starts after the pacing decision and the next capture's Draft released by that delay. Target-or-next therefore audits whether admission demoted either Draft in this horizon; it does not causally attribute the next decision to the current delay. The 14 floor misses occurred in four 24MP bursts: all targets were demoted, target/next margins stayed at least 307/276 ms, and no floor miss produced an actual Capture Timeout. Backlog was underestimated in 14/14 and headroom rose in 12/14 during median 4.78 s queue residence. Timeout-measurement-error records are invalid observations; no valid analyzed run timed out.</div>
      </div></body></html>'''
    path = TMP / "rq3_compact_table_v2.html"
    path.write_text(output)
    return path


def render_figure():
    normal = read_csv(POLICY / "band_activation_12mp_normal.csv")
    memory = read_csv(POLICY / "band_activation_24mp_memory.csv")
    envelope = {row["condition"]: row for row in read_csv(COORD / "envelope_share.csv")}
    svg = ['<rect width="1800" height="760" fill="white"/>',
           '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#777"/></marker><pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="7" stroke="#777" stroke-width="2"/></pattern></defs>']

    # Panel (a).
    x, y, width, height = 90, 90, 390, 320
    map_x = lambda value: x + (value + .6) / 4.2 * width
    map_y = lambda value: y + height - value / 100 * height
    for value in [0, 25, 50, 75, 100]:
        svg += [line(x, map_y(value), x + width, map_y(value), "#e3e3e3"),
                text(x - 9, map_y(value) + 5, value, 13, "end")]
    for index, label in enumerate([">40", "20–40", "0–20", "≤0"]):
        svg += [line(map_x(index), y, map_x(index), y + height, "#ededed"),
                text(map_x(index), y + height + 23, label, 13)]
    svg += [f'<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="none" stroke="#444"/>',
            text(x + width / 2, y - 18, "(a) Targeted activation", 19, weight="bold"),
            text(x + width / 2, y + height + 52, "Retrospective spare (% of budget)", 15),
            text(x - 54, y + height / 2, "Activation rate (%)", 15, rotate=-90)]
    for index, (left, right) in enumerate(zip(normal, memory)):
        for offset, row, fill, stroke, dashed in [(-.13, left, "#555", "#111", False),
                                                   (.13, right, "white", "#777", True)]:
            xx, yy, zero = map_x(index + offset), map_y(float(row["activation_pct"])), map_y(0)
            dash = ' stroke-dasharray="4 2"' if dashed else ""
            svg.append(f'<rect x="{xx - 12}" y="{yy}" width="24" height="{zero - yy}" fill="{fill}" stroke="{stroke}"{dash}/>')
            low, high = map_y(float(row["act_lo_pct"])), map_y(float(row["act_hi_pct"]))
            svg += [line(xx, low, xx, high, "#444"), line(xx - 5, low, xx + 5, low, "#444"),
                    line(xx - 5, high, xx + 5, high, "#444")]
    svg += ['<rect x="108" y="104" width="15" height="10" fill="#555" stroke="#111"/><text x="130" y="114" font-size="13">12MP normal</text>',
            '<rect x="108" y="122" width="15" height="10" fill="white" stroke="#777" stroke-dasharray="3 2"/><text x="130" y="132" font-size="13">24MP memory pressure</text>']

    # Panel (b).
    svg.append(text(900, 72, "(b) Boundary mismatch mechanisms", 19, weight="bold"))
    box(svg, 605, 110, 135, 70, ["Backlog risk at", "pacing decision"])
    box(svg, 820, 110, 170, 70, ["Admission later demoted", "15/15 targets;", "55/58 ahead"], "#f0f0f0")
    box(svg, 1070, 110, 150, 70, ["Paced, yet >40%", "spare: 15/1,275"])
    svg += [line(740, 145, 818, 145, "#777", 1.5, True), text(779, 136, "pace", 12),
            line(990, 145, 1068, 145, "#777", 1.5, True)]
    box(svg, 605, 270, 135, 70, ["No pace from", "duration history"])
    box(svg, 820, 270, 170, 70, ["Queued 5.14 s;", "headroom rose", "53/62"], "#f0f0f0")
    box(svg, 1070, 270, 150, 70, ["Backlog underestimated", "61/62; projected", "overrun 62/220"])
    svg += [line(740, 305, 818, 305, "#777", 1.5, True), line(990, 305, 1068, 305, "#777", 1.5, True),
            text(905, 377, "Admission demoted 29/62 targets: partial backstop", 13)]

    # Panel (c).
    x, y, width = 1325, 120, 380
    svg.append(text(x + width / 2, 72, "(c) Admission-aware sizing and action", 19, weight="bold"))
    for value in [0, 25, 50, 75, 100]:
        xx = x + value / 100 * width
        svg += [line(xx, 105, xx, 365, "#e6e6e6"), text(xx, 388, value, 13)]
    for condition, yy, label in [("12mp_normal", 170, "12MP normal"),
                                  ("24mp_memory", 300, "24MP mem.")]:
        row = envelope[condition]
        portions = [float(row["full_covered_pct"]), float(row["admission_flexible_pct"]),
                    float(row["below_mandatory_pct"])]
        widths = [portion / 100 * width for portion in portions]
        starts = [x, x + widths[0], x + widths[0] + widths[1]]
        svg += [text(x - 12, yy + 6, label, 13, "end"),
                f'<rect x="{starts[0]}" y="{yy - 18}" width="{widths[0]}" height="36" fill="#555" stroke="#333"/>',
                f'<rect x="{starts[1]}" y="{yy - 18}" width="{widths[1]}" height="36" fill="#d0d0d0" stroke="#777"/>']
        if widths[2]:
            svg.append(f'<rect x="{starts[2]}" y="{yy - 18}" width="{widths[2]}" height="36" fill="url(#hatch)" stroke="#777"/>')
        svg.append(text(starts[0] + widths[0] / 2, yy + 5, row["full_count"], 13, weight="bold", fill="white"))
        demotion = "7/21" if condition == "12mp_normal" else "17/31"
        svg.append(text(starts[1] + widths[1] / 2, yy + 5,
                        f'{row["flexible_count"]} [{demotion}]', 12, weight="bold"))
        if widths[2]:
            center = starts[2] + widths[2] / 2
            svg += [f'<rect x="{center - 9}" y="{yy - 11}" width="18" height="16" fill="white"/>',
                    text(center, yy + 3, row["below_count"], 13, weight="bold")]
    svg += [text(x + width / 2, 424, "Transitions with pacing-only realized-work envelope > 0 (%)", 15),
            '<rect x="1335" y="93" width="14" height="10" fill="#555"/><text x="1356" y="103" font-size="12">Pacing covers realized work</text>',
            '<rect x="1502" y="93" width="14" height="10" fill="#d0d0d0"/><text x="1523" y="103" font-size="12">Admission-flexible</text>',
            '<rect x="1635" y="93" width="14" height="10" fill="url(#hatch)" stroke="#777"/><text x="1656" y="103" font-size="12">Below floor</text>',
            text(x + width / 2, 450, "Brackets: target / target-or-next demotions", 11),
            text(x + width / 2, 468, "24MP floor: 14/14 demoted; margin ≥307 ms; timeout 0/14", 11)]

    caption = [
        "Figure X. RQ3 admission–pacing coordination. (a) Online activation against retrospectively reconstructed pressure.",
        "(b) Pacing can precede admission demotion that later creates spare; queue residence and rising headroom are consistent with",
        "slowdown after a no-pacing decision and backlog under-estimation. Admission provides a partial backstop.",
        "(c) The 2C horizon covers the post-decision Draft and the next capture's Draft released by the delay.",
        "Brackets report target / target-or-next demotion; all 14 floor misses kept ≥307 ms margin and had no timeout.",
    ]
    for index, value in enumerate(caption):
        svg.append(text(900, 545 + index * 24, value, 16, weight="bold" if index == 0 else "normal"))
    output = ('<!doctype html><html><head><meta charset="utf-8"><style>body{margin:0;background:white;'
              'font-family:"Times New Roman",serif}svg{display:block}</style></head><body>'
              '<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="760">' + "".join(svg) +
              "</svg></body></html>")
    path = TMP / "rq3_compact_figure_v2.html"
    path.write_text(output)
    return path


if __name__ == "__main__":
    print(render_table())
    print(render_figure())
