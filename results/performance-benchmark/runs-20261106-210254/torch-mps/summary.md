# Benchmark summary

Generated: 2026-11-06T22:13:35.766277+00:00
Backbone: `neuphonic/neutts-nano` on `mps`
Codec: `neuphonic/neucodec` on `cpu`

Model load: **7.960 s**
Reference encoding: **10.005 s**
Peak process RSS: **5839.7 MB** (increase from pre-load: 5345.7 MB)

| Case | Median latency (s) | P90 latency (s) | Median RTF | Median audio (s) |
|---|---:|---:|---:|---:|
| short | 2.492 | 2.523 | 0.793 | 3.14 |
| medium | 5.999 | 6.231 | 0.748 | 8.02 |
| long | 11.391 | 13.677 | 0.789 | 14.44 |
| numbers_punctuation | 7.402 | 7.631 | 0.751 | 9.86 |
| questions_contractions | 5.668 | 5.963 | 0.770 | 7.36 |

RTF is wall-clock synthesis time divided by generated audio duration. Lower is faster; RTF below 1.0 is faster than real time.

Do not compare runs unless text, reference audio, transcript, seed, sampling settings, software versions and hardware conditions match.
