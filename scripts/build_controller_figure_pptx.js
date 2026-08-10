/*
 * Builds figures/fig_controller_interaction.pptx (Figure for Section 3.1).
 *
 * Layout contract
 * ---------------
 * The slide is four labelled regions stacked in two planes.  Each region is a
 * filled card with a tinted header strip, so a title always sits inside the
 * region it names.  The execution plane (top) runs left to right on one axis;
 * the controller plane (bottom) holds the two decision modules over the shared
 * estimator bar they both read.
 *
 * Every connector is orthogonal, unbroken, and terminates on the shape it acts
 * on -- no white knockouts over lines, no ports that stop at a border.  Lane
 * x-positions are chosen so that no lane crosses another lane, a module, or a
 * title glyph; the assertions at the bottom of this file re-check the ones that
 * are easy to break while editing.
 *
 * Icons come from figures/controller_icons/ already trimmed to their ink by
 * scripts/trim_icons.ps1; an opaque margin around one would hide the arrowhead
 * that terminates on it.
 *
 * Usage: node scripts/build_controller_figure_pptx.js [outPath]
 *        scripts/build_controller_figure.ps1   (also exports the PDF)
 */

const path = require("path");
const assert = require("assert");
const pptxgen = require("pptxgenjs");

/* ------------------------------------------------------------------ */
/* Text metrics (Helvetica/Arial AFM widths, per 1000 em)              */
/* ------------------------------------------------------------------ */

const AFM = {
  " ": 278, "!": 278, '"': 355, "#": 556, $: 556, "%": 889, "&": 667, "'": 191,
  "(": 333, ")": 333, "*": 389, "+": 584, ",": 278, "-": 333, ".": 278, "/": 278,
  0: 556, 1: 556, 2: 556, 3: 556, 4: 556, 5: 556, 6: 556, 7: 556, 8: 556, 9: 556,
  ":": 278, ";": 278, "<": 584, "=": 584, ">": 584, "?": 556, "@": 1015,
  A: 667, B: 667, C: 722, D: 722, E: 667, F: 611, G: 778, H: 722, I: 278, J: 500,
  K: 667, L: 556, M: 833, N: 722, O: 778, P: 667, Q: 778, R: 722, S: 667, T: 611,
  U: 722, V: 667, W: 944, X: 667, Y: 667, Z: 611,
  "[": 278, "\\": 278, "]": 278, "^": 469, _: 556, "`": 333,
  a: 556, b: 556, c: 500, d: 556, e: 556, f: 278, g: 556, h: 556, i: 222, j: 222,
  k: 500, l: 222, m: 833, n: 556, o: 556, p: 556, q: 556, r: 333, s: 500, t: 278,
  u: 556, v: 500, w: 722, x: 500, y: 500, z: 500,
  "{": 334, "|": 260, "}": 334, "~": 584,
};

function textWidth(text, fontSize, bold = false) {
  let em = 0;
  for (const ch of text) em += AFM[ch] ?? 556;
  return (em / 1000) * (bold ? 1.07 : 1.0) * (fontSize / 72);
}

const FIT_SLACK = 0.06; // inches of breathing room demanded on every text box

function fits(text, fontSize, bold, boxW, where) {
  const w = textWidth(text, fontSize, bold);
  assert(
    w <= boxW - FIT_SLACK,
    `${where}: "${text}" is ${w.toFixed(3)}in at ${fontSize}pt but the box is ${boxW.toFixed(3)}in`,
  );
  return w;
}

function approx(a, b, where) {
  assert(Math.abs(a - b) < 1e-6, `${where}: ${a} != ${b}`);
}

/* ------------------------------------------------------------------ */
/* Design tokens                                                       */
/* ------------------------------------------------------------------ */

const C = {
  navy: "14233E",
  slate: "526477",
  muted: "63738A",
  hairline: "D4DCE8",
  panel: "F7F9FC",
  panelHead: "E7EDF6",
  ctrl: "F2F5FA",
  ctrlHead: "DFE7F3",
  queue: "ECF1F8",
  orange: "E56E2E",
  blue: "2476D2",
  blueTint: "EFF5FE",
  modelTint: "F1F4F8",
  white: "FFFFFF",
};

const FONT = "Arial";
const FS = {
  panelTitle: 14.5,
  card: 12.5,
  queueItem: 12.0,
  sub: 12.0,
  connector: 12.0,
  module: 12.0,
  bar: 12.0,
  chip: 10.5,
};

const LINE_PT = 1.4;   // semantic connectors
const THIN_PT = 1.05;  // manifold stubs, shape outlines
const HAIR_PT = 0.75;  // panel borders

/* ------------------------------------------------------------------ */
/* Geometry                                                            */
/* ------------------------------------------------------------------ */

const SLIDE = { w: 12.0, h: 5.16 };
const AXIS = 1.40;                       // execution-plane flow axis

const PANEL = { y: 0.18, h: 2.06, head: 0.34 };
const PANEL_BOTTOM = PANEL.y + PANEL.h;  // 2.24
const CONTENT_TOP = PANEL.y + PANEL.head; // 0.52

const A = { x: 0.30, w: 2.62 };           // 0.30 -  2.92  parallel captures
const B = { x: 3.22, w: 2.88 };           // 3.22 -  6.10  pending Draft Sequences
const Cp = { x: 6.40, w: 5.30 };          // 6.40 - 11.70  one active Draft Sequence

// -- Panel A: three capture cards, staggered right and down in time.
const CARD = { w: 1.42, h: 0.38 };
const CARDS = [
  { x: 0.50, y: 0.83, suffix: "" },
  { x: 0.78, y: 1.21, suffix: "+1" },
  // Pacing pushes capture i+2 a further 0.14in along the time axis.
  { x: 1.20, y: 1.59, suffix: "+2" },
];
const BUS_X = 2.80;                      // manifold collecting every capture

// -- Panel B: the pending queue.
const QUEUE = { x: 3.38, y: 1.00, w: 2.56, h: 0.80 };
const CELL = { y: 1.17, h: 0.46 };
const CELLS = {
  arrival: { x: 3.47, w: 0.42 },
  tail: { x: 3.98, w: 0.89, suffix: "+2" },
  head: { x: 4.96, w: 0.89, suffix: "+1" },
};

// -- Panel C: the active sequence.
const TILE = 0.80;                       // every stage glyph is one 0.80in tile
const OPT = { x: 6.68, w: 2.22, y: 0.86, h: 1.08 };
const TILE_MULTI = 6.82;                 // left edge of the multi-frame tile
const TILE_ENH = 7.96;                   // left edge of the enhancement tile
const TILE_ENC = 9.24;                   // left edge of the encode tile
const TILE_IMG = 10.58;                  // left edge of the draft-image tile
const SUB_ROW = { y: 0.58, h: 0.22 };
const CAPTION_ROW = { y: 1.98, h: 0.20 };

// -- Controller plane.
const CTRL = { x: 0.30, y: 3.06, w: 11.40, h: 1.92 };
const CTRL_HEAD = 0.34;
const ROW1 = { y: 3.50, h: 0.60 };       // Pacing / Admission
const BAR = { x: 3.20, y: 4.34, w: 5.60, h: 0.50 }; // shared estimator
const PACING = { x: 0.75, w: 3.15 };
const ADMISSION = { x: 8.10, w: 3.15 };

// -- Lanes (vertical corridors). None of these may share an x with another.
const LANE = {
  available: 0.92,   // captureAvailable  : capture i+1 -> Pacing
  release: 2.47,     // delayed release   : Pacing -> capture i+2
  dispatch: 4.20,    // queued work       : queue -> estimator bar
  admit: 9.40,       // admit / skip      : Admission -> optional stages
  complete: 11.52,   // measured duration : draft image -> estimator bar
};
const ADMIT_Y = 2.94;                    // horizontal run of the admission lane
const COMPLETE_Y = BAR.y + BAR.h / 2;    // horizontal run of the feedback lane
const LABEL_ROW = { y: 2.42, h: 0.44 };

/* ------------------------------------------------------------------ */
/* Deck                                                                */
/* ------------------------------------------------------------------ */

const pptx = new pptxgen();
pptx.defineLayout({ name: "SEIP_FIGURE", width: SLIDE.w, height: SLIDE.h });
pptx.layout = "SEIP_FIGURE";
pptx.author = "SEIP 2027 paper authors";
pptx.company = "SEIP 2027";
pptx.subject = "Budget-Aware Draft Controller overview";
pptx.title = "Budget-Aware Draft Controller";
pptx.lang = "en-US";
pptx.theme = { headFontFace: FONT, bodyFontFace: FONT, lang: "en-US" };

const slide = pptx.addSlide();
slide.background = { color: C.white };
const ST = pptx.ShapeType;

/* ------------------------------------------------------------------ */
/* Primitives                                                          */
/* ------------------------------------------------------------------ */

function addText(text, x, y, w, h, opts = {}) {
  slide.addText(text, {
    x, y, w, h,
    fontFace: FONT,
    fontSize: opts.fontSize ?? FS.connector,
    color: opts.color ?? C.navy,
    bold: opts.bold ?? false,
    italic: opts.italic ?? false,
    align: opts.align ?? "center",
    valign: opts.valign ?? "middle",
    margin: 0,
    wrap: false,
    isTextBox: true,
    ...opts,
  });
}

function addRect(x, y, w, h, fill, line, lineW = THIN_PT, radius = null) {
  slide.addShape(radius === null ? ST.rect : ST.roundRect, {
    x, y, w, h,
    ...(radius === null ? {} : { rectRadius: radius }),
    fill: { color: fill },
    line: line
      ? { color: line.color, width: lineW, dashType: line.dash ?? "solid" }
      : { color: fill, transparency: 100 },
  });
}

// PowerPoint rejects a shape with a negative extent (it reports the whole file
// as corrupt), so a line that runs right-to-left or bottom-to-top is emitted
// with a positive box plus the matching flip.
function addLine(x1, y1, x2, y2, color, width = LINE_PT, arrow = "none") {
  slide.addShape(ST.line, {
    x: Math.min(x1, x2),
    y: Math.min(y1, y2),
    w: Math.abs(x2 - x1),
    h: Math.abs(y2 - y1),
    flipH: x2 < x1,
    flipV: y2 < y1,
    line: { color, width, beginArrowType: "none", endArrowType: arrow },
  });
}

// Orthogonal polyline; only the last segment carries the arrowhead.
function addPath(points, color, width = LINE_PT, arrow = true) {
  for (let i = 0; i < points.length - 1; i += 1) {
    const [x1, y1] = points[i];
    const [x2, y2] = points[i + 1];
    assert(x1 === x2 || y1 === y2, `non-orthogonal segment ${x1},${y1} -> ${x2},${y2}`);
    addLine(x1, y1, x2, y2, color, width, arrow && i === points.length - 2 ? "triangle" : "none");
  }
}

// Region card: fill + tinted header strip + title, so the title is bound to it.
function addRegion(x, y, w, h, title, opts = {}) {
  const fill = opts.fill ?? C.panel;
  const head = opts.head ?? C.panelHead;
  const border = opts.border ?? C.hairline;
  const borderW = opts.borderW ?? HAIR_PT;
  const radius = 0.05;

  addRect(x, y, w, h, fill, { color: border }, borderW, radius);
  addRect(x, y, w, CTRL_HEAD, head, null, 0, radius);
  addRect(x, y + CTRL_HEAD / 2, w, CTRL_HEAD / 2, head, null, 0);
  addLine(x, y + CTRL_HEAD, x + w, y + CTRL_HEAD, border, borderW);

  const titleW = fits(title, FS.panelTitle, true, w - 0.30 - (opts.reserve ?? 0), `${title} header`);
  // A reserved trailing badge shifts the title so the whole group stays centred.
  const shift = (opts.reserve ?? 0) / 2;
  addText(title, x - shift, y, w, CTRL_HEAD, {
    fontSize: FS.panelTitle, bold: true, color: C.navy,
  });
  return { titleW, centerX: x + w / 2 - shift };
}

// Two-line connector caption. Anchored beside its lane, never on top of it.
function addConnectorLabel(line1, line2, x, w, color, align = "left") {
  fits(line1, FS.connector, false, w, "connector label");
  if (line2) fits(line2, FS.connector, false, w, "connector label");
  addText(line1, x, LABEL_ROW.y, w, 0.20, { fontSize: FS.connector, color, align });
  if (line2) {
    addText(line2, x, LABEL_ROW.y + 0.22, w, 0.20, { fontSize: FS.connector, color, align });
  }
}

const ICON_DIR = path.join(__dirname, "..", "figures", "controller_icons");
// The PNGs are trimmed to their ink by scripts/trim_icons.ps1, so an icon can be
// dropped straight onto its tile rectangle.  If they are ever replaced with
// untrimmed art, re-run that script rather than padding here: an opaque margin
// hides the arrowheads that terminate on these tiles.
function addIconTile(name, tileX, tileY, size) {
  slide.addImage({
    path: path.join(ICON_DIR, `${name}.png`),
    x: tileX, y: tileY, w: size, h: size,
    altText: `${name.replaceAll("_", " ")} icon`,
  });
}

function captureRuns(suffix) {
  const runs = [{ text: "Capture " }, { text: "i", options: { italic: true } }];
  if (suffix) runs.push({ text: suffix });
  return runs;
}

function draftRuns(suffix) {
  const runs = [{ text: "Draft " }, { text: "i", options: { italic: true } }];
  if (suffix) runs.push({ text: suffix });
  return runs;
}

function addRuns(runs, x, y, w, h, opts = {}) {
  slide.addText(runs, {
    x, y, w, h,
    fontFace: FONT,
    fontSize: opts.fontSize ?? FS.card,
    color: opts.color ?? C.navy,
    bold: opts.bold ?? false,
    align: "center",
    valign: "middle",
    margin: 0,
    wrap: false,
    isTextBox: true,
  });
}

/* ------------------------------------------------------------------ */
/* Vector glyphs                                                       */
/* ------------------------------------------------------------------ */

function addEnhancementIcon(x, y, size) {
  addRect(x, y, size, size, C.white, { color: C.navy }, 1.05, 0.05);

  const imageX = x + size * 0.11;
  const imageY = y + size * 0.28;
  const imageW = size * 0.60;
  const imageH = size * 0.48;
  addRect(imageX, imageY, imageW / 2, imageH, C.modelTint, null);
  addRect(imageX + imageW / 2, imageY, imageW / 2, imageH, C.blueTint, null);
  slide.addShape(ST.ellipse, {
    x: x + size * 0.18, y: y + size * 0.35, w: size * 0.08, h: size * 0.08,
    fill: { color: "708CB5" }, line: { color: C.navy, width: 0.45 },
  });
  slide.addShape(ST.triangle, {
    x: x + size * 0.15, y: y + size * 0.55, w: size * 0.26, h: size * 0.15,
    fill: { color: "6A83AC" }, line: { color: C.navy, width: 0.45 },
  });
  slide.addShape(ST.triangle, {
    x: x + size * 0.37, y: y + size * 0.46, w: size * 0.28, h: size * 0.24,
    fill: { color: "405F8E" }, line: { color: C.navy, width: 0.45 },
  });
  addLine(imageX + imageW / 2, imageY, imageX + imageW / 2, imageY + imageH, C.white, 0.8);
  slide.addShape(ST.roundRect, {
    x: imageX, y: imageY, w: imageW, h: imageH, rectRadius: 0.02,
    fill: { color: C.white, transparency: 100 },
    line: { color: C.navy, width: 0.9 },
  });
  slide.addShape(ST.star4, {
    x: x + size * 0.69, y: y + size * 0.09, w: size * 0.18, h: size * 0.18,
    fill: { color: C.blue }, line: { color: C.navy, width: 0.45 },
  });
}

function addEncodeSaveIcon(x, y, size) {
  addRect(x, y, size, size, C.white, { color: C.navy }, 1.05, 0.05);
  slide.addShape(ST.can, {
    x: x + size * 0.22, y: y + size * 0.18, w: size * 0.56, h: size * 0.56,
    fill: { color: C.navy }, line: { color: C.navy, width: 1.0 },
  });
  [0.31, 0.445, 0.58].forEach((rx, index) => {
    addRect(x + size * rx, y + size * 0.42, size * 0.09, size * 0.09,
      index === 1 ? C.blue : C.white, null);
  });
}

// Estimator glyph: a dial with a needle.  Reads as an instrument, matching the
// two lever glyphs used by the decision modules.
function addEstimatorIcon(x, y, size) {
  const cx = x + size * 0.50;
  const cy = y + size * 0.54;
  const r = size * 0.44;

  slide.addShape(ST.ellipse, {
    x: cx - r, y: cy - r, w: r * 2, h: r * 2,
    fill: { color: C.white }, line: { color: C.navy, width: 1.2 },
  });
  [150, 90, 30].forEach((deg) => {
    const t = (deg * Math.PI) / 180;
    addLine(
      cx + Math.cos(t) * r * 0.66, cy - Math.sin(t) * r * 0.66,
      cx + Math.cos(t) * r * 0.90, cy - Math.sin(t) * r * 0.90,
      C.slate, 1.15,
    );
  });
  const needle = (58 * Math.PI) / 180;
  addLine(cx, cy, cx + Math.cos(needle) * r * 0.74, cy - Math.sin(needle) * r * 0.74,
    C.orange, 1.7);
  slide.addShape(ST.ellipse, {
    x: cx - size * 0.055, y: cy - size * 0.055, w: size * 0.11, h: size * 0.11,
    fill: { color: C.navy }, line: { color: C.navy, width: 0.5 },
  });
}

/* ================================================================== */
/* 1. Regions                                                          */
/* ================================================================== */

addRegion(A.x, PANEL.y, A.w, PANEL.h, "Parallel captures");
addRegion(B.x, PANEL.y, B.w, PANEL.h, "Pending Draft Sequences");
const CHIP = { w: 0.62, h: 0.22, gap: 0.14 };
const cHead = addRegion(Cp.x, PANEL.y, Cp.w, PANEL.h, "One active Draft Sequence", {
  reserve: CHIP.w + CHIP.gap,
});
addRegion(CTRL.x, CTRL.y, CTRL.w, CTRL.h, "Budget-Aware Draft Controller", {
  fill: C.ctrl, head: C.ctrlHead, border: C.navy, borderW: 1.0,
});

// "Draft i" chip riding in panel C's header names the sequence being executed.
const chipX = cHead.centerX + cHead.titleW / 2 + CHIP.gap;
addRect(chipX, PANEL.y + (CTRL_HEAD - CHIP.h) / 2, CHIP.w, CHIP.h, C.white,
  { color: C.blue }, 0.85, 0.03);
addRuns(draftRuns(""), chipX, PANEL.y + (CTRL_HEAD - CHIP.h) / 2, CHIP.w, CHIP.h,
  { fontSize: FS.chip, color: C.blue, bold: true });

/* ================================================================== */
/* 2. Execution plane                                                  */
/* ================================================================== */

// -- Panel A: parallel captures ------------------------------------------------
CARDS.forEach(({ x, y, suffix }) => {
  addRect(x, y, CARD.w, CARD.h, C.white, { color: C.navy }, 1.05, 0.045);
  addRuns(captureRuns(suffix), x, y, CARD.w, CARD.h, { fontSize: FS.card });
});
CARDS.forEach(({ suffix }) => fits(`Capture ${suffix ? `i${suffix}` : "i"}`,
  FS.card, false, CARD.w, "capture card"));

// Manifold: every capture enqueues one Draft Sequence, in capture order.
const cardMidY = CARDS.map((c) => c.y + CARD.h / 2);
addLine(CARDS[0].x + CARD.w, cardMidY[0], BUS_X, cardMidY[0], C.navy, THIN_PT);
addLine(CARDS[2].x + CARD.w, cardMidY[2], BUS_X, cardMidY[2], C.navy, THIN_PT);
addLine(BUS_X, cardMidY[0], BUS_X, cardMidY[2], C.navy, THIN_PT);
addLine(CARDS[1].x + CARD.w, AXIS, QUEUE.x, AXIS, C.navy, LINE_PT, "triangle");
// Junction dot: without it the manifold reads as a bracket, not a merge.
const JUNCTION = 0.10;
slide.addShape(ST.ellipse, {
  x: BUS_X - JUNCTION / 2, y: AXIS - JUNCTION / 2, w: JUNCTION, h: JUNCTION,
  fill: { color: C.navy }, line: { color: C.navy, width: 0.5 },
});

// -- Panel B: the pending queue -----------------------------------------------
fits("served in capture order", FS.sub, false, B.w - 0.20, "queue sub-label");
addText("served in capture order", B.x, SUB_ROW.y, B.w, SUB_ROW.h, {
  fontSize: FS.sub, color: C.muted,
});
addRect(QUEUE.x, QUEUE.y, QUEUE.w, QUEUE.h, C.queue, { color: C.navy }, 1.1, 0.05);
addRect(CELLS.arrival.x, CELL.y, CELLS.arrival.w, CELL.h, C.white,
  { color: C.slate, dash: "dash" }, 0.9, 0.035);
[CELLS.tail, CELLS.head].forEach((cell) => {
  addRect(cell.x, CELL.y, cell.w, CELL.h, C.white, { color: C.navy }, 1.0, 0.035);
  addRuns(draftRuns(cell.suffix), cell.x, CELL.y, cell.w, CELL.h, { fontSize: FS.queueItem });
  fits(`Draft i${cell.suffix}`, FS.queueItem, false, cell.w, "queue item");
});
addLine(QUEUE.x + QUEUE.w, AXIS, OPT.x, AXIS, C.navy, LINE_PT, "triangle");

// -- Panel C: the active sequence ---------------------------------------------
fits("Optional image processing", FS.sub, true, OPT.w, "optional sub-label");
addText("Optional image processing", OPT.x, SUB_ROW.y, OPT.w, SUB_ROW.h, {
  fontSize: FS.sub, bold: true, color: C.blue,
});
addRect(OPT.x, OPT.y, OPT.w, OPT.h, C.blueTint, { color: C.blue, dash: "dash" }, 1.05, 0.05);

const tileY = AXIS - TILE / 2;
addIconTile("optional_multiframe", TILE_MULTI, tileY, TILE);
addLine(TILE_MULTI + TILE, AXIS, TILE_ENH, AXIS, C.navy, THIN_PT, "triangle");
addEnhancementIcon(TILE_ENH, tileY, TILE);

addLine(OPT.x + OPT.w, AXIS, TILE_ENC, AXIS, C.navy, LINE_PT, "triangle");
addEncodeSaveIcon(TILE_ENC, tileY, TILE);
addText("Encoding & saving", TILE_ENC + TILE / 2 - 0.78, CAPTION_ROW.y, 1.56, CAPTION_ROW.h, {
  fontSize: FS.sub, color: C.navy,
});
fits("Encoding & saving", FS.sub, false, 1.56, "encode caption");

addLine(TILE_ENC + TILE, AXIS, TILE_IMG, AXIS, C.navy, LINE_PT, "triangle");
addIconTile("draft_image", TILE_IMG, tileY, TILE);
addText("Draft image", TILE_IMG + TILE / 2 - 0.48, CAPTION_ROW.y, 0.96, CAPTION_ROW.h, {
  fontSize: FS.sub, color: C.navy,
});
fits("Draft image", FS.sub, false, 0.96, "draft image caption");

/* ================================================================== */
/* 3. Controller plane                                                 */
/* ================================================================== */

const MOD_ICON = 0.46;
function addModule(x, w, iconName, line1, line2, accent) {
  addRect(x, ROW1.y, w, ROW1.h, C.white, { color: accent }, 1.15, 0.055);
  addIconTile(iconName, x + 0.15, ROW1.y + (ROW1.h - MOD_ICON) / 2, MOD_ICON);
  const textX = x + 0.15 + MOD_ICON + 0.16;
  const textW = x + w - 0.12 - textX;
  fits(line1, FS.module, true, textW, `${line1} module label`);
  fits(line2, FS.module, true, textW, `${line2} module label`);
  addText(line1, textX, ROW1.y + 0.09, textW, 0.20,
    { fontSize: FS.module, bold: true, align: "left" });
  addText(line2, textX, ROW1.y + 0.31, textW, 0.20,
    { fontSize: FS.module, bold: true, align: "left" });
}

addModule(PACING.x, PACING.w, "pacing", "Capture-Availability", "Pacing", C.orange);
addModule(ADMISSION.x, ADMISSION.w, "admission", "Remaining-Sequence", "Admission", C.blue);

// Shared estimator bar, read by both modules.
addRect(BAR.x, BAR.y, BAR.w, BAR.h, C.white, { color: C.slate }, 1.15, 0.05);
const BAR_ICON = 0.38;
const barLabel = "Workload Model & Online Duration Estimates";
const barLabelW = textWidth(barLabel, FS.bar, true);
const barGroupX = BAR.x + (BAR.w - (BAR_ICON + 0.14 + barLabelW)) / 2;
assert(barGroupX > BAR.x + 0.10, "estimator bar is too narrow for its label");
addEstimatorIcon(barGroupX, BAR.y + (BAR.h - BAR_ICON) / 2, BAR_ICON);
addText(barLabel, barGroupX + BAR_ICON + 0.14, BAR.y, barLabelW + 0.10, BAR.h, {
  fontSize: FS.bar, bold: true, align: "left",
});

// Estimates feed both decision modules.
addLine(BAR.x + 0.30, BAR.y, BAR.x + 0.30, ROW1.y + ROW1.h, C.orange, LINE_PT, "triangle");
addLine(BAR.x + BAR.w - 0.30, BAR.y, BAR.x + BAR.w - 0.30, ROW1.y + ROW1.h, C.blue, LINE_PT, "triangle");

/* ================================================================== */
/* 4. Connectors between the two planes                                */
/* ================================================================== */

// (1) capture i+1 raises captureAvailable; the callback is handed to Pacing.
addPath([[LANE.available, CARDS[1].y + CARD.h], [LANE.available, ROW1.y]], C.slate);
addConnectorLabel("captureAvailable", "callback", LANE.available + 0.10, 1.35, C.slate);

// (2) Pacing releases it later, setting the earliest start of capture i+2.
addPath([[LANE.release, ROW1.y], [LANE.release, CARDS[2].y + CARD.h]], C.orange);
addConnectorLabel("delayed release", "sets next capture", LANE.release + 0.10, 1.45, C.orange);

// (3) Dispatching a Draft Sequence refreshes the queued-work estimate.
addPath([[LANE.dispatch, QUEUE.y + QUEUE.h], [LANE.dispatch, BAR.y]], C.slate);
addConnectorLabel("queued work observed", "at dispatch", LANE.dispatch + 0.10, 1.90, C.slate);

// (4) Admission admits or skips the optional stages of the active sequence.
addPath([
  [LANE.admit, ROW1.y],
  [LANE.admit, ADMIT_Y],
  [OPT.x + OPT.w / 2, ADMIT_Y],
  [OPT.x + OPT.w / 2, OPT.y + OPT.h],
], C.blue);
addConnectorLabel("admit or skip", "optional stages", OPT.x + OPT.w / 2 + 0.12, 1.40,
  C.blue);

// (5) Completion feeds the measured duration back into the estimator.
addPath([
  [TILE_IMG + TILE, AXIS],
  [LANE.complete, AXIS],
  [LANE.complete, COMPLETE_Y],
  [BAR.x + BAR.w, COMPLETE_Y],
], C.slate);
addConnectorLabel("measured Draft", "Sequence duration", LANE.complete - 1.62, 1.52,
  C.slate, "right");

/* ================================================================== */
/* 5. Geometry assertions                                              */
/* ================================================================== */

const lanes = Object.entries(LANE);
lanes.forEach(([n1, x1], i) => lanes.slice(i + 1).forEach(([n2, x2]) => {
  assert(Math.abs(x1 - x2) > 0.60, `lanes ${n1} and ${n2} are too close (${x1}, ${x2})`);
}));

// The three region gaps in the execution plane are identical.
approx(B.x - (A.x + A.w), 0.30, "A->B gap");
approx(Cp.x - (B.x + B.w), 0.30, "B->C gap");
approx(A.x, SLIDE.w - (Cp.x + Cp.w), "execution-plane margins");

// Panel A: the captureAvailable lane must run clear of capture i+2's card.
assert(LANE.available > CARDS[1].x + 0.10, "captureAvailable lane clips capture i+1");
assert(LANE.available < CARDS[2].x - 0.20, "captureAvailable lane clips capture i+2");
assert(LANE.release > CARDS[2].x + 0.20 && LANE.release < CARDS[2].x + CARD.w - 0.10,
  "release lane must land inside capture i+2");
assert(BUS_X > CARDS[2].x + CARD.w && BUS_X < A.x + A.w - 0.10, "manifold bus escapes panel A");

// Panel B: the queue cells must sit inside the frame with even padding.
const cellsRight = CELLS.head.x + CELLS.head.w;
approx(CELLS.arrival.x - QUEUE.x, QUEUE.x + QUEUE.w - cellsRight, "queue cell padding");
approx(QUEUE.x + QUEUE.w / 2, B.x + B.w / 2, "queue frame centring");
assert(LANE.dispatch > CELLS.tail.x && LANE.dispatch < CELLS.tail.x + CELLS.tail.w,
  "dispatch lane must leave from under a queued item");

// Panel C: the stage tiles all share one size and sit on the flow axis.
[TILE_MULTI, TILE_ENH, TILE_ENC, TILE_IMG].forEach((tx, i, all) => {
  if (i > 0) assert(tx >= all[i - 1] + TILE, "stage tiles overlap");
});
approx(TILE_ENH + TILE + 0.14, OPT.x + OPT.w, "optional box right padding");
approx(TILE_MULTI - OPT.x, 0.14, "optional box left padding");
// The second stage arrow is the longer one: it keeps the two stage captions
// underneath from reading as a single run.
assert(TILE_ENC - (OPT.x + OPT.w) >= 0.30, "optional -> encode arrow is too short");
assert(TILE_IMG - (TILE_ENC + TILE) > TILE_ENC - (OPT.x + OPT.w), "stage captions will collide");
assert(LANE.complete > TILE_IMG + TILE && LANE.complete < Cp.x + Cp.w - 0.15,
  "completion lane escapes panel C");

// Controller: modules are symmetric about the slide centre and clear of lanes.
approx(PACING.x - CTRL.x, CTRL.x + CTRL.w - (ADMISSION.x + ADMISSION.w),
  "controller module symmetry");
assert(PACING.w === ADMISSION.w, "controller modules must be clones");
approx(BAR.x + BAR.w / 2, SLIDE.w / 2, "estimator bar centring");
assert(LANE.dispatch > PACING.x + PACING.w + 0.25, "dispatch lane clips the Pacing module");
assert(LANE.dispatch > BAR.x && LANE.dispatch < BAR.x + BAR.w, "dispatch lane misses the bar");
assert(LANE.complete > ADMISSION.x + ADMISSION.w + 0.15, "feedback lane clips Admission");
assert(LANE.admit > ADMISSION.x && LANE.admit < ADMISSION.x + ADMISSION.w,
  "admission lane must leave from its own module");
assert(LANE.admit > BAR.x + BAR.w, "admission lane clips the estimator bar");
assert(LANE.available < BAR.x && LANE.release < BAR.x, "pacing lanes clip the estimator bar");
assert(COMPLETE_Y > ROW1.y + ROW1.h + 0.20, "feedback bus runs too close to Admission");
approx(CTRL.y + CTRL.h + PANEL.y, SLIDE.h, "top and bottom margins");

// No lane may cross a title glyph in a header strip.
const ctrlTitleW = textWidth("Budget-Aware Draft Controller", FS.panelTitle, true);
lanes.forEach(([name, x]) => {
  const crossesHeader = x > CTRL.x && x < CTRL.x + CTRL.w;
  if (!crossesHeader) return;
  assert(
    Math.abs(x - SLIDE.w / 2) > ctrlTitleW / 2 + 0.15,
    `lane ${name} crosses the controller title`,
  );
});

/* ------------------------------------------------------------------ */

const outPath = process.argv[2]
  ? path.resolve(process.argv[2])
  : path.join(__dirname, "..", "figures", "fig_controller_interaction.pptx");
pptx.writeFile({ fileName: outPath })
  .then(() => console.log(`Wrote ${outPath}`))
  .catch((error) => {
    console.error(error);
    process.exitCode = 1;
  });
