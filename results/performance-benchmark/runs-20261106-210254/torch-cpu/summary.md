# Benchmark summary

Generated: 2026-11-06T22:09:47.672437+00:00
Backbone: `neuphonic/neutts-nano` on `cpu`
Codec: `neuphonic/neucodec` on `cpu`

Model load: **7.510 s**
Reference encoding: **8.326 s**
Peak process RSS: **5694.3 MB** (increase from pre-load: 5199.9 MB)

| Case | Median latency (s) | P90 latency (s) | Median RTF | Median audio (s) |
|---|---:|---:|---:|---:|
| short | 5.412 | 5.490 | 2.553 | 2.12 |
| medium | 12.943 | 13.020 | 1.575 | 8.22 |
| long | 20.758 | 21.664 | 1.430 | 14.52 |
| numbers_punctuation | 14.542 | 14.977 | 1.460 | 9.96 |
| questions_contractions | 11.699 | 11.792 | 1.543 | 7.58 |

RTF is wall-clock synthesis time divided by generated audio duration. Lower is faster; RTF below 1.0 is faster than real time.

Do not compare runs unless text, reference audio, transcript, seed, sampling settings, software versions and hardware conditions match.
