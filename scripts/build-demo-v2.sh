#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

for cmd in node npm uv ffmpeg ffprobe curl; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing required command: $cmd" >&2
    exit 1
  fi
done

mkdir -p video/build/browser

if [ ! -d node_modules/playwright ]; then
  echo "Installing Playwright locally without saving it to package metadata..."
  npm install --no-save --no-package-lock playwright
fi

if [ ! -x "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then
  echo "Google Chrome was not found at the macOS path expected by scripts/record-demo.mjs" >&2
  exit 1
fi

OPERATOR_URL="http://127.0.0.1:8766/"
OPERATOR_LOG="video/build/operator-console.log"
OPERATOR_PID=""

cleanup() {
  if [ -n "${OPERATOR_PID:-}" ] && kill -0 "$OPERATOR_PID" >/dev/null 2>&1; then
    kill "$OPERATOR_PID" >/dev/null 2>&1 || true
    wait "$OPERATOR_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

echo "Starting the local operator console in preview-only mode..."
uv run incidentbridge-web --host 127.0.0.1 --port 8766 >"$OPERATOR_LOG" 2>&1 &
OPERATOR_PID=$!

if ! curl -fsS \
  --retry 20 \
  --retry-delay 1 \
  --retry-connrefused \
  "${OPERATOR_URL}api/capabilities" >/dev/null; then
  echo "Operator console did not become ready. See $OPERATOR_LOG" >&2
  exit 1
fi

echo "Recording the judge-focused browser demo..."
BEFORE_LIST="$(mktemp)"
AFTER_LIST="$(mktemp)"
find video/build/browser -type f -name '*.webm' -print | sort > "$BEFORE_LIST"
INCIDENTBRIDGE_OPERATOR_URL="$OPERATOR_URL" node scripts/record-demo.mjs
find video/build/browser -type f -name '*.webm' -print | sort > "$AFTER_LIST"
VIDEO="$(comm -13 "$BEFORE_LIST" "$AFTER_LIST" | tail -n 1)"
rm -f "$BEFORE_LIST" "$AFTER_LIST"

cleanup
OPERATOR_PID=""

if [ -z "${VIDEO:-}" ]; then
  VIDEO="$(find video/build/browser -type f -name '*.webm' -print0 | xargs -0 ls -t | head -n 1)"
fi

if [ -z "${VIDEO:-}" ] || [ ! -f "$VIDEO" ]; then
  echo "Could not locate the newly recorded browser video." >&2
  exit 1
fi

echo "Generating narration from the reviewed SRT cues..."
HF_HUB_DISABLE_XET=1 uv run --script scripts/synthesize-demo-narration.py

NARRATION="video/build/narration-kokoro.wav"
SRT="video/incidentbridge-demo.en.srt"
OUTPUT="video/build/incidentbridge-demo-v2.mp4"

if [ ! -f "$NARRATION" ]; then
  echo "Narration was not generated at $NARRATION" >&2
  exit 1
fi

echo "Muxing narration and burning English captions..."
ffmpeg -y \
  -i "$VIDEO" \
  -i "$NARRATION" \
  -vf "subtitles=${SRT}:force_style='FontName=Arial,FontSize=18,Outline=1,Shadow=0,MarginV=24'" \
  -map 0:v:0 \
  -map 1:a:0 \
  -c:v libx264 \
  -preset medium \
  -crf 20 \
  -pix_fmt yuv420p \
  -c:a aac \
  -b:a 160k \
  -movflags +faststart \
  -shortest \
  "$OUTPUT"

DURATION="$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$OUTPUT" 2>/dev/null || true)"

echo
echo "Built: $OUTPUT"
if [ -n "$DURATION" ]; then
  printf 'Duration: %.1f seconds\n' "$DURATION"
fi
echo "The operator console was recorded in preview-only mode; this build script cannot place a phone call."
echo "Before uploading, watch the entire MP4 once and verify that every on-screen claim is accurate."
