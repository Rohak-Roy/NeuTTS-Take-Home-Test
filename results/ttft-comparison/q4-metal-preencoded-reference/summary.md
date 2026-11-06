# Benchmark summary

Generated: 2026-11-06T22:55:20.870139+00:00
Backbone: `neuphonic/neutts-nano-q4-gguf` on `mps`
Codec: `neuphonic/neucodec` on `cpu`

Model load: **12.589 s**
Pre-encoded reference load: **0.001 s**
Peak process RSS: **3168.0 MB** (increase from pre-load: 2674.0 MB)

| Case | Median latency (s) | P90 latency (s) | Median RTF | Median audio (s) |
|---|---:|---:|---:|---:|
| short | 1.027 | 1.034 | 0.349 | 2.94 |
| medium | 2.309 | 2.662 | 0.297 | 7.78 |
| long | 3.895 | 6.354 | 0.268 | 14.52 |
| numbers_punctuation | 1.668 | 1.833 | 0.282 | 5.92 |
| questions_contractions | 1.985 | 2.290 | 0.277 | 7.18 |

RTF is wall-clock synthesis time divided by generated audio duration. Lower is faster; RTF below 1.0 is faster than real time.

Do not compare runs unless text, reference audio, transcript, seed, sampling settings, software versions and hardware conditions match.
