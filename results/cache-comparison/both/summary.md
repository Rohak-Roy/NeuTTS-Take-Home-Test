# Benchmark summary

Generated: 2026-11-06T23:48:29.872508+00:00
Backbone: `neuphonic/neutts-nano-q4-gguf` on `mps`
Codec: `neuphonic/neucodec` on `cpu`

Model load: **12.061 s**
Reference encoding: **9.493 s**
Peak process RSS: **5568.8 MB** (increase from pre-load: 5074.8 MB)

| Case | Median latency (s) | P90 latency (s) | Median RTF | Median audio (s) |
|---|---:|---:|---:|---:|
| short | 1.187 | 1.297 | 0.404 | 2.94 |
| medium | 2.804 | 3.432 | 0.361 | 7.76 |
| long | 3.798 | 5.258 | 0.297 | 12.80 |
| numbers_punctuation | 2.811 | 4.550 | 0.314 | 8.96 |
| questions_contractions | 2.158 | 2.284 | 0.283 | 7.64 |

RTF is wall-clock synthesis time divided by generated audio duration. Lower is faster; RTF below 1.0 is faster than real time.

Do not compare runs unless text, reference audio, transcript, seed, sampling settings, software versions and hardware conditions match.
