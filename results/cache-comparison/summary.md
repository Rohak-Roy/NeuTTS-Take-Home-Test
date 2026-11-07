# Prompt caching comparison

The Q4 MPS configuration was run in four modes over the same five prompts, with one warmup and five measured runs per prompt (25 measured runs per mode). KV reuse applies only to llama.cpp's exact shared prompt prefix; phoneme caching uses a bounded per-model LRU cache keyed by exact input text.

| Mode | Median TTFT | P90 TTFT | Median wall time | Median RTF | Phoneme cache hits |
|---|---:|---:|---:|---:|---:|
| Both caches off | 298.8 ms | 324.8 ms | 1.961 s | 0.275 | 0 / 60 |
| KV cache only | 201.3 ms | 275.7 ms | 2.403 s | 0.287 | 0 / 60 |
| Phoneme cache only | 301.3 ms | 322.9 ms | 1.962 s | 0.277 | 54 / 60 |
| Both caches on | 202.2 ms | 299.4 ms | 2.528 s | 0.314 | 54 / 60 |

KV reuse lowered median TTFT by about **33%** in this run. Phoneme memoization recorded 54 cache hits but did not measurably reduce end-to-end latency, indicating that phonemization is a small portion of this workload.

The cached and uncached runs produced different speech-token counts despite using the same seed (median 388 with KV reuse versus 359 without). That makes total wall time and RTF an imperfect comparison and means output equivalence still needs a quality check. The current benchmark's TTFT metric is time from `tts.infer()` entry to the first llama.cpp token; it excludes one-time model load and reference preparation.
