# Performance comparison

Source: `/Users/rohakroy/Documents/NeuTTS-Take-Home-Test/results.json`

Overall P90 latency pools all successful prompt runs, so prompt lengths are mixed. Use the per-prompt table below for like-for-like latency comparisons. Lower RTF is faster; RTF below 1.0 indicates faster than real-time generation.

## Overall by configuration

| Config | P90 latency (s) | Median RTF | Peak process RSS (MB) | Successful / failed runs | Status |
|---|---:|---:|---:|---:|---|
| q4-cpu-layers0 | 22.930 | 2.370 | 6082.6 | 25 / 0 | ok |
| q4-metal | 3.835 | 0.280 | 6166.3 | 25 / 0 | ok |
| q4-metal-distill-codec | 5.214 | 0.296 | 4100.0 | 25 / 0 | ok |
| q4-metal-mps-codec | 3.674 | 0.268 | 3101.5 | 25 / 0 | ok |
| q4-metal-onnx-int8 | 4.115 | 0.284 | 2223.2 | 25 / 0 | ok |
| q8-cpu | 23.818 | 2.397 | 6045.7 | 25 / 0 | ok |
| q8-metal | 4.148 | 0.290 | 5161.6 | 25 / 0 | ok |
| q8-metal-distill-codec | 4.133 | 0.292 | 4275.4 | 25 / 0 | ok |
| q8-metal-onnx-int8 | 4.290 | 0.296 | 2316.9 | 25 / 0 | ok |
| torch-cpu | 20.758 | 1.543 | 5694.3 | 25 / 0 | ok |
| torch-mps | 11.391 | 0.767 | 5839.7 | 25 / 0 | ok |

## Per-prompt comparison

| Config | Prompt | P90 latency (s) | Median RTF | Peak process RSS (MB) | Runs |
|---|---|---:|---:|---:|---:|
| q4-cpu-layers0 | short | 20.475 | 7.761 | 6082.6 | 5 |
| q4-cpu-layers0 | medium | 19.063 | 2.352 | 6082.6 | 5 |
| q4-cpu-layers0 | long | 22.993 | 1.876 | 6082.6 | 5 |
| q4-cpu-layers0 | numbers_punctuation | 22.433 | 2.361 | 6082.6 | 5 |
| q4-cpu-layers0 | questions_contractions | 18.361 | 2.391 | 6082.6 | 5 |
| q4-metal | short | 0.987 | 0.332 | 6166.3 | 5 |
| q4-metal | medium | 2.290 | 0.273 | 6166.3 | 5 |
| q4-metal | long | 5.054 | 0.264 | 6166.3 | 5 |
| q4-metal | numbers_punctuation | 1.667 | 0.281 | 6166.3 | 5 |
| q4-metal | questions_contractions | 2.254 | 0.280 | 6166.3 | 5 |
| q4-metal-distill-codec | short | 1.114 | 0.347 | 4100.0 | 5 |
| q4-metal-distill-codec | medium | 2.513 | 0.273 | 4100.0 | 5 |
| q4-metal-distill-codec | long | 5.492 | 0.360 | 4100.0 | 5 |
| q4-metal-distill-codec | numbers_punctuation | 2.791 | 0.284 | 4100.0 | 5 |
| q4-metal-distill-codec | questions_contractions | 2.088 | 0.270 | 4100.0 | 5 |
| q4-metal-mps-codec | short | 0.984 | 0.327 | 3101.5 | 5 |
| q4-metal-mps-codec | medium | 2.079 | 0.266 | 3101.5 | 5 |
| q4-metal-mps-codec | long | 3.686 | 0.253 | 3101.5 | 5 |
| q4-metal-mps-codec | numbers_punctuation | 1.694 | 0.283 | 3101.5 | 5 |
| q4-metal-mps-codec | questions_contractions | 1.960 | 0.268 | 3101.5 | 5 |
| q4-metal-onnx-int8 | short | 0.972 | 0.331 | 2223.2 | 5 |
| q4-metal-onnx-int8 | medium | 2.233 | 0.282 | 2223.2 | 5 |
| q4-metal-onnx-int8 | long | 4.126 | 0.284 | 2223.2 | 5 |
| q4-metal-onnx-int8 | numbers_punctuation | 1.673 | 0.281 | 2223.2 | 5 |
| q4-metal-onnx-int8 | questions_contractions | 2.077 | 0.285 | 2223.2 | 5 |
| q8-cpu | short | 20.524 | 7.780 | 6045.7 | 5 |
| q8-cpu | medium | 19.350 | 2.158 | 6045.7 | 5 |
| q8-cpu | long | 24.293 | 1.751 | 6045.7 | 5 |
| q8-cpu | numbers_punctuation | 22.597 | 2.397 | 6045.7 | 5 |
| q8-cpu | questions_contractions | 18.870 | 2.521 | 6045.7 | 5 |
| q8-metal | short | 1.207 | 0.362 | 5161.6 | 5 |
| q8-metal | medium | 2.678 | 0.287 | 5161.6 | 5 |
| q8-metal | long | 4.200 | 0.286 | 5161.6 | 5 |
| q8-metal | numbers_punctuation | 2.767 | 0.285 | 5161.6 | 5 |
| q8-metal | questions_contractions | 2.515 | 0.301 | 5161.6 | 5 |
| q8-metal-distill-codec | short | 1.003 | 0.378 | 4275.4 | 5 |
| q8-metal-distill-codec | medium | 2.401 | 0.295 | 4275.4 | 5 |
| q8-metal-distill-codec | long | 6.107 | 0.285 | 4275.4 | 5 |
| q8-metal-distill-codec | numbers_punctuation | 2.455 | 0.288 | 4275.4 | 5 |
| q8-metal-distill-codec | questions_contractions | 2.195 | 0.291 | 4275.4 | 5 |
| q8-metal-onnx-int8 | short | 0.968 | 0.353 | 2316.9 | 5 |
| q8-metal-onnx-int8 | medium | 2.552 | 0.291 | 2316.9 | 5 |
| q8-metal-onnx-int8 | long | 4.441 | 0.296 | 2316.9 | 5 |
| q8-metal-onnx-int8 | numbers_punctuation | 2.859 | 0.292 | 2316.9 | 5 |
| q8-metal-onnx-int8 | questions_contractions | 2.250 | 0.298 | 2316.9 | 5 |
| torch-cpu | short | 5.490 | 2.553 | 5694.3 | 5 |
| torch-cpu | medium | 13.020 | 1.575 | 5694.3 | 5 |
| torch-cpu | long | 21.664 | 1.430 | 5694.3 | 5 |
| torch-cpu | numbers_punctuation | 14.977 | 1.460 | 5694.3 | 5 |
| torch-cpu | questions_contractions | 11.792 | 1.543 | 5694.3 | 5 |
| torch-mps | short | 2.523 | 0.793 | 5839.7 | 5 |
| torch-mps | medium | 6.231 | 0.748 | 5839.7 | 5 |
| torch-mps | long | 13.677 | 0.789 | 5839.7 | 5 |
| torch-mps | numbers_punctuation | 7.631 | 0.751 | 5839.7 | 5 |
| torch-mps | questions_contractions | 5.963 | 0.770 | 5839.7 | 5 |
