import copy
import pytest
import torch
from src.cache_policy import RetentionPolicy
from src.position_policy import apply_position_policy
from tests.test_position_reference import tiny


def test_forced_anchors_degenerate_to_prefix():
    model=tiny(); apply_position_policy(model,"cache_relative")
    prefix=RetentionPolicy("streaming",2,budget=8,start=1,end=4)
    forced=RetentionPolicy("h2_forced_prefix",2,budget=8,start=1,end=4)
    a=b=None
    with torch.no_grad():
        for step in range(28):
            x=torch.tensor([[step%41]])
            first=model(x,past_key_values=a,use_cache=True); second=model(x,past_key_values=b,use_cache=True)
            torch.testing.assert_close(first.logits,second.logits,atol=0,rtol=0)
            a=prefix.evict(first.past_key_values,step); b=forced.evict(second.past_key_values,step)
            for (k,v),(rk,rv) in zip(a,b):
                torch.testing.assert_close(k,rk,atol=0,rtol=0); torch.testing.assert_close(v,rv,atol=0,rtol=0)


def test_calibration_only_preserves_logits_and_no_future_selection():
    model=tiny(); apply_position_policy(model,"cache_relative")
    baseline=RetentionPolicy("streaming",4,budget=128,start=64,end=96)
    control=RetentionPolicy("calibration_control",4,budget=128,start=64,end=96)
    a=b=None
    with torch.no_grad():
        for step in range(150):
            x=torch.tensor([[step%41]])
            first=model(x,past_key_values=a,use_cache=True)
            second=model(x,past_key_values=b,use_cache=True,output_attentions=control.needs_attention(step))
            control.observe(step,second.attentions)
            torch.testing.assert_close(first.logits,second.logits,atol=0,rtol=0)
            a=baseline.evict(first.past_key_values,step); b=control.evict(second.past_key_values,step)
    assert control.anchors==[0,1,2,3] and control.decision_step==95 and control.calibration_queries==32


def test_actual_calibration_mass_and_frozen_decision():
    policy=RetentionPolicy("h1_adaptive_sink",4,budget=1024,start=64,end=66)
    for step in [64,65]:
        weights=torch.zeros(1,2,1,step+1); weights[:,:,:,0]=0.95; weights[:,:,:,-1]=0.05
        policy.observe(step,(weights,weights))
    assert policy.anchors==[0] and policy.decision_step==65
    policy.observe(700,None)
    assert policy.anchors==[0]


def test_random_control_seeds_and_protected_first():
    selections=[]
    for seed in range(3):
        p=RetentionPolicy("random_anchors",4,seed=seed,start=64,end=65)
        p.observe(64,(torch.ones(1,1,1,65)/65,))
        assert 0 in p.anchors and len(set(p.anchors))==4 and p.anchors==sorted(p.anchors)
        selections.append(p.anchors)
    assert len({tuple(x) for x in selections})==3
