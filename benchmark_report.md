# NeuTTS-Nano performance benchmark

## Method

The 11 configurations vary the backbone among Q4 GGUF, Q8 GGUF, and the standard Torch model, then pair each with the standard decoder. CPU configurations run both stages on CPU; MPS configurations run the backbone on MPS and the decoder on CPU. Additional Q4/Q8 MPS runs compare the distilled and ONNX INT8 decoders, and one Q4 run places both backbone and standard decoder on MPS. Each configuration runs five prompts covering short, medium, and long text, numbers and punctuation, and questions and contractions.

The benchmark runs sequentially on the M3 Pro. For each prompt and configuration it performs one warmup, then five measured runs; medians are calculated from measured runs, excluding warmups. This reduces cold-start effects and yields 25 measured runs per configuration. Recorded metrics include latency, P90 latency, real-time factor (RTF), model load and voice preparation time, backbone and decoder stage times, token throughput, generated audio duration, and peak process RSS.

## Findings

The Q4 and Q8 ONNX INT8 codec configurations used an MPS backbone and a CPU ONNX decoder. They had the lowest measured process RSS: **2.2 GB** for Q4 and **2.3 GB** for Q8. Their median RTFs were **0.284** and **0.296**, respectively. Both were faster than real time, but they were not the fastest configurations: Q4 with both the backbone and codec on MPS had the lowest median RTF (**0.268**) and pooled P90 latency (**3.67 s**). The Q4 ONNX configuration's pooled P90 latency was **4.09 s**.

CPU RTFs were higher than 1.0: **2.37** for Q4 GGUF, **2.40** for Q8 GGUF, and **1.54** for the Torch CPU configuration. These runs did not generate audio faster than playback on median.

## Scope

All configurations use the same prompts, reference voice, sampling settings, and repeat counts. Overall P90 pools runs across prompts of different lengths, so per-prompt P90 values in `performance_comparison.md` are more appropriate for direct latency comparisons. RSS is process memory sampled during a run; it does not include every shared Metal or unified-memory allocation.
