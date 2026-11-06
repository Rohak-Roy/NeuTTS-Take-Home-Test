# Benchmark summary

Generated: 2026-11-06T22:15:50.379069+00:00
Backbone: `neuphonic/neutts-nano-q4-gguf` on `mps`
Codec: `neuphonic/distill-neucodec` on `cpu`

Model load: **12.908 s**
Reference encoding: **1.679 s**
Peak process RSS: **4100.0 MB** (increase from pre-load: 3606.7 MB)

| Case | Median latency (s) | P90 latency (s) | Median RTF | Median audio (s) |
|---|---:|---:|---:|---:|
| short | 0.992 | 1.114 | 0.347 | 2.86 |
| medium | 2.312 | 2.513 | 0.273 | 8.48 |
| long | 5.214 | 5.492 | 0.360 | 14.50 |
| numbers_punctuation | 2.643 | 2.791 | 0.284 | 9.30 |
| questions_contractions | 2.081 | 2.088 | 0.270 | 7.70 |

RTF is wall-clock synthesis time divided by generated audio duration. Lower is faster; RTF below 1.0 is faster than real time.

Do not compare runs unless text, reference audio, transcript, seed, sampling settings, software versions and hardware conditions match.
