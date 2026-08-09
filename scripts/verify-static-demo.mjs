import { chromium } from "playwright";
import { mkdir } from "node:fs/promises";

const baseUrl = process.argv[2] || "http://127.0.0.1:8765";
const outputDir = process.argv[3] || "verify_shots";

await mkdir(outputDir, { recursive: true });
const browser = await chromium.launch({
  headless: true,
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
});

const errors = [];
const timings = [];

async function verifyViewport(name, viewport) {
  const page = await browser.newPage({ viewport });
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(`${name}: ${message.text()}`);
  });
  page.on("pageerror", (error) => errors.push(`${name}: ${error.message}`));

  for (let attempt = 0; attempt < 3; attempt += 1) {
    const started = performance.now();
    await page.goto(baseUrl, { waitUntil: "networkidle" });
    await page.locator("#statusPill").waitFor({ state: "visible" });
    await page.waitForFunction(() => document.querySelector("#statusPill")?.textContent !== "Loading");
    timings.push({ viewport: name, attempt: attempt + 1, milliseconds: Math.round(performance.now() - started) });
  }

  const expected = [
    ["Live provider call", "needs_human", "COMPLETED"],
    ["Authorization preview", "awaiting authorization", "preview"],
    ["Vendor acknowledged", "vendor_acknowledged", "simulate"],
  ];

  for (const [buttonLabel, route, status] of expected) {
    await page.getByRole("button", { name: new RegExp(buttonLabel) }).click();
    await page.waitForFunction(
      ({ expectedRoute, expectedStatus }) =>
        document.querySelector("#routeValue")?.textContent === expectedRoute &&
        document.querySelector("#statusPill")?.textContent === expectedStatus,
      { expectedRoute: route, expectedStatus: status },
    );
    const activeCount = await page.locator(".scenario-button.active").count();
    if (activeCount !== 1) errors.push(`${name}: expected one active scenario, found ${activeCount}`);
  }

  await page.getByRole("button", { name: /Live provider call/ }).click();
  await page.waitForFunction(() => document.querySelector("#routeValue")?.textContent === "needs_human");
  await page.mouse.move(0, 0);

  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
  if (overflow) errors.push(`${name}: horizontal overflow detected`);

  await page.screenshot({ path: `${outputDir}/${name}.png`, fullPage: true });
  await page.close();
}

await verifyViewport("desktop", { width: 1440, height: 1000 });
await verifyViewport("mobile", { width: 390, height: 844 });
await browser.close();

console.log(JSON.stringify({ ok: errors.length === 0, timings, errors }, null, 2));
if (errors.length) process.exitCode = 1;
