#!/usr/bin/env python3
"""Reproducible, local NeuTTS-Nano benchmark runner.

Measures model load, reference encoding, end-to-end synthesis, backbone generation,
codec decoding, audio duration, real-time factor and process RSS. It does not
claim that RSS captures every Metal/unified-memory allocation.
"""
from __future__ import annotations

import argparse
import csv
import importlib.metadata
import json
import os
import platform
import re
import statistics
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterator

import numpy as np
import psutil
import soundfile as sf

SPEECH_TOKEN_RE = re.compile(r"<\|speech_(\d+)\|>")
REPOSITORY_ROOT = Path(__file__).resolve().parent


class RSSSampler:
    """Sample this process's resident set size while the benchmark is running.

    Args:
        interval: Delay in seconds between RSS samples.
    """
    def __init__(self, interval: float = 0.02) -> None:
        self.interval = interval
        self.process = psutil.Process(os.getpid())
        self.baseline = self.process.memory_info().rss
        self.peak = self.baseline
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def _sample(self) -> None:
        """Update the recorded peak until sampling is stopped."""
        while not self._stop.is_set():
            try:
                self.peak = max(self.peak, self.process.memory_info().rss)
            except psutil.Error:
                pass
            self._stop.wait(self.interval)

    def start(self) -> None:
        """Start the background RSS sampling thread."""
        self._thread = threading.Thread(target=self._sample, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop sampling and take one final RSS measurement."""
        self._stop.set()
        if self._thread is not None:
            self._thread.join()
        try:
            self.peak = max(self.peak, self.process.memory_info().rss)
        except psutil.Error:
            pass

    @property
    def peak_mb(self) -> float:
        """Return peak RSS in mebibytes."""
        return self.peak / (1024 * 1024)

    @property
    def delta_mb(self) -> float:
        """Return peak RSS growth above the initial baseline in mebibytes."""
        return max(0.0, self.peak - self.baseline) / (1024 * 1024)


def run_command(args: list[str]) -> str | None:
    """Return a command's trimmed output, or ``None`` if it cannot run.

    Args:
        args: Command and arguments passed to ``subprocess``.

    Returns:
        Standard output with surrounding whitespace removed, or ``None``.
    """
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def package_version(name: str) -> str | None:
    """Return an installed package version when the package is available.

    Args:
        name: Installed distribution name.

    Returns:
        Version string, or ``None`` if the distribution is not installed.
    """
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def hardware_info() -> dict[str, Any]:
    """Collect host hardware, software versions, and accelerator availability.

    Returns:
        JSON-serializable host and runtime information.
    """
    info: dict[str, Any] = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "platform": platform.platform(),
        "system": platform.system(),
        "macos_version": platform.mac_ver()[0] or None,
        "machine": platform.machine(),
        "processor": platform.processor(),
        "mac_hardware_model_id": run_command(["sysctl", "-n", "hw.model"]),
        "logical_cpu_count": os.cpu_count(),
        "physical_memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "python_version": platform.python_version(),
        "neutts_version": package_version("neutts"),
        "torch_version": package_version("torch"),
        "llama_cpp_python_version": package_version("llama-cpp-python"),
        "onnxruntime_version": package_version("onnxruntime"),
        "perf_core_count": run_command(["sysctl", "-n", "hw.perflevel0.physicalcpu"]),
        "physical_core_count": run_command(["sysctl", "-n", "hw.physicalcpu"]),
    }
    try:
        import torch

        info["torch_mps_available"] = bool(torch.backends.mps.is_available())
        info["torch_mps_built"] = bool(torch.backends.mps.is_built())
    except Exception as exc:  # hardware report should not hide a useful benchmark error
        info["torch_mps_error"] = str(exc)
    try:
        import llama_cpp

        info["llama_cpp_module"] = getattr(llama_cpp, "__file__", None)
        low_level = getattr(llama_cpp, "llama_cpp", None)
        supports_gpu = getattr(low_level, "llama_supports_gpu_offload", None)
        if callable(supports_gpu):
            info["llama_cpp_gpu_offload_supported"] = bool(supports_gpu())
    except Exception as exc:
        info["llama_cpp_probe_error"] = str(exc)
    return info


def percentiles(values: list[float]) -> dict[str, float | None]:
    """Summarize latency samples with mean, median, p90, and sample deviation.

    Args:
        values: Measured values for one prompt/configuration.

    Returns:
        Summary statistics rounded to microsecond precision.
    """
    if not values:
        return {"mean": None, "median": None, "p90": None, "stdev": None}
    ordered = sorted(values)
    p90_index = min(len(ordered) - 1, max(0, int(np.ceil(0.90 * len(ordered))) - 1))
    return {
        "mean": round(statistics.fmean(values), 6),
        "median": round(float(statistics.median(values)), 6),
        "p90": round(float(ordered[p90_index]), 6),
        "stdev": round(float(statistics.stdev(values)), 6) if len(values) > 1 else 0.0,
    }


def load_config(path: Path) -> dict[str, Any]:
    """Read a config JSON file and check fields used by this runner.

    Args:
        path: Path to the configuration JSON file.

    Returns:
        Configuration mapping.

    Raises:
        ValueError: If required config fields are missing.
    """
    with path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    required = [
        "backbone_repo",
        "backbone_device",
        "codec_repo",
        "codec_device",
        "reference_audio",
        "reference_text_file",
        "prompts_file",
        "output_dir",
    ]
    missing = [key for key in required if key not in config]
    if missing:
        raise ValueError(f"Missing config fields: {', '.join(missing)}")
    return config


def timed_method(
    obj: Any,
    method_name: str,
    timings: list[float],
    token_counts: list[int] | None = None,
    synchronize: Callable[[], None] | None = None,
) -> None:
    """Wrap a NeuTTS stage method and collect duration and optional token count.

    Args:
        obj: NeuTTS instance whose method is instrumented.
        method_name: Private stage method name, such as ``_infer_ggml``.
        timings: List receiving elapsed time for each invocation.
        token_counts: Optional list receiving speech-token counts from ``_decode``.
        synchronize: Optional callback that waits for asynchronous device work.
    """
    original: Callable[..., Any] = getattr(obj, method_name)

    def wrapped(*args: Any, **kwargs: Any) -> Any:
        if synchronize is not None:
            synchronize()
        started = time.perf_counter()
        result = original(*args, **kwargs)
        if synchronize is not None:
            synchronize()
        timings.append(time.perf_counter() - started)
        if token_counts is not None:
            source = args[0] if args else kwargs.get("codes", "")
            if isinstance(source, str):
                token_counts.append(len(SPEECH_TOKEN_RE.findall(source)))
        return result

    setattr(obj, method_name, wrapped)


def timed_first_generated_token(
    backbone: Any,
    request_start: list[float | None],
    timings: list[float],
) -> None:
    """Record request-to-first-token time for llama.cpp generation.

    Args:
        backbone: llama.cpp model instance with a ``generate`` token iterator.
        request_start: One-item state list set immediately before each measured inference.
        timings: List receiving time to the first yielded token for each measured call.
    """
    original_generate: Callable[..., Iterator[int]] = backbone.generate

    def wrapped_generate(*args: Any, **kwargs: Any) -> Iterator[int]:
        for token in original_generate(*args, **kwargs):
            started = request_start[0]
            if started is not None:
                # The first yielded token means prompt prefill and first-token sampling finished.
                timings.append(time.perf_counter() - started)
                request_start[0] = None
            yield token

    backbone.generate = wrapped_generate


def resolve_path(value: str | Path) -> Path:
    """Resolve a relative input path from the repository root.

    Args:
        value: Absolute or repository-relative path.

    Returns:
        Expanded, absolute path.
    """
    path = Path(value).expanduser()
    return path if path.is_absolute() else REPOSITORY_ROOT / path


def resolve_gguf_backbone(repo_or_path: str) -> tuple[str, str | None]:
    """Resolve a GGUF repo ID to its cached file and return its language.

    Args:
        repo_or_path: Hugging Face repo ID or an existing local GGUF path.

    Returns:
        Effective model path/repo and an optional language code.

    Raises:
        FileNotFoundError: If a repo ID has no local cached GGUF file.
    """
    if not repo_or_path.lower().endswith("gguf"):
        return repo_or_path, None

    from neutts.neutts import BACKBONE_LANGUAGE_MAP

    language = BACKBONE_LANGUAGE_MAP.get(repo_or_path)
    local_path = resolve_path(repo_or_path)
    if local_path.is_file():
        return str(local_path), language

    cache_name = "models--" + repo_or_path.replace("/", "--")
    snapshots = REPOSITORY_ROOT / "models" / "huggingface" / "hub" / cache_name / "snapshots"
    for snapshot in sorted(snapshots.glob("*")):
        candidates = sorted(snapshot.glob("*.gguf"))
        if candidates:
            # Preserve the .gguf symlink name: llama-cpp-python uses its suffix
            # to distinguish a local GGUF file from a Hugging Face repo ID.
            return str(candidates[0].absolute()), language
    raise FileNotFoundError(f"No cached GGUF file found for {repo_or_path!r} in {snapshots}")


def resolve_cached_model_file(repo_id: str, filename: str) -> Path:
    """Find a named file in a repository's local Hugging Face snapshot.

    Args:
        repo_id: Hugging Face model repository identifier.
        filename: File expected inside a snapshot directory.

    Returns:
        Path to the cached snapshot file.

    Raises:
        FileNotFoundError: If no snapshot contains the requested file.
    """
    cache_name = "models--" + repo_id.replace("/", "--")
    snapshots = REPOSITORY_ROOT / "models" / "huggingface" / "hub" / cache_name / "snapshots"
    for snapshot in sorted(snapshots.glob("*")):
        candidate = snapshot / filename
        if candidate.is_file():
            return candidate.absolute()
    raise FileNotFoundError(f"Cached {filename!r} not found for {repo_id!r} in {snapshots}")


def configure_local_codec(repo_id: str) -> str:
    """Make optional codecs load from the files already cached in this repository.

    The distill and ONNX snapshots contain their weight files but omit the
    ``config.json`` that the generic Hugging Face mixin tries to fetch first.
    The distill codec's custom loader needs only its checkpoint and metadata;
    the ONNX decoder can be initialized directly from its local graph file.

    Args:
        repo_id: Codec repository identifier from the benchmark config.

    Returns:
        A codec identifier or local path accepted by NeuTTS.
    """
    if "onnx" in repo_id:
        return str(resolve_cached_model_file(repo_id, "model.onnx"))
    if repo_id == "neuphonic/distill-neucodec":
        from neucodec.model import DistillNeuCodec

        # Bypass only the generic config.json lookup; _from_pretrained still
        # loads the checked-in pytorch_model.bin and meta.yaml from HF's cache.
        def load_cached_distill(cls: type, model_id: str, **kwargs: Any) -> Any:
            return cls._from_pretrained(model_id=model_id, local_files_only=True)

        DistillNeuCodec.from_pretrained = classmethod(load_cached_distill)
    return repo_id


def main() -> int:
    """Run one config's prompts and write audio, JSON, CSV, and Markdown.

    Returns:
        Zero if at least one measured inference succeeds; otherwise one.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/q8-cpu.json"),
        help="Config JSON path; the shell runner invokes this once per config.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Override the config's output_dir (used by performance_benchmark.sh).",
    )
    parser.add_argument("--repeats", type=int, help="Override the config's repeat count.")
    parser.add_argument(
        "--warmup-runs", type=int, help="Override the config's warmup count per prompt."
    )
    parser.add_argument(
        "--kv-cache",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Enable or disable GGUF common-prefix KV-cache reuse.",
    )
    parser.add_argument(
        "--phoneme-cache",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Enable or disable per-instance phonemization result caching.",
    )
    args = parser.parse_args()
    config_path = resolve_path(args.config)
    config = load_config(config_path)

    # CLI overrides make short smoke runs possible without editing config files.
    warmups = args.warmup_runs if args.warmup_runs is not None else int(config.get("warmup_runs", 1))
    repeats = args.repeats if args.repeats is not None else int(config.get("repeats", 5))
    cache_kv = args.kv_cache if args.kv_cache is not None else bool(config.get("cache_kv", True))
    cache_phonemes = (
        args.phoneme_cache
        if args.phoneme_cache is not None
        else bool(config.get("cache_phonemes", True))
    )
    if warmups < 1 or repeats < 1:
        parser.error("warmup_runs and repeats must both be >= 1")

    output_dir = resolve_path(args.output_dir or config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    prompts_path = resolve_path(config["prompts_file"])
    prompts = json.loads(prompts_path.read_text(encoding="utf-8"))
    if not isinstance(prompts, list) or not prompts:
        raise ValueError("prompts_file must contain a non-empty JSON list")

    reference_audio = resolve_path(config["reference_audio"])
    reference_text_path = resolve_path(config["reference_text_file"])
    for path in (reference_audio, reference_text_path, prompts_path):
        if not path.exists():
            raise FileNotFoundError(f"Required input file not found: {path}")
    reference_text = reference_text_path.read_text(encoding="utf-8").strip()
    if not reference_text:
        raise ValueError("Reference transcript is empty")

    # Use repository-local cached weights and avoid contacting Hugging Face.
    os.environ.setdefault("HF_HOME", str(REPOSITORY_ROOT / "models" / "huggingface"))
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

    # Import only after validating user-supplied paths, so common setup errors are clear.
    from neutts import NeuTTS
    effective_backbone, language = resolve_gguf_backbone(str(config["backbone_repo"]))
    config["resolved_backbone_path"] = effective_backbone
    effective_codec = configure_local_codec(str(config["codec_repo"]))
    if effective_codec != config["codec_repo"]:
        config["resolved_codec_path"] = effective_codec
    config["cache_kv"] = cache_kv
    config["cache_phonemes"] = cache_phonemes

    sampler = RSSSampler()
    sampler.start()
    process = psutil.Process(os.getpid())
    rss_before_model_mb = process.memory_info().rss / (1024 * 1024)

    load_started = time.perf_counter()
    tts = NeuTTS(
        backbone_repo=effective_backbone,
        backbone_device=config["backbone_device"],
        codec_repo=effective_codec,
        codec_device=config["codec_device"],
        language=language,
        seed=int(config.get("seed", 1234)),
        cache_kv=cache_kv,
        cache_phonemes=cache_phonemes,
    )
    model_load_seconds = time.perf_counter() - load_started

    # Torch and llama.cpp calls can enqueue asynchronous MPS work. Synchronize
    # around timed stages so their durations include completed GPU operations.
    import torch

    def synchronize() -> None:
        if "mps" in (
            str(config["backbone_device"]).lower(),
            str(config["codec_device"]).lower(),
        ):
            torch.mps.synchronize()

    synchronize()

    reference_codes_load_seconds: float | None = None
    if config.get("reference_codes_file"):
        codes_path = resolve_path(config["reference_codes_file"])
        if not codes_path.exists():
            raise FileNotFoundError(f"Pre-encoded reference codes not found: {codes_path}")
        import torch
        ref_started = time.perf_counter()
        try:
            ref_codes = torch.load(codes_path, map_location="cpu", weights_only=True)
        except TypeError:  # compatibility with older torch releases
            ref_codes = torch.load(codes_path, map_location="cpu")
        synchronize()
        reference_codes_load_seconds = time.perf_counter() - ref_started
        reference_encode_seconds = None
    else:
        synchronize()
        ref_started = time.perf_counter()
        ref_codes = tts.encode_reference(str(reference_audio))
        synchronize()
        reference_encode_seconds = time.perf_counter() - ref_started

    stage_backbone: list[float] = []
    stage_codec: list[float] = []
    generated_token_counts: list[int] = []
    first_token_samples: list[float] = []
    request_start: list[float | None] = [None]

    # These wrappers instrument the library's existing stage boundaries without
    # editing upstream code. The private method names are version-sensitive.
    if hasattr(tts, "_infer_ggml"):
        timed_method(tts, "_infer_ggml", stage_backbone, synchronize=synchronize)
        # llama.cpp exposes generated token IDs as an iterator, allowing direct TTFT timing.
        timed_first_generated_token(tts.backbone, request_start, first_token_samples)
    if hasattr(tts, "_infer_torch"):
        timed_method(tts, "_infer_torch", stage_backbone, synchronize=synchronize)
    timed_method(tts, "_decode", stage_codec, generated_token_counts, synchronize)

    temperature = float(config.get("temperature", 1.0))
    top_k = int(config.get("top_k", 50))
    # Warm each prompt independently so its first measured run avoids cache/setup costs.
    for prompt in prompts:
        warmup_text = str(prompt["text"])
        for _ in range(warmups):
            synchronize()
            tts.infer(warmup_text, ref_codes, reference_text,
                      temperature=temperature, top_k=top_k)
            synchronize()

    records: list[dict[str, Any]] = []
    sample_rate = int(getattr(tts, "sample_rate", 24000))
    for prompt_index, prompt in enumerate(prompts):
        case_id = str(prompt.get("id", f"prompt_{prompt_index + 1}"))
        text = str(prompt["text"])
        for repeat in range(repeats):
            stage_backbone.clear()
            stage_codec.clear()
            generated_token_counts.clear()
            first_token_samples.clear()
            synchronize()
            started = time.perf_counter()
            request_start[0] = started
            try:
                wav = tts.infer(text, ref_codes, reference_text,
                                temperature=temperature, top_k=top_k)
                synchronize()
                wall_seconds = time.perf_counter() - started
                wav_array = np.asarray(wav, dtype=np.float32).reshape(-1)
                if wav_array.size == 0 or not np.isfinite(wav_array).all():
                    raise ValueError("Inference returned empty audio or non-finite samples")
            except Exception as exc:
                request_start[0] = None
                records.append({
                    "case_id": case_id,
                    "repeat": repeat + 1,
                    "text_chars": len(text),
                    "text_words": len(text.split()),
                    "status": "error",
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                })
                continue
            request_start[0] = None
            audio_seconds = len(wav_array) / sample_rate
            backbone_seconds = stage_backbone[-1] if stage_backbone else None
            codec_seconds = stage_codec[-1] if stage_codec else None
            token_count = generated_token_counts[-1] if generated_token_counts else None
            other_seconds = (max(0.0, wall_seconds - (backbone_seconds or 0.0)
                                 - (codec_seconds or 0.0)))
            rtf = wall_seconds / audio_seconds if audio_seconds > 0 else None
            token_rate = (token_count / backbone_seconds
                          if token_count is not None and backbone_seconds else None)
            wav_name = f"{case_id}_repeat_{repeat + 1:02d}.wav"
            wav_path = output_dir / "audio" / wav_name
            wav_path.parent.mkdir(parents=True, exist_ok=True)
            sf.write(wav_path, wav_array, sample_rate)
            records.append({
                "case_id": case_id,
                "repeat": repeat + 1,
                "status": "ok",
                "text_chars": len(text),
                "text_words": len(text.split()),
                "wall_seconds": wall_seconds,
                "time_to_first_token_seconds": (
                    first_token_samples[0] if first_token_samples else None
                ),
                "backbone_seconds": backbone_seconds,
                "codec_decode_seconds": codec_seconds,
                "other_seconds": other_seconds,
                "audio_seconds": audio_seconds,
                "rtf": rtf,
                "audio_seconds_per_wall_second": (audio_seconds / wall_seconds
                                                   if wall_seconds > 0 else None),
                "speech_tokens": token_count,
                "speech_tokens_per_second": token_rate,
                "wav_path": str(wav_path),
            })

    sampler.stop()
    ttft_values = [
        float(record["time_to_first_token_seconds"])
        for record in records
        if record.get("time_to_first_token_seconds") is not None
    ]
    metadata = {
        "hardware": hardware_info(),
        "config": config,
        "measurement": {
            "model_load_seconds": model_load_seconds,
            "reference_encode_seconds": reference_encode_seconds,
            "reference_codes_load_seconds": reference_codes_load_seconds,
            "phonemization_cache": tts.phonemization_cache_info(),
            "median_time_to_first_token_seconds": (
                round(float(statistics.median(ttft_values)), 6) if ttft_values else None
            ),
            "rss_before_model_mb": round(rss_before_model_mb, 2),
            "peak_process_rss_mb": round(sampler.peak_mb, 2),
            "peak_process_rss_delta_mb": round(sampler.delta_mb, 2),
            "memory_note": "Process RSS is a useful lower-bound indicator, not a complete measurement of all shared Metal/unified-memory allocations.",
            "sample_rate_hz": sample_rate,
            "warmup_runs": warmups,
            "repeats_per_prompt": repeats,
        },
        "records": records,
    }
    (output_dir / "results.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8")

    csv_path = output_dir / "results.csv"
    if records:
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            fieldnames = list(dict.fromkeys(key for record in records for key in record))
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)

    summary_lines = [
        "# Benchmark summary", "",
        f"Generated: {metadata['hardware']['timestamp_utc']}",
        f"Backbone: `{config['backbone_repo']}` on `{config['backbone_device']}`",
        f"Codec: `{config['codec_repo']}` on `{config['codec_device']}`", "",
        f"Model load: **{model_load_seconds:.3f} s**",
        (f"Reference encoding: **{reference_encode_seconds:.3f} s**" if reference_encode_seconds is not None
         else f"Pre-encoded reference load: **{reference_codes_load_seconds:.3f} s**"),
        f"Peak process RSS: **{sampler.peak_mb:.1f} MB** "
        f"(increase from pre-load: {sampler.delta_mb:.1f} MB)", "",
        "| Case | Median latency (s) | P90 latency (s) | Median RTF | Median audio (s) |",
        "|---|---:|---:|---:|---:|",
    ]
    for case_id in dict.fromkeys(r["case_id"] for r in records):
        subset = [r for r in records if r["case_id"] == case_id and r.get("status") == "ok"]
        if not subset:
            summary_lines.append(f"| {case_id} | failed | failed | — | — |")
            continue
        lat = percentiles([r["wall_seconds"] for r in subset])
        rtf_stats = percentiles([r["rtf"] for r in subset if r["rtf"] is not None])
        audio_stats = percentiles([r["audio_seconds"] for r in subset])
        summary_lines.append(
            f"| {case_id} | {lat['median']:.3f} | {lat['p90']:.3f} | "
            f"{rtf_stats['median']:.3f} | {audio_stats['median']:.2f} |"
        )
    summary_lines += ["", "RTF is wall-clock synthesis time divided by generated audio duration. "
                     "Lower is faster; RTF below 1.0 is faster than real time.",
                     "", "Do not compare runs unless text, reference audio, transcript, "
                     "seed, sampling settings, software versions and hardware conditions match."]
    (output_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"Benchmark complete. Results: {output_dir.resolve()}")
    reference_summary = (f"reference encode: {reference_encode_seconds:.2f}s"
                         if reference_encode_seconds is not None
                         else f"pre-encoded codes load: {reference_codes_load_seconds:.2f}s")
    print(f"Model load: {model_load_seconds:.2f}s | {reference_summary}")
    print(f"Peak process RSS: {sampler.peak_mb:.0f} MB (delta {sampler.delta_mb:.0f} MB)")
    print(f"Summary: {(output_dir / 'summary.md').resolve()}")
    return 0 if any(record.get("status") == "ok" for record in records) else 1


if __name__ == "__main__":
    raise SystemExit(main())
