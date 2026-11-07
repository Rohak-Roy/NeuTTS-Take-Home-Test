# Benchmark summary

Generated: 2026-11-06T23:43:28.188774+00:00
Backbone: `neuphonic/neutts-nano-q4-gguf` on `mps`
Codec: `neuphonic/neucodec` on `cpu`

Model load: **13.313 s**
Reference encoding: **9.655 s**
Peak process RSS: **5559.8 MB** (increase from pre-load: 5066.3 MB)

| Case | Median latency (s) | P90 latency (s) | Median RTF | Median audio (s) |
|---|---:|---:|---:|---:|
| short | 0.983 | 0.990 | 0.335 | 2.94 |
| medium | 2.132 | 2.149 | 0.274 | 7.78 |
| long | 3.823 | 3.827 | 0.263 | 14.52 |
| numbers_punctuation | 1.665 | 1.704 | 0.281 | 5.92 |
| questions_contractions | 1.961 | 1.975 | 0.273 | 7.18 |

RTF is wall-clock synthesis time divided by generated audio duration. Lower is faster; RTF below 1.0 is faster than real time.

Do not compare runs unless text, reference audio, transcript, seed, sampling settings, software versions and hardware conditions match.
