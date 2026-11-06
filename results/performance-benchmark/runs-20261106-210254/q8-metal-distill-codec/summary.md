# Benchmark summary

Generated: 2026-11-06T22:17:41.636198+00:00
Backbone: `neuphonic/neutts-nano-q8-gguf` on `mps`
Codec: `neuphonic/distill-neucodec` on `cpu`

Model load: **12.382 s**
Reference encoding: **1.432 s**
Peak process RSS: **4275.4 MB** (increase from pre-load: 3781.0 MB)

| Case | Median latency (s) | P90 latency (s) | Median RTF | Median audio (s) |
|---|---:|---:|---:|---:|
| short | 0.992 | 1.003 | 0.378 | 2.62 |
| medium | 2.340 | 2.401 | 0.295 | 7.94 |
| long | 4.133 | 6.107 | 0.285 | 14.50 |
| numbers_punctuation | 2.442 | 2.455 | 0.288 | 8.48 |
| questions_contractions | 2.184 | 2.195 | 0.291 | 7.50 |

RTF is wall-clock synthesis time divided by generated audio duration. Lower is faster; RTF below 1.0 is faster than real time.

Do not compare runs unless text, reference audio, transcript, seed, sampling settings, software versions and hardware conditions match.
