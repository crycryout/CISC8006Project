"""Use the pinned official raw-K patch, with explicit per-layer verification."""
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"third_party/streaming-llm"))


def apply_position_policy(model,policy):
    from transformers.models.gpt_neox.modeling_gpt_neox import GPTNeoXAttention
    from streaming_llm.pos_shift.modify_gpt_neox import enable_gpt_neox_pos_shift_attention, gpt_neox_pos_shift_attention_forward
    layers=[module for module in model.modules() if isinstance(module,GPTNeoXAttention)]
    if len(layers)!=model.config.num_hidden_layers: raise ValueError("unexpected attention layer topology")
    if policy=="cache_relative":
        enable_gpt_neox_pos_shift_attention(model)
        if any(module.forward.__func__ is not gpt_neox_pos_shift_attention_forward for module in layers): raise ValueError("position patch did not cover every layer")
    elif policy!="legacy_implicit": raise ValueError(f"unknown position policy: {policy}")
    return len(layers)
