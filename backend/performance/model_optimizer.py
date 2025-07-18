"""Model optimisation helpers – quantisation, warm-up, caching."""
from __future__ import annotations

import logging
import time
from functools import lru_cache
from typing import Callable

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

logger = logging.getLogger(__name__)


@lru_cache(maxsize=4)
def load_quantised_model(model_name: str):  # noqa: D401
    """Load *model_name* in 8-bit quantised form to save memory & improve speed."""
    logger.info("Loading quantised model %s", model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name, load_in_8bit=True, device_map="auto")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return model, tokenizer


def warm_up(model, tokenizer: Callable[[str, bool], object], *, prompt: str = "hello", n: int = 3):  # noqa: D401
    """Run quick dummy inference to compile kernels & fill caches."""
    logger.info("Warming up model with %s iterations", n)
    for _ in range(n):
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        _ = model.generate(**inputs, max_new_tokens=8)
    torch.cuda.empty_cache()


# Example usage:
# model, tok = load_quantised_model("google/flan-t5-base")
# warm_up(model, tok)
