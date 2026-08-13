import { chromium } from "playwright";
import { mkdir } from "node:fs/promises";

const outputDir = "video/build/browser";
await mkdir(outputDir, { recursive: true });

const browser = await chromium.launch({
  headless: true,
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
});
const context = await browser.newContext({
  viewport: { width: 1280, height: 720 },
  recordVideo: { dir: outputDir, size: { width: 1280, height: 720 } },
  colorScheme: "light",
});
const page = await context.newPage();
const video = page.video();

const pause = (seconds) => page.waitForTimeout(seconds * 1000);
const moveTo = async (selector) => {
  const box = await page.locator(selector).boundingBox();
  if (box) await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2, { steps: 24 });
};

const demoUrl =
  process.env.INCIDENTBRIDGE_DEMO_URL ||
  "https://yangyangnovelist-hub.github.io/incidentbridge-calle/";
await page.goto(demoUrl, { waitUntil: "networkidle" });
await page.waitForFunction(() => document.querySelector("#statusPill")?.textContent !== "Loading");
await moveTo(".hero-copy h1");
await pause(17);

await page.locator("#workflow").scrollIntoViewIfNeeded();
await pause(2);
await moveTo(".flow article:nth-child(1)");
await pause(17);

await page.locator("#console").scrollIntoViewIfNeeded();
await pause(4);
await moveTo(".scenario-button:nth-of-type(1)");
await pause(12);
await moveTo(".scenario-button:nth-of-type(2)");
await page.locator(".scenario-button:nth-of-type(2)").click();
await pause(13);
await moveTo(".scenario-button:nth-of-type(3)");
await page.locator(".scenario-button:nth-of-type(3)").click();
await pause(13);

await page.locator("#proof").scrollIntoViewIfNeeded();
await pause(4);
await moveTo(".proof div:nth-child(2)");
await pause(16);
await page.locator(".boundary").scrollIntoViewIfNeeded();
await pause(14);

await page.locator("#proof .cta").scrollIntoViewIfNeeded();
await pause(16);
await page.evaluate(() => window.scrollTo({ top: 0, behavior: "smooth" }));
await pause(10);

await page.close();
await context.close();
console.log(await video.path());
await browser.close();
