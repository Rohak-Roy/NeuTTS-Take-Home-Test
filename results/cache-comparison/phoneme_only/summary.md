# Benchmark summary

Generated: 2026-11-06T23:46:43.461679+00:00
Backbone: `neuphonic/neutts-nano-q4-gguf` on `mps`
Codec: `neuphonic/neucodec` on `cpu`

Model load: **13.935 s**
Reference encoding: **8.911 s**
Peak process RSS: **5417.0 MB** (increase from pre-load: 4922.7 MB)

| Case | Median latency (s) | P90 latency (s) | Median RTF | Median audio (s) |
|---|---:|---:|---:|---:|
| short | 0.978 | 1.019 | 0.333 | 2.94 |
| medium | 2.155 | 2.179 | 0.277 | 7.78 |
| long | 3.846 | 3.861 | 0.265 | 14.52 |
| numbers_punctuation | 1.671 | 1.700 | 0.282 | 5.92 |
| questions_contractions | 1.962 | 1.969 | 0.273 | 7.18 |

RTF is wall-clock synthesis time divided by generated audio duration. Lower is faster; RTF below 1.0 is faster than real time.

Do not compare runs unless text, reference audio, transcript, seed, sampling settings, software versions and hardware conditions match.
