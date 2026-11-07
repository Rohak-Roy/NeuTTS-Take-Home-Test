# NeuTTS-Nano performance benchmark

## Setup

Use Python 3.13 and Xcode Command Line Tools on Apple silicon. Core NeuTTS dependencies are declared in `upstream/pyproject.toml`.

```bash
python3.13 -m venv .venv-accelerate
source .venv-accelerate/bin/activate
python -m pip install -e ./upstream
CMAKE_ARGS="-DGGML_ACCELERATE=ON -DGGML_METAL=OFF" \
  python -m pip install --no-cache-dir --no-binary llama-cpp-python llama-cpp-python
deactivate

python3.13 -m venv .venv-metal
source .venv-metal/bin/activate
python -m pip install -e ./upstream
CMAKE_ARGS="-DGGML_METAL=ON" \
  python -m pip install --no-cache-dir --no-binary llama-cpp-python llama-cpp-python
python -m pip install onnxruntime  # Needed by the ONNX INT8 decoder configs.
deactivate
```

The runner selects `.venv-accelerate` when both backbone and decoder use CPU; all other configs use `.venv-metal`. The build flags follow the [llama.cpp Accelerate](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md#accelerate-framework) and [llama-cpp-python Metal](https://github.com/abetlen/llama-cpp-python#metal) build instructions.

Model files must be present in `models/huggingface/hub`; the benchmark runs offline and needs no Hugging Face token. The runtime cache should contain these model entries:

| Hugging Face model ID | Purpose / configs |
|---|---|
| `neuphonic/neutts-nano-q4-gguf` | Q4 GGUF backbone configs |
| `neuphonic/neutts-nano-q8-gguf` | Q8 GGUF backbone configs |
| `neuphonic/neutts-nano` | Standard Torch backbone configs |
| `neuphonic/neucodec` | Standard reference encoder and audio decoder |
| `neuphonic/distill-neucodec` | Distilled decoder configs; also needs `ntu-spml/distilhubert` |
| `neuphonic/neucodec-onnx-decoder-int8` | ONNX INT8 decoder configs |
| `facebook/w2v-bert-2.0` | Semantic encoder used by standard NeuCodec |
| `ntu-spml/distilhubert` | Semantic encoder used by distilled NeuCodec |

These are Hugging Face cache entries under `models/huggingface/hub/models--<org>--<name>/`. The pre-encoded-reference and ONNX INT8 configs also use `upstream/samples/jo.pt`; other configs encode `upstream/samples/jo.wav` using `jo.txt`. All configs use `prompts.json`.

Run from a host macOS terminal so MPS can access Metal:

```bash
./performance_benchmark.sh
```

The script runs configs sequentially and writes `results.json` plus per-config logs, WAVs, and reports under `results/performance-benchmark/`. `REPEATS` and `WARMUP_RUNS` can override config defaults. `CONFIG_NAMES="q4-metal q4-metal-preencoded-reference"` runs only selected configs.

## Results and optimizations

- In the initial 11-config sweep, CPU median RTF ranged from **1.54–2.40**. Q4 with both backbone and decoder on MPS had the lowest median RTF (**0.268**). Q4/Q8 MPS with ONNX INT8 had the lowest process RSS (**2.2/2.3 GB**), with median RTF **0.284/0.296**.
- Pre-encoded reference tokens reduced reference preparation from **12.052 s** to about **0.001 s**. Generation-only median TTFT was nearly unchanged (**305.7 ms vs. 303.8 ms**); estimated cold-start to first token fell from **25.33 s** to **12.89 s**.
- KV-prefix reuse lowered median TTFT from **299 ms** to **201 ms** in the Q4 MPS test. Phonemization caching hit **54 of 60** repeated conversions but had no measurable end-to-end speedup. KV-cached runs produced different speech-token counts under the same seed, so their full-generation RTF comparison is inconclusive; audio quality was not evaluated.

Detailed reports: `performance_comparison.md`, `benchmark_report.md`, `results/ttft-comparison/summary.md`, and `results/cache-comparison/summary.md`.
