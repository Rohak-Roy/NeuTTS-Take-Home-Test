#!/usr/bin/env python3
"""Compare latency, real-time factor, and process RSS across benchmark configs.

The script reads the combined JSON produced by ``performance_benchmark.sh`` and
writes a Markdown report plus a CSV. Latency is reported both across all prompts
and separately for each prompt, because prompt length affects synthesis time.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from pathlib import Path
from typing import Any


def percentile_90(values: list[float]) -> float | None:
    """Return the nearest-rank 90th percentile for a non-empty sample.

    Args:
        values: Numeric measurements to summarize.

    Returns:
        The P90 value, or ``None`` when there are no measurements.
    """
    if not values:
        return None
    ordered = sorted(values)
    # Nearest-rank percentile: rank = ceil(p * N), using one-based indexing.
    return ordered[max(0, math.ceil(0.90 * len(ordered)) - 1)]


def format_number(value: float | None, places: int = 3) -> str:
    """Format a numeric value for tables, using an em dash for missing data.

    Args:
        value: Value to format.
        places: Number of decimal places to show.

    Returns:
        A fixed-precision string or an em dash.
    """
    return f"{value:.{places}f}" if value is not None else "—"


def load_results(path: Path) -> list[dict[str, Any]]:
    """Load and validate per-config reports from the benchmark bundle.

    Args:
        path: Combined ``results.json`` path.

    Returns:
        List of configuration result mappings.

    Raises:
        ValueError: If the JSON does not contain a config list.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    configs = data.get("configs")
    if not isinstance(configs, list):
        raise ValueError(f"Expected a 'configs' list in {path}")
    return configs


def summarize_config(config_entry: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Calculate overall and per-prompt metrics for one configuration.

    Args:
        config_entry: One item from the combined results' ``configs`` list.

    Returns:
        An overall metric row and a list of prompt-specific metric rows.
    """
    name = str(config_entry.get("config", "unknown"))
    report = config_entry.get("report") or {}
    records = report.get("records") or []
    successful = [record for record in records if record.get("status") == "ok"]
    measurement = report.get("measurement") or {}
    rss = measurement.get("peak_process_rss_mb")

    all_latencies = [float(record["wall_seconds"]) for record in successful
                     if record.get("wall_seconds") is not None]
    all_rtfs = [float(record["rtf"]) for record in successful if record.get("rtf") is not None]
    overall = {
        "config": name,
        "exit_code": config_entry.get("exit_code"),
        "successful_runs": len(successful),
        "failed_runs": len(records) - len(successful),
        "p90_latency_seconds": percentile_90(all_latencies),
        "median_rtf": statistics.median(all_rtfs) if all_rtfs else None,
        "peak_process_rss_mb": float(rss) if rss is not None else None,
        "error_type": config_entry.get("error_type"),
        "error_message": config_entry.get("error_message"),
    }

    prompt_rows: list[dict[str, Any]] = []
    prompt_ids = dict.fromkeys(str(record.get("case_id", "unknown")) for record in successful)
    for prompt_id in prompt_ids:
        prompt_records = [record for record in successful
                          if str(record.get("case_id", "unknown")) == prompt_id]
        latencies = [float(record["wall_seconds"]) for record in prompt_records
                     if record.get("wall_seconds") is not None]
        rtfs = [float(record["rtf"]) for record in prompt_records if record.get("rtf") is not None]
        prompt_rows.append({
            "config": name,
            "prompt": prompt_id,
            "successful_runs": len(prompt_records),
            "p90_latency_seconds": percentile_90(latencies),
            "median_rtf": statistics.median(rtfs) if rtfs else None,
            "peak_process_rss_mb": overall["peak_process_rss_mb"],
        })
    return overall, prompt_rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write all-config and per-prompt metrics to a single CSV file.

    Args:
        path: Destination CSV path.
        rows: Metric rows containing an ``analysis_scope`` field.
    """
    fields = [
        "analysis_scope", "config", "prompt", "exit_code", "successful_runs",
        "failed_runs", "p90_latency_seconds", "median_rtf", "peak_process_rss_mb",
        "error_type", "error_message",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(
    path: Path,
    overall_rows: list[dict[str, Any]],
    prompt_rows: list[dict[str, Any]],
    source_path: Path,
) -> None:
    """Write a Markdown overview and per-prompt comparison.

    Args:
        path: Destination Markdown path.
        overall_rows: One aggregated metrics row per config.
        prompt_rows: One metrics row per config and prompt.
        source_path: Input results file, recorded in the report for traceability.
    """
    lines = [
        "# Performance comparison",
        "",
        f"Source: `{source_path}`",
        "",
        "Overall P90 latency pools all successful prompt runs, so prompt lengths are mixed. "
        "Use the per-prompt table below for like-for-like latency comparisons. Lower RTF is faster; "
        "RTF below 1.0 indicates faster than real-time generation.",
        "",
        "## Overall by configuration",
        "",
        "| Config | P90 latency (s) | Median RTF | Peak process RSS (MB) | Successful / failed runs | Status |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in overall_rows:
        completed = f"{row['successful_runs']} / {row['failed_runs']}"
        status = "ok" if row["exit_code"] == 0 and row["failed_runs"] == 0 else "failed"
        if row["error_type"]:
            status += f" ({row['error_type']})"
        lines.append(
            f"| {row['config']} | {format_number(row['p90_latency_seconds'])} | "
            f"{format_number(row['median_rtf'])} | {format_number(row['peak_process_rss_mb'], 1)} | "
            f"{completed} | {status} |"
        )

    lines += [
        "",
        "## Per-prompt comparison",
        "",
        "| Config | Prompt | P90 latency (s) | Median RTF | Peak process RSS (MB) | Runs |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in prompt_rows:
        lines.append(
            f"| {row['config']} | {row['prompt']} | {format_number(row['p90_latency_seconds'])} | "
            f"{format_number(row['median_rtf'])} | "
            f"{format_number(row['peak_process_rss_mb'], 1)} | {row['successful_runs']} |"
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    """Parse paths, calculate comparisons, and write Markdown and CSV reports.

    Returns:
        Zero when comparison reports were written successfully.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("results.json"),
        help="Combined performance benchmark JSON file.",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        help="Markdown report path (defaults beside the input file).",
    )
    parser.add_argument(
        "--csv-output",
        type=Path,
        help="CSV report path (defaults beside the input file).",
    )
    args = parser.parse_args()

    input_path = args.input.expanduser().resolve()
    if not input_path.is_file():
        parser.error(f"Input file does not exist: {input_path}")
    markdown_path = args.markdown_output or input_path.parent / "performance_comparison.md"
    csv_path = args.csv_output or input_path.parent / "performance_comparison.csv"

    overall_rows = []
    prompt_rows = []
    for config_entry in load_results(input_path):
        overall, prompts = summarize_config(config_entry)
        overall_rows.append(overall)
        prompt_rows.extend(prompts)

    # Keep overview rows and per-prompt rows together so the CSV supports filtering.
    csv_rows = [
        {"analysis_scope": "all_prompts", **row} for row in overall_rows
    ] + [
        {"analysis_scope": "per_prompt", **row} for row in prompt_rows
    ]
    write_markdown(markdown_path, overall_rows, prompt_rows, input_path)
    write_csv(csv_path, csv_rows)
    print(f"Markdown comparison: {markdown_path.resolve()}")
    print(f"CSV comparison: {csv_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
