import fs from "node:fs/promises";
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { FileBlob, PresentationFile } = require("@oai/artifact-tool");

// Rebuilds the editable Figure 4 deck. The checked-in, author-designed Figure 3
// deck supplies the paper's slide size and theme and is never overwritten.

const ROOT = path.resolve(process.cwd());
const TMP = path.join(ROOT, "tmp", "presentations", "controller_figures");
const FIGURES = path.join(ROOT, "figures");

const C = {
  navy: "#14233E",
  slate: "#526477",
  line: "#D4DCE8",
  panel: "#F7F9FC",
  controller: "#F2F5FA",
  controllerHeader: "#DFE7F3",
  header: "#E7EDF6",
  orange: "#E56E2E",
  orangeFill: "#FFF4ED",
  blue: "#2476D2",
  blueFill: "#EFF5FE",
  white: "#FFFFFF",
};

async function writeBlob(filePath, blob) {
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

function addText(slide, name, text, position, options = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    name,
    position,
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    typeface: "Arial",
    fontSize: options.fontSize ?? 16,
    bold: options.bold ?? false,
    color: options.color ?? C.navy,
    alignment: options.alignment ?? "center",
    verticalAlignment: options.verticalAlignment ?? "middle",
    autoFit: "none",
    wrap: options.wrap ?? "none",
    insets: options.insets ?? { top: 2, right: 4, bottom: 2, left: 4 },
  };
  return shape;
}

function addCard(slide, name, text, position, options = {}) {
  const geometry = options.geometry ?? "roundRect";
  const shape = slide.shapes.add({
    geometry,
    name,
    position,
    fill: options.fill ?? C.white,
    line: {
      style: options.lineStyle ?? "solid",
      fill: options.line ?? C.line,
      width: options.lineWidth ?? 1.2,
    },
    ...(["rect", "textbox", "roundRect"].includes(geometry)
      ? { borderRadius: options.borderRadius ?? 7 }
      : {}),
  });
  if (text) {
    shape.text = text;
    shape.text.style = {
      typeface: "Arial",
      fontSize: options.fontSize ?? 16,
      bold: options.bold ?? false,
      color: options.color ?? C.navy,
      alignment: options.alignment ?? "center",
      verticalAlignment: options.verticalAlignment ?? "middle",
      autoFit: "none",
      wrap: "none",
      insets: options.insets ?? { top: 5, right: 7, bottom: 5, left: 7 },
    };
  }
  return shape;
}

function addLine(slide, name, position, options = {}) {
  return slide.shapes.add({
    geometry: "line",
    name,
    position,
    fill: "none",
    line: {
      style: options.style ?? "solid",
      fill: options.color ?? C.line,
      width: options.width ?? 1,
    },
  });
}

function connect(slide, from, to, options = {}) {
  const connector = slide.shapes.connect(from, to, {
    kind: options.kind ?? "elbow",
    fromSide: options.fromSide,
    toSide: options.toSide,
    line: {
      style: options.style ?? "solid",
      fill: options.color ?? C.slate,
      width: options.width ?? 1.7,
    },
    head: options.tail ? { type: "triangle", width: "sm", length: "sm" } : { type: "none" },
    tail: options.head === false ? { type: "none" } : { type: "triangle", width: "sm", length: "sm" },
  });
  connector.bringToFront();
  return connector;
}

function clearSlide(slide) {
  slide.shapes.deleteAll();
  for (const image of [...slide.images.items]) image.delete();
  for (const chart of [...slide.charts.items]) chart.delete();
  for (const table of [...slide.tables.items]) table.delete();
}

function buildFigure3(slide) {
  clearSlide(slide);
  slide.background.fill = C.white;

  addText(slide, "application-heading", "Application-facing\navailability", { left: 30, top: 14, width: 265, height: 50 }, { fontSize: 19.3, bold: true });
  addText(slide, "pipeline-heading", "Existing single-worker Draft pipeline", { left: 325, top: 18, width: 797, height: 28 }, { fontSize: 19.3, bold: true });

  const app = addCard(slide, "next-capture-opportunity", "Earliest next-capture\nopportunity", { left: 58, top: 78, width: 210, height: 82 }, { fontSize: 18, line: C.slate, lineWidth: 1.4 });
  const queue = addCard(slide, "pending-draft-queue", "Pending Draft\nqueue", { left: 350, top: 78, width: 170, height: 82 }, { fontSize: 18, fill: C.panel, line: C.slate, lineWidth: 1.3 });
  const optional = addCard(slide, "optional-processing", "Optional image\nprocessing", { left: 590, top: 70, width: 190, height: 98 }, { fontSize: 18, bold: true, fill: C.blueFill, line: C.blue, lineWidth: 1.7 });
  const encoding = addCard(slide, "encoding-saving", "Encoding\n& saving", { left: 838, top: 78, width: 150, height: 82 }, { fontSize: 18, line: C.navy, lineWidth: 1.4 });
  const output = addCard(slide, "draft-image", "Draft\nimage", { left: 1036, top: 84, width: 82, height: 70 }, { fontSize: 16.5, line: C.navy, lineWidth: 1.3 });

  connect(slide, app, queue, { kind: "straight", fromSide: "right", toSide: "left", color: C.slate });
  connect(slide, queue, optional, { kind: "straight", fromSide: "right", toSide: "left", color: C.slate });
  connect(slide, optional, encoding, { kind: "straight", fromSide: "right", toSide: "left", color: C.slate });
  connect(slide, encoding, output, { kind: "straight", fromSide: "right", toSide: "left", color: C.slate });
  addText(slide, "new-capture-label", "new\ncapture", { left: 270, top: 88, width: 78, height: 34 }, { fontSize: 14.5, color: C.slate });

  const shell = addCard(slide, "controller-shell", "", { left: 28.8, top: 293.76, width: 1094.4, height: 184.32 }, { fill: C.controller, line: C.navy, lineWidth: 1.25, borderRadius: 5 });
  shell.sendToBack();
  const shellHeader = addCard(slide, "controller-header", "", { left: 28.8, top: 293.76, width: 1094.4, height: 32.64 }, { geometry: "rect", fill: C.controllerHeader, line: C.controllerHeader, lineWidth: 0, borderRadius: 0 });
  addLine(slide, "controller-header-rule", { left: 28.8, top: 326.4, width: 1094.4, height: 0 }, { color: C.navy, width: 1.1 });
  addText(slide, "controller-title", "Budget-Aware Draft Controller", { left: 28.8, top: 293.76, width: 1094.4, height: 32.64 }, { fontSize: 20.5, bold: true });

  const pacing = addCard(slide, "pacing-module", "Capture-Availability Pacing\nworker occupancy + deadline window", { left: 72, top: 336, width: 302.4, height: 57.6 }, { fontSize: 15.3, bold: true, fill: C.white, line: C.orange, lineWidth: 1.7 });
  const admission = addCard(slide, "admission-module", "Remaining-Sequence Admission\nremaining suffix + live budget", { left: 777.6, top: 336, width: 302.4, height: 57.6 }, { fontSize: 16.3, bold: true, fill: C.white, line: C.blue, lineWidth: 1.7 });
  const state = addCard(slide, "shared-runtime-state", "Runtime state & online duration estimates", { left: 307.2, top: 416.64, width: 537.6, height: 48 }, { fontSize: 17.2, bold: true, fill: C.white, line: C.slate, lineWidth: 1.3 });

  connect(slide, pacing, app, { fromSide: "top", toSide: "bottom", color: C.orange, width: 1.9 });
  connect(slide, admission, optional, { fromSide: "top", toSide: "bottom", color: C.blue, width: 1.9 });
  connect(slide, encoding, state, { fromSide: "bottom", toSide: "right", color: C.slate, width: 1.5 });
  connect(slide, state, pacing, { fromSide: "left", toSide: "bottom", color: C.slate, width: 1.3, style: "dashed", head: false });
  connect(slide, state, admission, { fromSide: "right", toSide: "bottom", color: C.slate, width: 1.3, style: "dashed", head: false });

  addText(slide, "pacing-output-label", "immediate / delayed\ncaptureAvailable callback", { left: 64, top: 184, width: 250, height: 45 }, { fontSize: 15.5, color: C.orange });
  addText(slide, "admission-output-label", "admit / skip optional work", { left: 638, top: 188, width: 220, height: 25 }, { fontSize: 15.5, color: C.blue });
  addText(slide, "completion-observation-label", "completed-Draft observations", { left: 870, top: 188, width: 230, height: 25 }, { fontSize: 14.8, color: C.slate });

  slide.speakerNotes.setText([
    "[Sources]",
    "- Internal implementation audit: ML commit cdd524fbd86e390446cbbd15c0e4f7923d4f1c58.",
    "- Manuscript Sections 3.1-3.4.",
    "[/Sources]",
  ].join("\n"));
}

function eventHeader(slide, number, title, left, fill, color) {
  const card = addCard(slide, `event-${number}-header`, "", { left, top: 18, width: 168, height: 54 }, { fill, line: color, lineWidth: 1.25, borderRadius: 6 });
  addCard(slide, `event-${number}-number`, String(number), { left: left + 9, top: 29, width: 28, height: 28 }, { geometry: "ellipse", fill: color, line: color, lineWidth: 0, fontSize: 16, bold: true, color: C.white, insets: { top: 1, right: 1, bottom: 1, left: 1 } });
  addText(slide, `event-${number}-title`, title, { left: left + 42, top: 20, width: 118, height: 50 }, { fontSize: 16.5, bold: true, color });
  return card;
}

function buildFigure4(slide) {
  clearSlide(slide);
  slide.background.fill = C.white;

  const laneX = 28;
  const laneW = 164;
  const bodyX = 202;
  const bodyW = 922;
  const rowTops = [88, 202, 316];
  const rowH = 102;
  const eventLefts = [204, 389, 574, 759, 944];

  const headers = [
    eventHeader(slide, 1, "Callback\ndecision", eventLefts[0], C.orangeFill, C.orange),
    eventHeader(slide, 2, "Draft\nstart", eventLefts[1], C.orangeFill, C.orange),
    eventHeader(slide, 3, "Optional\nnode", eventLefts[2], C.blueFill, C.blue),
    eventHeader(slide, 4, "Draft\ncompletion", eventLefts[3], C.panel, C.slate),
    eventHeader(slide, 5, "Queue\ndrain", eventLefts[4], C.panel, C.slate),
  ];
  for (let i = 0; i < headers.length - 1; i += 1) {
    connect(slide, headers[i], headers[i + 1], { kind: "straight", fromSide: "right", toSide: "left", color: C.slate, width: 1.25 });
  }

  const laneNames = [
    ["Capture-Availability\nPacing", C.orange, C.orangeFill, 15],
    ["Draft manager /\nsingle worker", C.navy, C.panel, 17],
    ["Predictor /\nadmission policy", C.blue, C.blueFill, 17],
  ];
  for (let i = 0; i < rowTops.length; i += 1) {
    const band = addCard(slide, `lane-${i + 1}-band`, "", { left: bodyX, top: rowTops[i], width: bodyW, height: rowH }, { geometry: "rect", fill: "none", line: C.line, lineWidth: 0.8, borderRadius: 0 });
    band.sendToBack();
    addCard(slide, `lane-${i + 1}-label`, laneNames[i][0], { left: laneX, top: rowTops[i], width: laneW, height: rowH }, { fill: laneNames[i][2], line: laneNames[i][1], lineWidth: 1.2, fontSize: laneNames[i][3], bold: true, color: laneNames[i][1], insets: { top: 4, right: 2, bottom: 4, left: 2 } });
  }

  for (let i = 1; i < eventLefts.length; i += 1) {
    addLine(slide, `event-divider-${i}`, { left: eventLefts[i] - 9, top: 84, width: 0, height: 342 }, { color: C.line, width: 0.8, style: "dashed" });
  }

  const callback = addCard(slide, "callback-actions", "Read backlog / reserve /\ndeadline\nCompute delay\nEnqueue + update clock\nSchedule release", { left: 211, top: 94, width: 154, height: 90 }, { fill: C.white, line: C.orange, lineWidth: 1.45, fontSize: 12.8, color: C.navy, insets: { top: 3, right: 4, bottom: 3, left: 4 } });

  const startPacer = addCard(slide, "draft-start-pacer", "Pop oldest decision\nRebase clock\nRefresh reserve", { left: 396, top: 103, width: 154, height: 72 }, { fill: C.white, line: C.orange, lineWidth: 1.45, fontSize: 14.8 });
  const startWorker = addCard(slide, "draft-start-worker", "Draft starts", { left: 408, top: 230, width: 130, height: 46 }, { fill: C.white, line: C.navy, lineWidth: 1.35, fontSize: 16, bold: true });
  connect(slide, startWorker, startPacer, { kind: "straight", fromSide: "top", toSide: "bottom", color: C.orange, width: 1.35 });

  const nodeWorker = addCard(slide, "optional-node-worker", "Build suffix\nReread live budget", { left: 581, top: 218, width: 154, height: 62 }, { fill: C.white, line: C.navy, lineWidth: 1.35, fontSize: 15.2 });
  const nodePolicy = addCard(slide, "optional-node-policy", "Admit + watchdog\nor skip", { left: 593, top: 343, width: 130, height: 54 }, { fill: C.white, line: C.blue, lineWidth: 1.5, fontSize: 13.0, bold: true, color: C.blue });
  connect(slide, nodeWorker, nodePolicy, { kind: "straight", fromSide: "bottom", toSide: "top", color: C.blue, width: 1.6, tail: true });
  addCard(slide, "optional-repeat", "repeat per optional node", { left: 578, top: 282, width: 160, height: 25 }, { fill: C.blueFill, line: C.blueFill, lineWidth: 0, fontSize: 12.5, color: C.blue, insets: { top: 1, right: 3, bottom: 1, left: 3 } });
  addText(slide, "optional-state", "first rejection may stick", { left: 582, top: 397, width: 153, height: 17 }, { fontSize: 11.8, color: C.blue });

  const completePacer = addCard(slide, "completion-pacer", "Update burst\nsize maximum", { left: 778, top: 114, width: 130, height: 52 }, { fill: C.white, line: C.orange, lineWidth: 1.25, fontSize: 15 });
  const completeWorker = addCard(slide, "completion-worker", "Saved-Draft\ncompletion", { left: 778, top: 226, width: 130, height: 54 }, { fill: C.white, line: C.navy, lineWidth: 1.35, fontSize: 14.5, bold: true });
  const completeModel = addCard(slide, "completion-model", "Update learned\nduration model", { left: 778, top: 343, width: 130, height: 54 }, { fill: C.white, line: C.blue, lineWidth: 1.35, fontSize: 15.2 });
  connect(slide, completeWorker, completePacer, { kind: "straight", fromSide: "top", toSide: "bottom", color: C.slate, width: 1.25 });
  connect(slide, completeWorker, completeModel, { kind: "straight", fromSide: "bottom", toSide: "top", color: C.slate, width: 1.25 });

  const drainPacer = addCard(slide, "drain-pacer", "Clear pacing\nsession", { left: 963, top: 114, width: 130, height: 52 }, { fill: C.white, line: C.orange, lineWidth: 1.25, fontSize: 15.2 });
  const drainWorker = addCard(slide, "drain-worker", "Queue empty", { left: 963, top: 230, width: 130, height: 46 }, { fill: C.white, line: C.navy, lineWidth: 1.35, fontSize: 16, bold: true });
  const drainPolicy = addCard(slide, "drain-policy", "Clear sticky\ndemotions\nRetain learned\nmodel", { left: 953, top: 334, width: 150, height: 70 }, { fill: C.white, line: C.blue, lineWidth: 1.35, fontSize: 13.2, insets: { top: 3, right: 5, bottom: 3, left: 5 } });
  connect(slide, drainWorker, drainPacer, { kind: "straight", fromSide: "top", toSide: "bottom", color: C.slate, width: 1.25 });
  connect(slide, drainWorker, drainPolicy, { kind: "straight", fromSide: "bottom", toSide: "top", color: C.slate, width: 1.25 });

  addCard(slide, "burst-state-legend", "BURST-LOCAL STATE  •  cleared at queue drain", { left: 244, top: 448, width: 405, height: 30 }, { fill: C.controllerHeader, line: C.line, lineWidth: 0.9, fontSize: 14.2, bold: true, color: C.slate });
  addCard(slide, "learned-state-legend", "LEARNED DURATION MODEL  •  retained", { left: 670, top: 448, width: 358, height: 30 }, { fill: C.blueFill, line: C.blue, lineWidth: 0.9, fontSize: 14.2, bold: true, color: C.blue });

  slide.speakerNotes.setText([
    "[Sources]",
    "- Internal implementation audit: ML commit cdd524fbd86e390446cbbd15c0e4f7923d4f1c58.",
    "- Manuscript Sections 3.3-3.5.",
    "[/Sources]",
  ].join("\n"));
}

async function buildOne(name, builder, finalName) {
  const workspace = path.join(TMP, name);
  const starter = path.join(FIGURES, "fig_controller_interaction.pptx");
  const presentation = await PresentationFile.importPptx(await FileBlob.load(starter));
  const slide = presentation.slides.getItem(0);
  builder(slide);

  const renderDir = path.join(workspace, "final-render");
  const layoutDir = path.join(workspace, "final-layout");
  await fs.mkdir(renderDir, { recursive: true });
  await fs.mkdir(layoutDir, { recursive: true });
  await writeBlob(path.join(renderDir, "slide-01.png"), await presentation.export({ slide, format: "png", scale: 2 }));
  const layout = await slide.export({ format: "layout" });
  await fs.writeFile(path.join(layoutDir, "slide-01.layout.json"), await layout.text(), "utf8");
  await writeBlob(path.join(workspace, "final-montage.webp"), await presentation.export({ format: "webp", montage: true, scale: 1 }));
  const inspected = await presentation.inspect({ kind: "slide,textbox,shape,notes,layout", maxChars: 30000 });
  await fs.writeFile(path.join(workspace, "final-inspect.ndjson"), inspected.ndjson, "utf8");

  const finalPptx = path.join(FIGURES, finalName);
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(finalPptx);
  return finalPptx;
}

await fs.mkdir(FIGURES, { recursive: true });
const outputs = [];
outputs.push(await buildOne("fig4", buildFigure4, "fig_controller_runtime_sequence.pptx"));
console.log(outputs.join("\n"));
