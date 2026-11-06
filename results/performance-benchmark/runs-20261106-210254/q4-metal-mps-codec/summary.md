# Benchmark summary

Generated: 2026-11-06T21:15:20.336574+00:00
Backbone: `neuphonic/neutts-nano-q4-gguf` on `mps`
Codec: `neuphonic/neucodec` on `mps`

Model load: **15.702 s**
Reference encoding: **3.764 s**
Peak process RSS: **3101.5 MB** (increase from pre-load: 2607.3 MB)

| Case | Median latency (s) | P90 latency (s) | Median RTF | Median audio (s) |
|---|---:|---:|---:|---:|
| short | 0.963 | 0.984 | 0.327 | 2.94 |
| medium | 2.066 | 2.079 | 0.266 | 7.78 |
| long | 3.674 | 3.686 | 0.253 | 14.52 |
| numbers_punctuation | 1.672 | 1.694 | 0.283 | 5.92 |
| questions_contractions | 1.923 | 1.960 | 0.268 | 7.18 |

RTF is wall-clock synthesis time divided by generated audio duration. Lower is faster; RTF below 1.0 is faster than real time.

Do not compare runs unless text, reference audio, transcript, seed, sampling settings, software versions and hardware conditions match.
