# Benchmark summary

Generated: 2026-11-06T22:21:18.812735+00:00
Backbone: `neuphonic/neutts-nano-q8-gguf` on `mps`
Codec: `neuphonic/neucodec-onnx-decoder-int8` on `cpu`

Model load: **10.647 s**
Pre-encoded reference load: **0.000 s**
Peak process RSS: **2316.9 MB** (increase from pre-load: 1823.5 MB)

| Case | Median latency (s) | P90 latency (s) | Median RTF | Median audio (s) |
|---|---:|---:|---:|---:|
| short | 0.954 | 0.968 | 0.353 | 2.70 |
| medium | 2.544 | 2.552 | 0.291 | 8.74 |
| long | 4.290 | 4.441 | 0.296 | 14.50 |
| numbers_punctuation | 2.773 | 2.859 | 0.292 | 9.50 |
| questions_contractions | 2.232 | 2.250 | 0.298 | 7.50 |

RTF is wall-clock synthesis time divided by generated audio duration. Lower is faster; RTF below 1.0 is faster than real time.

Do not compare runs unless text, reference audio, transcript, seed, sampling settings, software versions and hardware conditions match.
