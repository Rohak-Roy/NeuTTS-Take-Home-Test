# Q4 MPS pre-encoded reference comparison

## Method

The standard `q4-metal` config was compared with `q4-metal-preencoded-reference`. Both used the same Q4 GGUF MPS backbone, CPU NeuCodec decoder, reference recording and transcript, prompts, and sampling settings. Each of the five prompts received one warmup and five measured runs (25 measured runs per config).

TTFT is measured from the start of `tts.infer()` to llama.cpp yielding its first generated token. It includes prompt construction and prompt prefill, but excludes model loading and reference preparation. Reference preparation is reported separately. “Cold-start to first token” below is an estimate that adds model load time, reference preparation time, and median TTFT.

## Results

| Measurement | Standard reference | Pre-encoded reference |
|---|---:|---:|
| Reference preparation | Encode: 12.052 s | Load codes: 0.001 s |
| Median generation TTFT | 305.7 ms | 303.8 ms |
| P90 generation TTFT | 332.8 ms | 325.3 ms |
| Estimated cold-start to first token | 25.33 s | 12.89 s |
| Peak process RSS | 4,963 MB | 3,168 MB |

## Conclusion

Pre-encoding did not materially reduce generation-only TTFT: the median changed by about **1.8 ms (0.6%)**, which is within run-to-run variation. It reduced the one-time reference preparation by about **12.05 seconds**, lowering estimated cold-start to first token by about **12.44 seconds (49%)**. Peak process RSS was also about **1.8 GB lower** in the pre-encoded run. The main benefit is faster readiness for the first request and lower measured process memory, rather than faster token generation once the reference is prepared.
