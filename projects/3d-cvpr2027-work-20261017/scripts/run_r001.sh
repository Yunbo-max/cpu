#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 4 ]; then
  printf 'usage: %s EXTRACTED_FR2_DIR TGZ ARCHIVED_SOURCE_ROOT LEGACY_HELPER\n' "$0" >&2
  exit 2
fi

project_root="$(cd "$(dirname "$0")/.." && pwd)"
output_dir="$project_root/runs/R001"
mkdir -p "$output_dir"
printf 'Start UTC: %s\n' "$(date -u +%FT%TZ)"
printf 'Command: env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 %s/scripts/fr2_transfer_r001.py --data %s --archive %s --source %s --legacy-helper %s --output %s\n' "$project_root" "$1" "$2" "$3" "$4" "$output_dir"
env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  python3 "$project_root/scripts/fr2_transfer_r001.py" \
  --data "$1" --archive "$2" --source "$3" --legacy-helper "$4" --output "$output_dir"
printf 'End UTC: %s\n' "$(date -u +%FT%TZ)"
