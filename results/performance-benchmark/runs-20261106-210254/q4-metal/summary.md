# Benchmark summary

Generated: 2026-11-06T21:17:11.522561+00:00
Backbone: `neuphonic/neutts-nano-q4-gguf` on `mps`
Codec: `neuphonic/neucodec` on `cpu`

Model load: **12.418 s**
Reference encoding: **9.735 s**
Peak process RSS: **6166.3 MB** (increase from pre-load: 5673.0 MB)

| Case | Median latency (s) | P90 latency (s) | Median RTF | Median audio (s) |
|---|---:|---:|---:|---:|
| short | 0.977 | 0.987 | 0.332 | 2.94 |
| medium | 2.123 | 2.290 | 0.273 | 7.78 |
| long | 3.835 | 5.054 | 0.264 | 14.52 |
| numbers_punctuation | 1.661 | 1.667 | 0.281 | 5.92 |
| questions_contractions | 2.013 | 2.254 | 0.280 | 7.18 |

RTF is wall-clock synthesis time divided by generated audio duration. Lower is faster; RTF below 1.0 is faster than real time.

Do not compare runs unless text, reference audio, transcript, seed, sampling settings, software versions and hardware conditions match.
