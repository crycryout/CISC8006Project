#!/usr/bin/env python3
"""Measure preset-tolerance GPU oracle errors on the independent tiny-model fixture."""
import copy
import json
import os
from pathlib import Path
import sys
import types
import uuid
import numpy as np
import torch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.cache_policy import RetentionPolicy
from src.config import DEFAULTS
from src.hardware import hardware as get_hardware,active_pids
from src.io_utils import write_json,file_hash
from src.position_policy import apply_position_policy
from src.run_store import RunStore
from tests.test_position_reference import tiny,reference_forward


def measure(dtype,atol,rtol,method,sink,anchors):
    model=tiny().cuda().to(dtype); reference=copy.deepcopy(model)
    apply_position_policy(model,"cache_relative")
    for layer in reference.gpt_neox.layers:
        layer.attention.forward=types.MethodType(reference_forward,layer.attention)
    policies=[RetentionPolicy(method,sink,budget=8,start=1,end=4) for _ in range(2)]
    for policy in policies: policy.anchors=anchors
    past=[None,None]; errors={name:[] for name in ("logits","K","V","attention")}
    with torch.no_grad():
        for step in range(28):
            token=torch.tensor([[step%41]],device="cuda")
            actual=model(token,past_key_values=past[0],use_cache=True,output_attentions=True)
            expected=reference(token,past_key_values=past[1],use_cache=True,output_attentions=True)
            pairs=[("logits",actual.logits,expected.logits)]
            for (k,v),(rk,rv),attention,reference_attention in zip(actual.past_key_values,expected.past_key_values,actual.attentions,expected.attentions):
                pairs.extend([("K",k,rk),("V",v,rv),("attention",attention,reference_attention)])
            for name,value,ref in pairs:
                torch.testing.assert_close(value,ref,atol=atol,rtol=rtol)
                errors[name].append((value.float()-ref.float()).abs().cpu().numpy().reshape(-1))
            for index,out in enumerate((actual,expected)):
                past[index]=policies[index].evict(out.past_key_values,step)
    distributions={}
    for name,arrays in errors.items():
        values=np.concatenate(arrays).astype(np.float64)
        distributions[name]=dict(elements=len(values),max_abs=float(values.max()),mean_abs=float(values.mean()),p50_abs=float(np.percentile(values,50)),p95_abs=float(np.percentile(values,95)),p99_abs=float(np.percentile(values,99)))
    return dict(method=method,dtype=str(dtype),preset_atol=atol,preset_rtol=rtol,status="pass",errors=distributions)


def main():
    hardware=get_hardware("cuda")
    if [pid for pid in active_pids(hardware["uuid"]) if pid!=os.getpid()]:
        raise RuntimeError("selected instance is occupied; run after the study finishes")
    rid="reference-errors-h800-"+uuid.uuid4().hex[:12]
    cfg=dict(DEFAULTS,run_id=rid,phase="smoke",device="cuda",max_gpu_seconds=180)
    store=RunStore(cfg,hardware); code=0; error=None
    rows=[]
    try:
        for dtype,atol,rtol in [(torch.float16,1e-3,5e-3),(torch.bfloat16,4e-3,2e-2)]:
            for method,sink,anchors in [("window",0,[]),("streaming",2,[0,1]),("h2_sink_selection",2,[0,5])]:
                rows.append(measure(dtype,atol,rtol,method,sink,anchors))
        write_json(store.directory/"errors.json",dict(status="pass",parameters=dict(weight_seed=17,layers=3,budget=8,steps=28,vocab_size=41),scope="random three-layer GPT-NeoX, budget8,28 sequential steps; not a bound on all full-model outputs",cases=rows))
    except BaseException as exc:
        code=1; error=f"{type(exc).__name__}: {exc}"
        write_json(store.directory/"failure.json",dict(error=error,completed_cases=rows))
    write_json(store.directory/"result.json",dict(run_id=rid,status="completed" if code==0 else "failed",artifact_kind="fixture",purpose="independent tiny-model GPU error distributions with unchanged preset tolerances",claim_status=None))
    receipt=store.finish(code,error)
    if code==0:
        write_json(ROOT/"environment/verification/reference-error-distributions.json",dict(status="pass",run_id=rid,artifact_path=str(store.directory.relative_to(ROOT)),source_commit=receipt["git_commit"],numerical_source_sha256=receipt["numerical_source_sha256"],script_sha256=file_hash(Path(__file__)),reference_fixture_sha256=file_hash(ROOT/"tests/test_position_reference.py"),errors_sha256=file_hash(store.directory/"errors.json"),parameters=dict(weight_seed=17,layers=3,budget=8,steps=28,vocab_size=41),scope="three-layer tiny model; FP16/BF16 window/streaming/selected-anchor references; no full-model global error bound",cases=rows))
    print(json.dumps(dict(run_id=rid,exit_code=code,gpu_hours=receipt["gpu_hours"],error=error)))
    return code


if __name__=="__main__": sys.exit(main())
