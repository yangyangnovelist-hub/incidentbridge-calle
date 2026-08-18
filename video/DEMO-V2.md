# IncidentBridge Demo V2 — Judge-Focused Build

The current source is optimized for the CALL-E judging rubric rather than for a generic product tour.

The story order is:

1. specific real-world phone-work problem;
2. authority boundary — calls create evidence, never recovery truth;
3. controlled workflow;
4. real CALL-E fail-closed provider evidence;
5. no-call preview and acknowledged route;
6. the verified local operator console in preview-only mode;
7. independent CALL-E maintainer review and official merge;
8. current runtime SDK / CI proof; and
9. transparent operator-time impact model.

The reviewed narration ends at approximately **2:28**, comfortably below the hackathon's three-minute limit.

## Build on macOS

Requirements:

- Google Chrome at `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
- Node + npm
- `uv`
- `ffmpeg` / `ffprobe`
- `curl`
- internet access for GitHub Pages and, on first run, the Kokoro model/dependencies

Run:

```bash
bash scripts/build-demo-v2.sh
```

Expected output:

```text
video/build/incidentbridge-demo-v2.mp4
```

The script:

- starts `incidentbridge-web` on `127.0.0.1:8766` in **preview-only mode**;
- verifies the local operator console is ready;
- records the public evidence console with Playwright;
- records the local browser operator surface and executes only **Preview — no call**;
- visits and interacts with the impact calculator;
- stops the local operator server;
- regenerates narration from `video/incidentbridge-demo.en.srt` using Kokoro-82M;
- burns English captions into the video; and
- produces an H.264/AAC MP4 suitable for YouTube or Vimeo.

The build script never passes `--enable-live-ui`, never supplies a phone allowlist, and therefore cannot place a phone call while recording.

## Review before upload

Watch the entire MP4 once and confirm:

- the real provider failure is clearly labeled as a real CALL-E run;
- the acknowledged public-browser scenario is clearly labeled as simulation unless a public consented live success artifact has been added;
- the local operator console visibly says live execution is disabled while the recording uses Preview;
- the official PR #132 merge claim is visible and accurate;
- the CI claim is **27 tests / 93.14% total coverage**, with the operator console at 95%;
- the impact calculator is explicitly presented as assumption-driven, not measured customer ROI; and
- the video remains under three minutes.

## Strongest possible final version

If a consented live success-path run is completed using `LIVE-SUCCESS-DEMO.md`, update the public evidence console and the video so the success route can be shown as:

**real CALL-E call + synthetic incident + consenting authorized recipient**

Do not call it a real vendor deployment. The strength of that artifact is that the transport and full success routing are real while the scenario remains privacy-safe and reproducible.

## Upload and Devpost

Upload the final MP4 to YouTube or Vimeo as a publicly visible video. Then replace the current Devpost demo-video URL before the submission deadline.

Do not delete the old video until the replacement URL is confirmed to play publicly.
