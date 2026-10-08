"""Explicit scoring and book/token estimands."""
import math
import numpy as np


def scored_count(tokens,budget=1024):
    return max(tokens-budget-2,0)


def aggregate(books):
    if not books or any(b["scored_tokens"]<=0 or not math.isfinite(b["mean_nll_scored"]) for b in books): raise ValueError("empty/nonfinite/zero-scored book")
    macro=sum(b["mean_nll_scored"] for b in books)/len(books)
    count=sum(b["scored_tokens"] for b in books)
    micro=sum(b["mean_nll_scored"]*b["scored_tokens"] for b in books)/count
    return dict(macro_book_nll=macro,macro_derived_ppl=math.exp(macro),micro_token_nll=micro,micro_token_ppl=math.exp(micro),scored_tokens=count)


def token_nll(logits,labels,precision="fp32"):
    import torch.nn.functional as F
    return F.cross_entropy(logits.float() if precision=="fp32" else logits,labels,reduction="none")


def bootstrap(deltas,n_boot=10000,seed=0):
    arr=np.asarray(deltas,dtype=np.float64)
    if arr.ndim!=1 or not len(arr) or not np.isfinite(arr).all() or n_boot<=0: raise ValueError("invalid bootstrap input")
    rng=np.random.default_rng(seed)
    means=arr[rng.integers(0,len(arr),size=(n_boot,len(arr)))].mean(axis=1)
    lo,hi=np.percentile(means,[2.5,97.5])
    return dict(paired_macro_delta_nll=float(arr.mean()),bootstrap_ci95=[float(lo),float(hi)],claim_status="supported" if hi<0 else "not_supported" if lo>0 else "inconclusive",bootstrap_seed=seed,n_boot=n_boot,n_books=len(arr))
