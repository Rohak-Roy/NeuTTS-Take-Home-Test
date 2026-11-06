# Benchmark summary

Generated: 2026-11-06T22:19:44.432359+00:00
Backbone: `neuphonic/neutts-nano-q4-gguf` on `mps`
Codec: `neuphonic/neucodec-onnx-decoder-int8` on `cpu`

Model load: **10.499 s**
Pre-encoded reference load: **0.001 s**
Peak process RSS: **2223.2 MB** (increase from pre-load: 1729.5 MB)

| Case | Median latency (s) | P90 latency (s) | Median RTF | Median audio (s) |
|---|---:|---:|---:|---:|
| short | 0.968 | 0.972 | 0.331 | 2.92 |
| medium | 2.190 | 2.233 | 0.282 | 7.76 |
| long | 4.115 | 4.126 | 0.284 | 14.50 |
| numbers_punctuation | 1.660 | 1.673 | 0.281 | 5.90 |
| questions_contractions | 2.037 | 2.077 | 0.285 | 7.16 |

RTF is wall-clock synthesis time divided by generated audio duration. Lower is faster; RTF below 1.0 is faster than real time.

Do not compare runs unless text, reference audio, transcript, seed, sampling settings, software versions and hardware conditions match.
