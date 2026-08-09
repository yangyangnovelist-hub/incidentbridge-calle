import { readFile, writeFile } from "node:fs/promises";

const [inputPath, outputPath, durationArgument] = process.argv.slice(2);
const totalDuration = Number(durationArgument);
const text = await readFile(inputPath, "utf8");
const sentences = text
  .replaceAll("E.164", "E§164")
  .replace(/\s+/g, " ")
  .trim()
  .match(/[^.!?]+[.!?]+/g)
  .map((sentence) => sentence.trim().replaceAll("E§164", "E.164"));
const weights = sentences.map((sentence) => sentence.split(/\s+/).length);
const totalWeight = weights.reduce((sum, value) => sum + value, 0);
const gap = 0.12;
const speechDuration = totalDuration - gap * (sentences.length - 1);

function timestamp(seconds) {
  const milliseconds = Math.max(0, Math.round(seconds * 1000));
  const hours = Math.floor(milliseconds / 3_600_000);
  const minutes = Math.floor((milliseconds % 3_600_000) / 60_000);
  const secs = Math.floor((milliseconds % 60_000) / 1000);
  const millis = milliseconds % 1000;
  return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}:${String(secs).padStart(2, "0")},${String(millis).padStart(3, "0")}`;
}

let cursor = 0;
const blocks = sentences.map((sentence, index) => {
  const duration = speechDuration * weights[index] / totalWeight;
  const start = cursor;
  const end = start + duration;
  cursor = end + gap;
  return `${index + 1}\n${timestamp(start)} --> ${timestamp(end)}\n${sentence}\n`;
});

await writeFile(outputPath, `${blocks.join("\n")}\n`);
