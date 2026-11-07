# Benchmark summary

Generated: 2026-11-06T23:45:08.648068+00:00
Backbone: `neuphonic/neutts-nano-q4-gguf` on `mps`
Codec: `neuphonic/neucodec` on `cpu`

Model load: **13.000 s**
Reference encoding: **10.012 s**
Peak process RSS: **5507.5 MB** (increase from pre-load: 5013.7 MB)

| Case | Median latency (s) | P90 latency (s) | Median RTF | Median audio (s) |
|---|---:|---:|---:|---:|
| short | 0.956 | 1.308 | 0.325 | 2.94 |
| medium | 2.987 | 3.088 | 0.385 | 7.76 |
| long | 3.462 | 3.855 | 0.270 | 12.80 |
| numbers_punctuation | 2.512 | 2.563 | 0.280 | 8.96 |
| questions_contractions | 2.217 | 2.237 | 0.290 | 7.64 |

RTF is wall-clock synthesis time divided by generated audio duration. Lower is faster; RTF below 1.0 is faster than real time.

Do not compare runs unless text, reference audio, transcript, seed, sampling settings, software versions and hardware conditions match.
