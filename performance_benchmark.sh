#!/usr/bin/env bash

# Run every configuration sequentially and combine each Python report in results.json.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
METAL_PYTHON="${METAL_PYTHON:-$SCRIPT_DIR/.venv-metal/bin/python}"
ACCELERATE_PYTHON="${ACCELERATE_PYTHON:-$SCRIPT_DIR/.venv-accelerate/bin/python}"
RESULTS_JSON="${RESULTS_JSON:-$SCRIPT_DIR/results.json}"
RUN_ID="$(date '+%Y%m%d-%H%M%S')"
RUNS_DIR="${RUNS_DIR:-$SCRIPT_DIR/results/performance-benchmark/runs-$RUN_ID}"

shopt -s nullglob
CONFIG_FILES=("$SCRIPT_DIR"/configs/*.json)
if [[ -n "${CONFIG_NAMES:-}" ]]; then
  # Allow selective reruns while retaining the same run directory and aggregate report.
  read -r -a selected_configs <<< "$CONFIG_NAMES"
  CONFIG_FILES=()
  for config_name in "${selected_configs[@]}"; do
    config_path="$SCRIPT_DIR/configs/$config_name.json"
    if [[ ! -f "$config_path" ]]; then
      echo "Unknown config name: $config_name" >&2
      exit 2
    fi
    CONFIG_FILES+=("$config_path")
  done
fi
if (( ${#CONFIG_FILES[@]} == 0 )); then
  echo "No JSON configuration files found in $SCRIPT_DIR/configs" >&2
  exit 2
fi
if [[ ! -x "$METAL_PYTHON" ]]; then
  echo "Metal environment Python not found or not executable: $METAL_PYTHON" >&2
  exit 2
fi

mkdir -p "$RUNS_DIR" "$(dirname "$RESULTS_JSON")"
printf 'Running %d configs sequentially.\n' "${#CONFIG_FILES[@]}"
printf 'Per-config output: %s\n' "$RUNS_DIR"

for config_path in "${CONFIG_FILES[@]}"; do
  config_name="$(basename "$config_path" .json)"
  config_output="$RUNS_DIR/$config_name"
  mkdir -p "$config_output"

  # Use the CPU-optimized environment only when both model stages target CPU.
  if "$METAL_PYTHON" -c 'import json,sys; c=json.load(open(sys.argv[1])); sys.exit(0 if c["backbone_device"] == "cpu" and c["codec_device"] == "cpu" else 1)' "$config_path"; then
    config_python="$ACCELERATE_PYTHON"
  else
    config_python="$METAL_PYTHON"
  fi
  if [[ ! -x "$config_python" ]]; then
    echo "Python executable not found or not executable: $config_python" >&2
    exit 2
  fi

  command=("$config_python" "$SCRIPT_DIR/performance_benchmark.py"
    --config "$config_path" --output-dir "$config_output")
  [[ -z "${REPEATS:-}" ]] || command+=(--repeats "$REPEATS")
  [[ -z "${WARMUP_RUNS:-}" ]] || command+=(--warmup-runs "$WARMUP_RUNS")

  printf '\n=== %s ===\n' "$config_name"
  if "${command[@]}" >"$config_output/run.log" 2>&1; then
    status=0
    cat "$config_output/run.log"
  else
    status=$?
    cat "$config_output/run.log" >&2
    echo "Config $config_name exited with status $status; continuing." >&2
  fi
  printf '%s\n' "$status" > "$config_output/exit_code.txt"
done

# Keep aggregation in the standard library so the shell runner has no extra dependencies.
"$METAL_PYTHON" - "$RUNS_DIR" "$RESULTS_JSON" "$SCRIPT_DIR" <<'PY'
"""Combine per-config benchmark JSON files into one portable run manifest."""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

runs_dir, results_path, repository_root = map(Path, sys.argv[1:])
configs = []
for config_dir in sorted(path for path in runs_dir.iterdir() if path.is_dir()):
    result_path = config_dir / "results.json"
    log_path = config_dir / "run.log"
    exit_path = config_dir / "exit_code.txt"
    exit_code = int(exit_path.read_text().strip()) if exit_path.exists() else None
    report = json.loads(result_path.read_text()) if result_path.exists() else None

    # Preserve exception names from tracebacks when initialization failed before a report existed.
    log = log_path.read_text(errors="replace") if log_path.exists() else ""
    exception = re.findall(r"^([A-Za-z_][A-Za-z0-9_.]*(?:Error|Exception)):", log, re.M)
    configs.append({
        "config": config_dir.name,
        "exit_code": exit_code,
        "error_type": exception[-1] if exit_code and exception else None,
        "error_message": log.splitlines()[-1] if exit_code and log else None,
        "report": report,
        "log_path": str(log_path),
    })

results = {
    "schema_version": 1,
    "created_at_utc": datetime.now(timezone.utc).isoformat(),
    "repository_root": str(repository_root),
    "raw_reports_dir": str(runs_dir),
    "config_count": len(configs),
    "configs": configs,
}
results_path.parent.mkdir(parents=True, exist_ok=True)
results_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Combined results written to: {results_path}")
PY
