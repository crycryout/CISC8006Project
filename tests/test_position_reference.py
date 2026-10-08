"""Independent trigonometric RoPE / softmax attention on frozen layer inputs."""
import copy
import math
import types
import pytest
import torch
from transformers import GPTNeoXConfig, GPTNeoXForCausalLM
from src.position_policy import apply_position_policy
from src.cache_policy import RetentionPolicy, choose_h1, choose_h2

torch.set_num_threads(1)


def rotate(x,positions,ndims,base):
    # Do not call upstream rotate_half, rotary_emb or pos-shift helpers.
    freq=base**(-torch.arange(0,ndims,2,device=x.device,dtype=torch.float32)/ndims)
    angles=positions.float()[:,None]*freq[None,:]
    angles=torch.cat([angles,angles],dim=-1)[None,None,:,:]
    cos,sin=angles.cos().to(x.dtype),angles.sin().to(x.dtype)
    first,second=x[...,:ndims//2],x[...,ndims//2:ndims]
    rotated=x[...,:ndims]*cos+torch.cat([-second,first],dim=-1)*sin
    return torch.cat([rotated,x[...,ndims:]],dim=-1)


def reference_forward(self,hidden_states,attention_mask,position_ids,head_mask=None,layer_past=None,use_cache=False,output_attentions=False):
    qkv=self.query_key_value(hidden_states).reshape(hidden_states.shape[0],hidden_states.shape[1],self.num_attention_heads,3*self.head_size)
    q,k,v=[qkv[...,j*self.head_size:(j+1)*self.head_size].permute(0,2,1,3) for j in range(3)]
    if layer_past is not None:
        k=torch.cat([layer_past[0],k],dim=2); v=torch.cat([layer_past[1],v],dim=2)
    present=(k,v) if use_cache else None
    q=rotate(q,position_ids[0],self.rotary_ndims,self.rotary_emb.base)
    rotated_k=rotate(k,torch.arange(k.shape[2],device=k.device),self.rotary_ndims,self.rotary_emb.base)
    scores=torch.matmul(q,rotated_k.transpose(-1,-2))/math.sqrt(self.head_size)
    if attention_mask is not None: scores=scores+attention_mask
    probabilities=scores.float().softmax(dim=-1).to(v.dtype)
    attended=torch.matmul(probabilities,v).permute(0,2,1,3).reshape(hidden_states.shape[0],hidden_states.shape[1],-1)
    out=(self.dense(attended),present)
    return out+(probabilities,) if output_attentions else out


def tiny():
    torch.manual_seed(17)
    return GPTNeoXForCausalLM(GPTNeoXConfig(vocab_size=41,hidden_size=32,num_hidden_layers=3,num_attention_heads=4,intermediate_size=64,max_position_embeddings=64,rotary_pct=0.5,hidden_dropout=0,attention_dropout=0)).eval()


@pytest.mark.parametrize("method,sink",[("window",0),("streaming",2),("h2_sink_selection",2)])
def test_logits_raw_keys_values_and_positions(method,sink):
    model=tiny(); reference=copy.deepcopy(model)
    apply_position_policy(model,"cache_relative")
    for layer in reference.gpt_neox.layers:
        layer.attention.forward=types.MethodType(reference_forward,layer.attention)
    actual_policy=RetentionPolicy(method,sink,budget=8,start=1,end=4)
    ref_policy=RetentionPolicy(method,sink,budget=8,start=1,end=4)
    if method=="h2_sink_selection": actual_policy.anchors=ref_policy.anchors=[0,5]
    past=None; refpast=None
    with torch.no_grad():
        for step in range(28):
            x=torch.tensor([[step%41]])
            out=model(x,past_key_values=past,use_cache=True,output_attentions=True)
            ref=reference(x,past_key_values=refpast,use_cache=True,output_attentions=True)
            torch.testing.assert_close(out.logits,ref.logits,rtol=1e-5,atol=1e-6)
            for (k,v),(rk,rv),a,ra in zip(out.past_key_values,ref.past_key_values,out.attentions,ref.attentions):
                torch.testing.assert_close(k,rk,rtol=1e-5,atol=1e-6)
                torch.testing.assert_close(v,rv,rtol=1e-5,atol=1e-6)
                torch.testing.assert_close(a,ra,rtol=1e-5,atol=1e-6)
            past=actual_policy.evict(out.past_key_values,step); refpast=ref_policy.evict(ref.past_key_values,step)
            assert actual_policy.ids==ref_policy.ids
            for k,v in past: assert k.shape[2]==v.shape[2]==min(step+1,8)


def test_preoverflow_vanilla_patch_and_reset():
    vanilla=tiny(); patched=copy.deepcopy(vanilla); apply_position_policy(patched,"cache_relative")
    a=b=None
    with torch.no_grad():
        for step in range(8):
            x=torch.tensor([[step]])
            va=vanilla(x,past_key_values=a,use_cache=True); pb=patched(x,past_key_values=b,use_cache=True)
            torch.testing.assert_close(va.logits,pb.logits,atol=1e-6,rtol=1e-5)
            a,b=va.past_key_values,pb.past_key_values
        fresh=patched(torch.tensor([[3]]),past_key_values=None,use_cache=True)
        independent=copy.deepcopy(patched)(torch.tensor([[3]]),past_key_values=None,use_cache=True)
        torch.testing.assert_close(fresh.logits,independent.logits,atol=0,rtol=0)


@pytest.mark.parametrize("method,sink,anchors",[("window",0,[]),("streaming",2,[0,1]),("h2_sink_selection",2,[0,5])])
def test_all_layer_kv_tags(method,sink,anchors):
    policy=RetentionPolicy(method,sink,budget=8,start=1,end=4); policy.anchors=anchors
    past=None
    for step in range(29):
        tag=torch.tensor([[[[float(step)]]]])
        past=tuple((torch.cat([k,tag],2),torch.cat([v,-tag-100*layer],2)) for layer,(k,v) in enumerate(past)) if past else tuple((tag.clone(),-tag-100*layer) for layer in range(3))
        past=policy.evict(past,step)
        expected=list(range(step+1)) if step<8 else sorted(anchors+[i for i in range(step+1) if i not in anchors][-(8-len(anchors)):])
        assert policy.ids==expected
        for layer,(k,v) in enumerate(past):
            assert k.flatten().tolist()==expected
            assert v.flatten().tolist()==[-i-100*layer for i in expected]


def test_selection_tie_fallback_and_causality():
    assert choose_h1([1]+[0]*7)==(1,False)
    assert choose_h1([0]*8)==(4,True)
    assert choose_h2([1]*64)==[0,1,2,3]
    scores=[0.0]*64; scores[12]=4; scores[5]=3; scores[19]=2
    assert choose_h2(scores)==[0,5,12,19]
    policy=RetentionPolicy("h1_adaptive_sink",4,start=64,end=512)
    assert not policy.needs_attention(63) and policy.needs_attention(64) and policy.needs_attention(511) and not policy.needs_attention(512)


@pytest.mark.skipif(not torch.cuda.is_available(),reason="H800 regression requires prepared GPU environment")
@pytest.mark.parametrize("dtype,atol,rtol",[(torch.float16,1e-3,5e-3),(torch.bfloat16,4e-3,2e-2)])
def test_gpu_precision_reference(dtype,atol,rtol):
    model=tiny().cuda().to(dtype); reference=copy.deepcopy(model); apply_position_policy(model,"cache_relative")
    for layer in reference.gpt_neox.layers: layer.attention.forward=types.MethodType(reference_forward,layer.attention)
    pa=RetentionPolicy("streaming",2,budget=8,start=1,end=4); pb=RetentionPolicy("streaming",2,budget=8,start=1,end=4)
    a=b=None
    with torch.no_grad():
        for step in range(28):
            x=torch.tensor([[step%41]],device="cuda")
            out=model(x,past_key_values=a,use_cache=True); ref=reference(x,past_key_values=b,use_cache=True)
            torch.testing.assert_close(out.logits,ref.logits,atol=atol,rtol=rtol)
            for (k,v),(rk,rv) in zip(out.past_key_values,ref.past_key_values):
                torch.testing.assert_close(k,rk,atol=atol,rtol=rtol); torch.testing.assert_close(v,rv,atol=atol,rtol=rtol)
            a=pa.evict(out.past_key_values,step); b=pb.evict(ref.past_key_values,step)
