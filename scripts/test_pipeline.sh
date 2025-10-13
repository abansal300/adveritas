#!/usr/bin/env bash
set -euo pipefail

VID_URL=${1:-"https://www.youtube.com/watch?v=dQw4w9WgXcQ"}
echo "Ingesting: $VID_URL"
VID=$(curl -s -X POST http://localhost:8000/videos/ingest -F "source_url=$VID_URL" -F "title=Demo" | jq -r .id)

echo "Video id: $VID"
echo "Waiting for transcription..."
for i in {1..60}; do
  S=$(curl -s http://localhost:8000/videos/$VID | jq -r .status)
  if [[ "$S" == "TRANSCRIBED" || "$S" == "NO_CLAIMS" ]]; then break; fi
  sleep 5
done
curl -s http://localhost:8000/videos/$VID | jq .

echo "Extracting claims..."
curl -s -X POST "http://localhost:8000/claims/video/$VID/extract?overwrite=true" | jq .

echo "Waiting for claims extraction..."
for i in {1..30}; do
  COUNT=$(curl -s http://localhost:8000/claims/video/$VID | jq -r 'length')
  if [[ "$COUNT" != "0" && "$COUNT" != "null" ]]; then break; fi
  sleep 2
done

CLAIM_ID=$(curl -s http://localhost:8000/claims/video/$VID | jq -r '.[0].id')
echo "First claim id: $CLAIM_ID"

echo "Fetching evidence..."
curl -s -X POST http://localhost:8000/evidence/claim/$CLAIM_ID/fetch | jq .

echo "Waiting for evidence..."
for i in {1..30}; do
  COUNT=$(curl -s http://localhost:8000/evidence/claim/$CLAIM_ID | jq -r 'length')
  if [[ "$COUNT" != "0" && "$COUNT" != "null" ]]; then break; fi
  sleep 2
done
curl -s http://localhost:8000/evidence/claim/$CLAIM_ID | jq .

echo "Generating verdict..."
curl -s -X POST http://localhost:8000/verdicts/claim/$CLAIM_ID/generate | jq .

echo "Waiting for verdict (may take 1-2 minutes on CPU)..."
for i in {1..90}; do
  OK=$(curl -s http://localhost:8000/verdicts/claim/$CLAIM_ID | jq -r '.ok')
  if [[ "$OK" == "true" ]]; then break; fi
  sleep 2
done
curl -s http://localhost:8000/verdicts/claim/$CLAIM_ID | jq .
