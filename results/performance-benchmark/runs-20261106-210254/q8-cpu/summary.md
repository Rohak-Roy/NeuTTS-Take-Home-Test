# Benchmark summary

Generated: 2026-11-06T21:28:06.800581+00:00
Backbone: `neuphonic/neutts-nano-q8-gguf` on `cpu`
Codec: `neuphonic/neucodec` on `cpu`

Model load: **12.467 s**
Reference encoding: **8.091 s**
Peak process RSS: **6045.7 MB** (increase from pre-load: 5551.3 MB)

| Case | Median latency (s) | P90 latency (s) | Median RTF | Median audio (s) |
|---|---:|---:|---:|---:|
| short | 20.384 | 20.524 | 7.780 | 2.62 |
| medium | 19.030 | 19.350 | 2.158 | 8.82 |
| long | 23.818 | 24.293 | 1.751 | 13.60 |
| numbers_punctuation | 22.582 | 22.597 | 2.397 | 9.42 |
| questions_contractions | 18.652 | 18.870 | 2.521 | 7.40 |

RTF is wall-clock synthesis time divided by generated audio duration. Lower is faster; RTF below 1.0 is faster than real time.

Do not compare runs unless text, reference audio, transcript, seed, sampling settings, software versions and hardware conditions match.
