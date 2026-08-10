const path = require("path");
const assert = require("assert");
const pptxgen = require("pptxgenjs");

const pptx = new pptxgen();
pptx.defineLayout({ name: "SEIP_FIGURE", width: 12, height: 4 });
pptx.layout = "SEIP_FIGURE";
pptx.author = "SEIP 2027 paper authors";
pptx.company = "SEIP 2027";
pptx.subject = "Budget-Aware Draft Controller overview";
pptx.title = "Budget-Aware Draft Controller";
pptx.lang = "en-US";
pptx.theme = {
  headFontFace: "Arial",
  bodyFontFace: "Arial",
  lang: "en-US",
};

const slide = pptx.addSlide();
slide.background = { color: "FFFFFF" };

const C = {
  navy: "14233E",
  slate: "526477",
  muted: "6E7A8D",
  lightLine: "AEB8C7",
  panel: "F8FAFD",
  orange: "E56E2E",
  orangeTint: "FCEDE4",
  blue: "2476D2",
  blueTint: "EAF3FF",
  modelTint: "F1F4F8",
  white: "FFFFFF",
};

const ST = pptx.ShapeType;
const FONT = "Arial";
const LINE_PT = 1.35;
const BORDER_PT = 1.0;
const PORT = 0.16;

function addText(text, x, y, w, h, opts = {}) {
  slide.addText(text, {
    x, y, w, h,
    fontFace: FONT,
    fontSize: opts.fontSize ?? 11.5,
    color: opts.color ?? C.navy,
    bold: opts.bold ?? false,
    italic: opts.italic ?? false,
    align: opts.align ?? "center",
    valign: opts.valign ?? "mid",
    margin: opts.margin ?? 0,
    breakLine: false,
    fit: "shrink",
    ...opts,
  });
}

function addRichLabel(runs, x, y, w, h, opts = {}) {
  slide.addText(runs, {
    x, y, w, h,
    fontFace: FONT,
    fontSize: opts.fontSize ?? 11.5,
    color: opts.color ?? C.navy,
    bold: opts.bold ?? false,
    align: opts.align ?? "center",
    valign: opts.valign ?? "mid",
    margin: 0,
    fit: "shrink",
  });
}

function addRoundRect(x, y, w, h, fill, line = C.navy, radius = 0.06, lineWidth = BORDER_PT) {
  slide.addShape(ST.roundRect, {
    x, y, w, h,
    rectRadius: radius,
    fill: { color: fill },
    line: { color: line, width: lineWidth },
  });
}

function addLine(x1, y1, x2, y2, color = C.navy, width = LINE_PT, arrows = {}) {
  slide.addShape(ST.line, {
    x: x1,
    y: y1,
    w: x2 - x1,
    h: y2 - y1,
    line: {
      color,
      width,
      beginArrowType: arrows.begin ?? "none",
      endArrowType: arrows.end ?? "none",
      dashType: arrows.dash ?? "solid",
    },
  });
}

function addOrthogonal(points, color, endArrow = true, width = LINE_PT) {
  assert(points.length >= 2, "orthogonal path needs at least two points");
  for (let i = 0; i < points.length - 1; i += 1) {
    const [x1, y1] = points[i];
    const [x2, y2] = points[i + 1];
    assert(x1 === x2 || y1 === y2, `non-orthogonal segment: ${x1},${y1} -> ${x2},${y2}`);
    addLine(x1, y1, x2, y2, color, width, {
      end: endArrow && i === points.length - 2 ? "triangle" : "none",
    });
  }
}

function addPort(cx, cy, color, size = PORT) {
  slide.addShape(ST.rect, {
    x: cx - size / 2,
    y: cy - size / 2,
    w: size,
    h: size,
    fill: { color },
    line: { color: C.navy, width: BORDER_PT },
  });
}

function addLabelKnockout(text, x, y, w, h, color = C.navy, fontSize = 10.5) {
  slide.addShape(ST.roundRect, {
    x, y, w, h,
    rectRadius: 0.025,
    fill: { color: C.white },
    line: { color: C.white, transparency: 100 },
  });
  addText(text, x, y, w, h, { color, fontSize, bold: false });
}

function addTwoLineKnockout(line1, line2, x, y, w, color, fontSize) {
  slide.addShape(ST.roundRect, {
    x, y, w, h: 0.46,
    rectRadius: 0.025,
    fill: { color: C.white },
    line: { color: C.white, transparency: 100 },
  });
  addText(line1, x, y, w, 0.22, { color, fontSize, bold: false });
  addText(line2, x, y + 0.24, w, 0.22, { color, fontSize, bold: false });
}

function captureLabel(suffix) {
  const runs = [{ text: "Capture " }, { text: "i", options: { italic: true } }];
  if (suffix) runs.push({ text: suffix });
  return runs;
}

function draftLabel(suffix) {
  const runs = [{ text: "Draft " }, { text: "i", options: { italic: true } }];
  if (suffix) runs.push({ text: suffix });
  return runs;
}

const ICON_DIR = path.join(__dirname, "..", "figures", "controller_icons");

function addIcon(name, x, y, w, h) {
  slide.addImage({
    path: path.join(ICON_DIR, `${name}.png`),
    x, y, w, h,
    altText: `${name.replaceAll("_", " ")} icon`,
  });
}

function addEnhancementIcon(x, y, size) {
  addRoundRect(x, y, size, size, C.white, C.navy, 0.05, 1.0);

  // A single before/after photo with one integrated sparkle denotes enhancement.
  const imageX = x + size * 0.11;
  const imageY = y + size * 0.28;
  const imageW = size * 0.60;
  const imageH = size * 0.48;
  slide.addShape(ST.rect, {
    x: imageX, y: imageY, w: imageW / 2, h: imageH,
    fill: { color: C.modelTint },
    line: { color: C.modelTint, transparency: 100 },
  });
  slide.addShape(ST.rect, {
    x: imageX + imageW / 2, y: imageY, w: imageW / 2, h: imageH,
    fill: { color: C.blueTint },
    line: { color: C.blueTint, transparency: 100 },
  });
  slide.addShape(ST.ellipse, {
    x: x + size * 0.18, y: y + size * 0.35,
    w: size * 0.08, h: size * 0.08,
    fill: { color: "708CB5" }, line: { color: C.navy, width: 0.45 },
  });
  slide.addShape(ST.triangle, {
    x: x + size * 0.15, y: y + size * 0.55,
    w: size * 0.26, h: size * 0.15,
    fill: { color: "6A83AC" }, line: { color: C.navy, width: 0.45 },
  });
  slide.addShape(ST.triangle, {
    x: x + size * 0.37, y: y + size * 0.46,
    w: size * 0.28, h: size * 0.24,
    fill: { color: "405F8E" }, line: { color: C.navy, width: 0.45 },
  });
  addLine(
    imageX + imageW / 2, imageY,
    imageX + imageW / 2, imageY + imageH,
    C.white, 0.8,
  );
  slide.addShape(ST.roundRect, {
    x: imageX, y: imageY, w: imageW, h: imageH,
    rectRadius: 0.02,
    fill: { color: C.white, transparency: 100 },
    line: { color: C.navy, width: 0.9 },
  });
  slide.addShape(ST.star4, {
    x: x + size * 0.69, y: y + size * 0.09,
    w: size * 0.18, h: size * 0.18,
    fill: { color: C.blue }, line: { color: C.navy, width: 0.45 },
  });
}

function addEncodeSaveIcon(x, y, size) {
  addRoundRect(x, y, size, size, C.white, C.navy, 0.05, 1.0);

  // A storage cylinder with one integrated pixel band denotes encoded output.
  slide.addShape(ST.can, {
    x: x + size * 0.22, y: y + size * 0.18,
    w: size * 0.56, h: size * 0.56,
    fill: { color: C.navy },
    line: { color: C.navy, width: 1.0 },
  });
  [0.31, 0.445, 0.58].forEach((relativeX, index) => {
    slide.addShape(ST.rect, {
      x: x + size * relativeX,
      y: y + size * 0.42,
      w: size * 0.09,
      h: size * 0.09,
      fill: { color: index === 1 ? C.blue : C.white },
      line: { color: index === 1 ? C.blue : C.white, transparency: 100 },
    });
  });
}

function addWorkloadEstimateIcon(x, y, size) {
  // Workload bars live inside one duration dial, yielding a single combined glyph.
  slide.addShape(ST.ellipse, {
    x, y, w: size, h: size,
    fill: { color: C.modelTint },
    line: { color: C.navy, width: 1.05 },
  });
  const bars = [
    { x: 0.19, h: 0.15, color: C.slate },
    { x: 0.34, h: 0.23, color: C.blue },
    { x: 0.49, h: 0.31, color: C.navy },
  ];
  bars.forEach((bar) => {
    slide.addShape(ST.rect, {
      x: x + size * bar.x,
      y: y + size * (0.76 - bar.h),
      w: size * 0.10,
      h: size * bar.h,
      fill: { color: bar.color },
      line: { color: bar.color, transparency: 100 },
    });
  });
  addLine(
    x + size * 0.52, y + size * 0.45,
    x + size * 0.72, y + size * 0.24,
    C.orange, 1.15,
  );
  slide.addShape(ST.ellipse, {
    x: x + size * 0.475, y: y + size * 0.405,
    w: size * 0.09, h: size * 0.09,
    fill: { color: C.orange },
    line: { color: C.navy, width: 0.5 },
  });
}

function addTwoLineModuleLabel(line1, line2, x, y, w, fontSize) {
  addText(line1, x, y, w, 0.22, {
    fontSize, bold: true, color: C.navy, align: "left",
  });
  addText(line2, x, y + 0.24, w, 0.22, {
    fontSize, bold: true, color: C.navy, align: "left",
  });
}

const TOP_GROUPS = [
  { name: "captures", x: 0.50, w: 2.75 },
  { name: "pending", x: 3.70, w: 1.50 },
  { name: "optional", x: 5.65, w: 2.70 },
  { name: "encoding", x: 8.80, w: 1.30 },
  { name: "image", x: 10.55, w: 0.95 },
];
const CONTROLLER = { x: 0.35, y: 2.88, w: 11.30, h: 1.00 };
const MODULES = [
  { name: "pacing", x: 1.10, w: 2.50 },
  { name: "model", x: 4.75, w: 2.50 },
  { name: "admission", x: 8.40, w: 2.50 },
];

// --- Background first, then connectors, then foreground modules. ---
addRoundRect(
  CONTROLLER.x, CONTROLLER.y, CONTROLLER.w, CONTROLLER.h,
  C.panel, C.navy, 0.08, BORDER_PT,
);

// The top execution plane uses one 1.35-inch axis and uniform 0.45-inch group gaps.
addLine(3.25, 1.35, 3.70, 1.35, C.navy, LINE_PT, { end: "triangle" });
addLine(5.05, 1.35, 5.87, 1.35, C.navy, LINE_PT, { end: "triangle" });
addLine(6.71, 1.35, 7.23, 1.35, C.navy, LINE_PT, { end: "triangle" });
addLine(8.07, 1.35, 8.94, 1.35, C.navy, LINE_PT, { end: "triangle" });
addLine(9.66, 1.35, 10.27, 1.35, C.navy, LINE_PT);
addLine(10.43, 1.35, 10.55, 1.35, C.navy, LINE_PT, { end: "triangle" });

// Capture i+1 produces captureAvailable; Pacing postpones its app-facing release.
addOrthogonal([[0.95, 1.195], [0.95, 1.88], [1.45, 1.88], [1.45, 3.12]], C.slate, true);
addOrthogonal([[2.05, 3.12], [2.05, 1.82], [1.20, 1.82], [1.20, 1.43]], C.orange, true);

// Admission controls the group as a whole and enters at its bottom center.
addOrthogonal([[9.65, 3.12], [9.65, 2.42], [7.00, 2.42], [7.00, 1.92]], C.blue, true);

// Completion feedback terminates at the controller boundary, not inside it.
addOrthogonal([[10.35, 1.43], [10.35, 2.08], [11.60, 2.08], [11.60, 2.80]], C.slate, true);

// Both control modules consume the central workload and duration estimates.
addLine(4.75, 3.42, 3.60, 3.42, C.orange, LINE_PT, { end: "triangle" });
addLine(7.25, 3.42, 8.40, 3.42, C.blue, LINE_PT, { end: "triangle" });

// --- Main execution plane. ---
addText("Parallel captures", 0.50, 0.10, 2.75, 0.28, { fontSize: 15.0, bold: true });
addText("Pending Draft Sequences", 3.20, 0.10, 2.50, 0.28, { fontSize: 15.0, bold: true });
addText("One active Draft Sequence", 5.65, 0.10, 5.85, 0.28, { fontSize: 15.0, bold: true });

const CAP_W = 2.05;
const CAP_H = 0.36;
const captures = [
  { x: 0.50, y: 0.50, suffix: "" },
  { x: 0.70, y: 0.835, suffix: "+1" },
  // Pacing after Capture i+1 adds 0.30 inches beyond the normal stagger.
  { x: 1.20, y: 1.17, suffix: "+2" },
];
captures.forEach(({ x, y, suffix }) => {
  addRoundRect(x, y, CAP_W, CAP_H, C.white, C.navy, 0.045, 1.0);
  addRichLabel(captureLabel(suffix), x, y, CAP_W, CAP_H, { fontSize: 11.8 });
});
assert(captures.every(() => CAP_W === 2.05 && CAP_H === 0.36), "capture cards are not clones");

addText("captureAvailable release", 1.35, 1.58, 1.55, 0.22, {
  fontSize: 9.8, bold: true, color: C.orange,
  align: "left",
});
addPort(1.20, 1.35, C.orange, 0.14);

const pending = [
  { x: 3.70, y: 0.835, suffix: "+2" },
  { x: 3.85, y: 1.17, suffix: "+1" },
];
pending.forEach(({ x, y, suffix }) => {
  addRoundRect(x, y, 1.20, CAP_H, C.white, C.navy, 0.04, 0.95);
  addRichLabel(draftLabel(suffix), x, y, 1.20, CAP_H, { fontSize: 11.2 });
});

addRoundRect(5.67, 0.48, 0.55, 0.23, C.blueTint, C.blue, 0.035, 0.8);
addRichLabel(draftLabel(""), 5.67, 0.48, 0.55, 0.23, {
  fontSize: 9.0, color: C.blue, bold: true,
});
addText("Optional image processing", 6.26, 0.48, 2.09, 0.23, {
  fontSize: 11.2, bold: true, color: C.blue,
});
slide.addShape(ST.roundRect, {
  x: 5.65, y: 0.75, w: 2.70, h: 1.10,
  rectRadius: 0.05,
  fill: { color: C.white, transparency: 100 },
  line: { color: C.blue, width: 1.0, dashType: "dash" },
});
// The source PNG contains transparent padding; 1.02in makes its visible tile 0.84in.
addIcon("optional_multiframe", 5.78, 0.84, 1.02, 1.02);
addEnhancementIcon(7.23, 0.93, 0.84);
addPort(7.00, 1.85, C.blue, 0.14);

addEncodeSaveIcon(8.94, 0.99, 0.72);
addText("Encoding & saving", 8.55, 1.82, 1.50, 0.22, {
  fontSize: 10.8, color: C.navy,
});

slide.addShape(ST.ellipse, {
  x: 10.27, y: 1.27, w: 0.16, h: 0.16,
  fill: { color: C.slate }, line: { color: C.navy, width: 0.75 },
});
addIcon("draft_image", 10.615, 0.93, 0.82, 0.82);
addText("Draft image", 10.48, 1.79, 1.10, 0.22, { fontSize: 10.8 });

// --- Controller plane. ---
addText("Budget-Aware Draft Controller", 4.05, 2.61, 3.90, 0.22, {
  fontSize: 14.4, bold: true,
});

addRoundRect(1.10, 3.12, 2.50, 0.60, C.white, C.orange, 0.055, 1.0);
addIcon("pacing", 1.23, 3.18, 0.48, 0.48);
addTwoLineModuleLabel("Capture-Availability", "Pacing", 1.80, 3.18, 1.64, 10.2);

addRoundRect(4.75, 3.12, 2.50, 0.60, C.white, C.slate, 0.055, 1.0);
addWorkloadEstimateIcon(4.88, 3.18, 0.48);
addTwoLineModuleLabel("Workload Model &", "Online Duration Estimates", 5.41, 3.18, 1.73, 10.2);

addRoundRect(8.40, 3.12, 2.50, 0.60, C.white, C.blue, 0.055, 1.0);
addIcon("admission", 8.53, 3.18, 0.48, 0.48);
addTwoLineModuleLabel("Remaining-Sequence", "Admission", 9.10, 3.18, 1.64, 10.2);

// Ports are exact clones and sit on connector centers.
addPort(1.45, 2.88, C.slate);
addPort(2.05, 2.88, C.orange);
addPort(9.65, 2.88, C.blue);
addPort(11.60, 2.88, C.slate);

// Connector labels use white knockouts so no line crosses text.
addTwoLineKnockout("captureAvailable", "callback", 0.15, 1.98, 1.15, C.navy, 10.2);
addTwoLineKnockout("postpone delivery", "to application", 2.20, 1.98, 1.25, C.orange, 10.2);
addLabelKnockout("admit / skip optional stages", 7.20, 2.27, 2.20, 0.29, C.blue, 11.0);
addTwoLineKnockout("update with measured", "Draft Sequence duration", 9.72, 2.18, 1.68, C.slate, 10.5);

// Deterministic geometry checks for the failure modes that motivated the redraw.
const topGaps = TOP_GROUPS.slice(1).map((group, index) => (
  group.x - (TOP_GROUPS[index].x + TOP_GROUPS[index].w)
));
assert(topGaps.every((gap) => Math.abs(gap - 0.45) < 1e-9), "top-group gaps must all be 0.45in");
const moduleGaps = MODULES.slice(1).map((module, index) => (
  module.x - (MODULES[index].x + MODULES[index].w)
));
assert(moduleGaps.every((gap) => Math.abs(gap - 1.15) < 1e-9), "controller-module gaps must all be 1.15in");
assert(PORT === 0.16, "controller ports must use one shared size");
assert(LINE_PT === 1.35, "semantic connectors must use one shared stroke");

const outPath = path.join(__dirname, "..", "figures", "fig_controller_interaction.pptx");
pptx.writeFile({ fileName: outPath })
  .then(() => console.log(`Wrote ${outPath}`))
  .catch((error) => {
    console.error(error);
    process.exitCode = 1;
  });
