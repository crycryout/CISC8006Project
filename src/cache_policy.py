"""Causal early-anchor selection; chronological, deduplicated retained K/V."""
import math
import random
import sys
from pathlib import Path
import torch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"third_party/streaming-llm"))
from streaming_llm.kv_cache import StartRecentKVCache


def choose_h1(scores,threshold=0.90):
    mass=sum(scores[:8])
    if not math.isfinite(mass) or mass<=1e-12 or any(not math.isfinite(x) or x<0 for x in scores[:8]): return 4,True
    for k in (1,2,4,8):
        if sum(scores[:k])/mass>=threshold: return k,False
    return 8,False


def choose_h2(scores,protect_first=True):
    if len(scores)<64 or any(not math.isfinite(x) or x<0 for x in scores[:64]): raise ValueError("invalid anchor scores")
    candidates=list(range(1,64)) if protect_first else list(range(64))
    selected=sorted(candidates,key=lambda i:(-scores[i],i))[:3 if protect_first else 4]
    return sorted(([0] if protect_first else [])+selected)


class RetentionPolicy:
    def __init__(self,method,sink=4,budget=1024,seed=0,start=64,end=512,threshold=0.90):
        self.method,self.budget,self.start,self.end,self.threshold=method,budget,start,end,threshold
        self.sink=sink
        self.anchors=list(range(sink)); self.ids=[]
        self.scores=torch.zeros(64,dtype=torch.float64)
        self.calibration_queries=0; self.fallback=False; self.decision_step=None
        self.rng=random.Random(seed)
        self.cache=StartRecentKVCache(sink,budget-sink,k_seq_dim=2,v_seq_dim=2)

    def needs_attention(self,step):
        return self.method in {"h1_adaptive_sink","h2_sink_selection","calibration_control","h2_forced_prefix","h2_no_first","random_anchors"} and self.start<=step<self.end

    def observe(self,step,attentions):
        if not self.needs_attention(step): return
        if attentions is None: raise ValueError("calibration requires actual attention probabilities")
        # Sum over all layers/heads/queries. Common scale cancels in selection.
        for weights in attentions:
            self.scores+=weights[0,:,-1,:64].double().sum(dim=0).cpu()
        self.calibration_queries+=1
        if step==self.end-1:
            if self.method=="h1_adaptive_sink":
                self.sink,self.fallback=choose_h1(self.scores.tolist(),self.threshold)
                self.anchors=list(range(self.sink))
                self.cache=StartRecentKVCache(self.sink,self.budget-self.sink,2,2)
            elif self.method in {"h2_sink_selection","h2_no_first"}:
                self.anchors=choose_h2(self.scores.tolist(),self.method!="h2_no_first")
            elif self.method=="random_anchors":
                self.anchors=sorted([0]+self.rng.sample(range(1,64),3))
            self.decision_step=step

    def evict(self,past,step):
        self.ids.append(step)
        if any(k.shape[2]!=len(self.ids) or v.shape[2]!=len(self.ids) for k,v in past): raise ValueError("layer K/V length mismatch")
        if len(self.ids)>self.budget:
            if self.method in {"h2_sink_selection","h2_no_first","random_anchors","h2_forced_prefix"}:
                anchors=set(self.anchors)
                if not anchors<=set(self.ids): raise ValueError("attempt to revive evicted anchor")
                recent=[i for i in self.ids if i not in anchors][-(self.budget-len(anchors)):]
                kept=sorted(anchors|set(recent))
                offsets={tag:i for i,tag in enumerate(self.ids)}
                indices=torch.tensor([offsets[i] for i in kept],device=past[0][0].device)
                past=tuple((k.index_select(2,indices),v.index_select(2,indices)) for k,v in past)
                self.ids=kept
            else:
                past=self.cache(past)
                self.ids=self.ids[:self.sink]+self.ids[-(self.budget-self.sink):]
        if len(self.ids)>self.budget or len(self.ids)!=len(set(self.ids)) or self.ids!=sorted(self.ids): raise ValueError("retention invariant failed")
        if any(k.shape[2]!=len(self.ids) or v.shape[2]!=len(self.ids) for k,v in past): raise ValueError("post-eviction K/V layer mismatch")
        return past

    def summary(self):
        return dict(anchors=self.anchors,sink_tokens=len(self.anchors),decision_step=self.decision_step,
                    calibration_queries=self.calibration_queries,attention_mass=self.scores.tolist(),fallback=self.fallback)
