# Benchmark summary

Generated: 2026-11-06T21:13:34.926838+00:00
Backbone: `neuphonic/neutts-nano-q4-gguf` on `cpu`
Codec: `neuphonic/neucodec` on `cpu`

Model load: **12.500 s**
Reference encoding: **8.259 s**
Peak process RSS: **6082.6 MB** (increase from pre-load: 5588.2 MB)

| Case | Median latency (s) | P90 latency (s) | Median RTF | Median audio (s) |
|---|---:|---:|---:|---:|
| short | 20.334 | 20.475 | 7.761 | 2.62 |
| medium | 18.579 | 19.063 | 2.352 | 7.90 |
| long | 22.930 | 22.993 | 1.876 | 12.22 |
| numbers_punctuation | 22.286 | 22.433 | 2.361 | 9.44 |
| questions_contractions | 18.311 | 18.361 | 2.391 | 7.66 |

RTF is wall-clock synthesis time divided by generated audio duration. Lower is faster; RTF below 1.0 is faster than real time.

Do not compare runs unless text, reference audio, transcript, seed, sampling settings, software versions and hardware conditions match.
