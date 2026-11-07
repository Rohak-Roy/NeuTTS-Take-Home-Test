"""Unit tests for prompt cache controls and phonemization memoization."""
from collections import OrderedDict
from typing import Any

import pytest

from neutts import NeuTTS


class CountingPhonemizer:
    """Small test double that records phonemizer calls."""

    def __init__(self) -> None:
        self.calls = 0

    def phonemize(self, texts: list[str]) -> list[str]:
        self.calls += 1
        return [f"phones for {text}" for text in texts]


class FakeBackbone:
    """Minimal GGUF-like backbone for testing reset behavior."""

    def __init__(self) -> None:
        self.reset_calls = 0

    def reset(self) -> None:
        self.reset_calls += 1

    def __call__(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        if kwargs.get("stream"):
            return iter([])  # type: ignore[return-value]
        return {"choices": [{"text": "<|speech_1|>"}]}


def make_model_for_phoneme_test(enabled: bool) -> tuple[NeuTTS, CountingPhonemizer]:
    """Create an uninitialized NeuTTS instance with only phonemizer state set."""
    model = NeuTTS.__new__(NeuTTS)
    phonemizer = CountingPhonemizer()
    model.phonemizer = phonemizer
    model.cache_phonemes = enabled
    model._phoneme_cache = OrderedDict()
    model._phoneme_cache_maxsize = 2
    model._phonemization_cache_hits = 0
    model._phonemization_cache_misses = 0
    return model, phonemizer


def test_phonemization_cache_reuses_exact_text() -> None:
    """Repeated identical text is phonemized once when caching is enabled."""
    model, phonemizer = make_model_for_phoneme_test(enabled=True)

    assert model._to_phones("hello") == "phones for hello"
    assert model._to_phones("hello") == "phones for hello"

    assert phonemizer.calls == 1
    assert model.phonemization_cache_info() == {
        "enabled": True,
        "hits": 1,
        "misses": 1,
        "entries": 1,
    }


def test_phonemization_cache_can_be_disabled() -> None:
    """Disabled caching recomputes the same text on each call."""
    model, phonemizer = make_model_for_phoneme_test(enabled=False)

    model._to_phones("hello")
    model._to_phones("hello")

    assert phonemizer.calls == 2
    assert model.phonemization_cache_info()["entries"] == 0


@pytest.mark.parametrize(("cache_kv", "expected_resets"), [(True, 0), (False, 1)])
def test_gguf_cache_option_controls_full_reset(cache_kv: bool, expected_resets: int) -> None:
    """GGUF inference preserves context for prefix reuse only when enabled."""
    model = NeuTTS.__new__(NeuTTS)
    model.cache_kv = cache_kv
    model.backbone = FakeBackbone()
    model.max_context = 32
    model._ggml_prompt = lambda *args, **kwargs: "prompt"  # type: ignore[method-assign]
    model._call_seed = lambda: 123  # type: ignore[method-assign]

    model._infer_ggml(ref_codes=[], ref_text="reference", input_text="request")

    assert model.backbone.reset_calls == expected_resets


@pytest.mark.parametrize(("cache_kv", "expected_resets"), [(True, 0), (False, 1)])
def test_streaming_gguf_cache_option_controls_full_reset(
    cache_kv: bool, expected_resets: int
) -> None:
    """Streaming GGUF inference follows the same cache reset setting."""
    model = NeuTTS.__new__(NeuTTS)
    model.cache_kv = cache_kv
    model.backbone = FakeBackbone()
    model.max_context = 32
    model._ggml_prompt = lambda *args, **kwargs: "prompt"  # type: ignore[method-assign]
    model._call_seed = lambda: 123  # type: ignore[method-assign]

    list(model._infer_stream_ggml(ref_codes=[], ref_text="reference", input_text="request"))

    assert model.backbone.reset_calls == expected_resets
