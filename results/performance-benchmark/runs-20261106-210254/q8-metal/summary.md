# Benchmark summary

Generated: 2026-11-06T21:30:31.600812+00:00
Backbone: `neuphonic/neutts-nano-q8-gguf` on `mps`
Codec: `neuphonic/neucodec` on `cpu`

Model load: **13.088 s**
Reference encoding: **10.942 s**
Peak process RSS: **5161.5 MB** (increase from pre-load: 4667.9 MB)

| Case | Median latency (s) | P90 latency (s) | Median RTF | Median audio (s) |
|---|---:|---:|---:|---:|
| short | 0.986 | 1.207 | 0.362 | 2.72 |
| medium | 2.517 | 2.678 | 0.287 | 8.76 |
| long | 4.148 | 4.200 | 0.286 | 14.52 |
| numbers_punctuation | 2.712 | 2.767 | 0.285 | 9.52 |
| questions_contractions | 2.265 | 2.515 | 0.301 | 7.52 |

RTF is wall-clock synthesis time divided by generated audio duration. Lower is faster; RTF below 1.0 is faster than real time.

Do not compare runs unless text, reference audio, transcript, seed, sampling settings, software versions and hardware conditions match.
