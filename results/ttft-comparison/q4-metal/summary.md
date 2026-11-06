# Benchmark summary

Generated: 2026-11-06T22:53:49.971681+00:00
Backbone: `neuphonic/neutts-nano-q4-gguf` on `mps`
Codec: `neuphonic/neucodec` on `cpu`

Model load: **12.973 s**
Reference encoding: **12.052 s**
Peak process RSS: **4963.4 MB** (increase from pre-load: 4470.1 MB)

| Case | Median latency (s) | P90 latency (s) | Median RTF | Median audio (s) |
|---|---:|---:|---:|---:|
| short | 0.989 | 1.040 | 0.336 | 2.94 |
| medium | 2.129 | 2.144 | 0.274 | 7.78 |
| long | 5.115 | 6.009 | 0.352 | 14.52 |
| numbers_punctuation | 1.678 | 1.742 | 0.283 | 5.92 |
| questions_contractions | 1.970 | 1.984 | 0.274 | 7.18 |

RTF is wall-clock synthesis time divided by generated audio duration. Lower is faster; RTF below 1.0 is faster than real time.

Do not compare runs unless text, reference audio, transcript, seed, sampling settings, software versions and hardware conditions match.
