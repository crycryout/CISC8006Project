#!/usr/bin/env python3
"""Token-by-token teacher forcing with immutable, verified schema-v2 outputs."""
import json
import math
import os
from pathlib import Path
import random
import signal
import subprocess
import sys
import time
import traceback
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG',':4096:8')
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.config import parse_config
from src.io_utils import file_hash, object_hash, write_json
from src.approvals import require_approval
from src.run_store import RunStore, Tee
from src.hardware import hardware


def prepare_inputs(cfg):
    import numpy as np
    from transformers import AutoTokenizer
    from scripts.prepare_data import token_hash
    manifest=json.loads(Path(cfg['assets_manifest']).read_text())
    if cfg['model']!=manifest['model'] or cfg['model_revision']!=manifest['model_revision']: raise ValueError('model not in verified manifest')
    expected={b['book_id']:b for b in manifest[cfg['manifest_split']+'_books']}
    files=cfg['book_files']
    if cfg['phase'] in {'reproduction','pilot','improvement','ablation'} and [Path(p).stem for p in files]!=list(expected): raise ValueError('scientific phase requires complete frozen book set')
    tokenizer=AutoTokenizer.from_pretrained(cfg['model'],revision=cfg['model_revision'],local_files_only=cfg['offline'])
    data=[]
    for path in files:
        book=expected.get(Path(path).stem)
        if book is None or file_hash(path)!=book['text_sha256']: raise ValueError(f'unknown or altered text: {path}')
        full=tokenizer(Path(path).read_text(encoding='utf-8'),add_special_tokens=True)['input_ids']
        if len(full)!=book['full_token_length']: raise ValueError(f'token length changed: {path}')
        ids=np.asarray(full[:cfg['max_tokens_per_book']],dtype='<i8')
        if len(ids)<=1026: raise ValueError('zero-scored book')
        digest=token_hash(ids)
        if cfg['max_tokens_per_book']==book['token_cap'] and digest!=book['token_ids_sha256']: raise ValueError('frozen token hash changed')
        data.append((book,ids,digest))
    return manifest,data


def run(cfg,store):
    import numpy as np
    import torch
    from transformers import AutoModelForCausalLM
    from src.position_policy import apply_position_policy
    from src.cache_policy import RetentionPolicy
    from src.metrics import aggregate, token_nll
    from scripts.prepare_data import token_hash
    random.seed(cfg['seed']); np.random.seed(cfg['seed']); torch.manual_seed(cfg['seed']); torch.cuda.manual_seed_all(cfg['seed'])
    torch.set_num_threads(1)
    torch.backends.cuda.matmul.allow_tf32=False; torch.backends.cudnn.allow_tf32=False
    torch.backends.cudnn.benchmark=False
    torch.use_deterministic_algorithms(True)
    dtype={'fp16':torch.float16,'bf16':torch.bfloat16,'fp32':torch.float32}[cfg['precision']]
    manifest,data=prepare_inputs(cfg)
    # Rehash weights and tokenizer before the first GPU allocation.
    from huggingface_hub import hf_hub_download
    for name,expected in manifest['model_files'].items():
        p=hf_hub_download(cfg['model'],name,revision=cfg['model_revision'],local_files_only=cfg['offline'])
        if file_hash(p)!=expected['sha256']: raise ValueError(f'model/tokenizer hash mismatch: {name}')
    model=AutoModelForCausalLM.from_pretrained(cfg['model'],revision=cfg['model_revision'],torch_dtype=dtype,local_files_only=cfg['offline']).to(cfg['device']).eval()
    layers=apply_position_policy(model,cfg['position_policy'])
    determinism=dict(enabled=True,tf32=False,cudnn_benchmark=False,torch_threads=1,cublas_workspace=os.environ['CUBLAS_WORKSPACE_CONFIG'],attention_backend='GPTNeoXAttention eager',torch=torch.__version__,transformers=__import__('transformers').__version__,cuda=torch.version.cuda)
    contract=dict(model=cfg['model'],model_revision=cfg['model_revision'],tokenizer_revision=manifest['tokenizer_revision'],assets_manifest_sha256=file_hash(cfg['assets_manifest']),precision=cfg['precision'],scorer_precision=cfg['scorer_precision'],position_policy=cfg['position_policy'],cache_budget=1024,min_scored_idx=1025,max_tokens_per_book=cfg['max_tokens_per_book'],add_special_tokens=True,eviction='after_forward',environment_id=cfg['environment_id'],numerical_source_sha256=store.row['numerical_source_sha256'],protocol_id=cfg['protocol_id'],seed=cfg['seed'],split=cfg['manifest_split'],determinism=determinism)
    contract['hardware_class']={key:store.row['hardware'].get(key) for key in ('name','memory_total_bytes','multiprocessor_count','compute_capability')}
    contract['calibration_protocol']=dict(start=cfg['calibration_start'],end=cfg['calibration_end'],selection_threshold=cfg['selection_threshold'])
    per_book=[]
    if cfg['device']=='cuda': torch.cuda.reset_peak_memory_stats()
    evaluation_t0=time.perf_counter()
    for book,ids,digest in data:
        if cfg['inject_failure_after_book'] is not None and len(per_book)==cfg['inject_failure_after_book']: raise RuntimeError('injected failure for recovery verification')
        book_t0=time.perf_counter(); calibration_seconds=0.0
        tensor=torch.tensor(ids,device=cfg['device']).unsqueeze(0)
        losses=torch.empty(len(ids)-1,device=cfg['device'],dtype=torch.float32)
        policy=RetentionPolicy(cfg['method'],cfg['sink_tokens'],1024,cfg['seed'],cfg['calibration_start'],cfg['calibration_end'],cfg['selection_threshold'])
        past=None; traces=[]; max_forward=0; max_retained=0; max_kv=0
        with torch.no_grad():
            for step in range(len(ids)-1):
                if time.perf_counter()-store.t0>cfg['max_gpu_seconds']: raise TimeoutError('run time reservation exhausted')
                collect=policy.needs_attention(step); ct=time.perf_counter()
                out=model(tensor[:,step:step+1],past_key_values=past,use_cache=True,output_attentions=collect)
                losses[step]=token_nll(out.logits.reshape(1,-1),tensor[:,step+1],cfg['scorer_precision'])[0]
                if collect:
                    policy.observe(step,out.attentions); calibration_seconds+=time.perf_counter()-ct
                forward=out.past_key_values[0][0].shape[2]; max_forward=max(max_forward,forward)
                past=policy.evict(out.past_key_values,step)
                retained=past[0][0].shape[2]; kv=sum(k.numel()*k.element_size()+v.numel()*v.element_size() for k,v in past)
                max_retained=max(max_retained,retained); max_kv=max(max_kv,kv)
                if step%128==0 or step in {1023,1024,1025,len(ids)-2}: traces.append(dict(step=step,forward_length=forward,retained_length=retained,kv_bytes=kv))
                if step%2048==0: print(json.dumps(dict(run_id=cfg['run_id'],book=book['book_id'],step=step)),flush=True)
        if cfg['device']=='cuda': torch.cuda.synchronize()
        nll=losses.cpu().numpy(); mask=np.arange(len(nll))>=1025; scored=nll[mask].astype(np.float64)
        if not np.isfinite(nll).all(): raise ValueError('nonfinite raw NLL')
        nll_sum=float(scored.sum()); mean=nll_sum/len(scored)
        row=dict(book_id=book['book_id'],input_tokens=len(ids),tokenized_length=len(ids),scored_tokens=len(scored),text_sha256=book['text_sha256'],token_ids_sha256=digest,scored_mask_sha256=__import__('hashlib').sha256(mask.tobytes()).hexdigest(),sum_nll_scored=nll_sum,mean_nll_scored=mean,ppl_scored=math.exp(mean),mean_nll_all_positions=float(nll.astype(np.float64).mean()),runtime_seconds=time.perf_counter()-book_t0,calibration_seconds=calibration_seconds,selection=policy.summary(),max_forward_length=max_forward,max_retained_length=max_retained,max_kv_bytes=max_kv,attention_layers=layers,cache_trace=traces)
        directory=store.directory/'books'/book['book_id']; directory.mkdir(parents=True,exist_ok=False)
        np.savez_compressed(directory/'position_nll.npz',nll=nll,input_ids=ids,scored_mask=mask)
        write_json(directory/'metrics.json',row); per_book.append(row)
        write_json(store.directory/'progress.json',dict(status='running',completed_books=[b['book_id'] for b in per_book]))
        print(json.dumps(dict(book=book['book_id'],nll=mean,scored=len(scored))),flush=True)
    elapsed=time.perf_counter()-evaluation_t0
    result=dict(schema_version=2,run_id=cfg['run_id'],status='completed',validation_status='valid',phase=cfg['phase'],method=cfg['method'],git_commit=store.row['git_commit'],device_uuid=store.row['gpu_uuid'],contract=contract,contract_sha256=object_hash(contract),book_ids=[b['book_id'] for b in per_book],per_book=per_book,**aggregate(per_book),elapsed_seconds=elapsed,predictions_per_second=sum(b['input_tokens']-1 for b in per_book)/elapsed,peak_gpu_memory_mb=torch.cuda.max_memory_allocated()/1024**2 if cfg['device']=='cuda' else None,claim_status=None)
    write_json(store.directory/'result.json',result)
    print(json.dumps({k:result[k] for k in ('run_id','macro_book_nll','micro_token_nll','scored_tokens','elapsed_seconds','predictions_per_second')},indent=2))


def main():
    cfg=parse_config(); require_approval(cfg['phase'],cfg['method'])
    store=RunStore(cfg,hardware(cfg['device']))
    original_out,original_err=sys.stdout,sys.stderr
    sys.stdout=Tee(original_out,store.directory/'stdout.log'); sys.stderr=Tee(original_err,store.directory/'stderr.log')
    def timeout(*_): raise TimeoutError('external termination / hard budget timeout')
    signal.signal(signal.SIGTERM,timeout)
    signal.signal(signal.SIGALRM,timeout); signal.alarm(cfg['max_gpu_seconds'])
    code=0; error=None
    try: run(cfg,store)
    except BaseException as exc:
        code=1; error=f'{type(exc).__name__}: {exc}'; traceback.print_exc()
        write_json(store.directory/'failure.json',dict(validation_status='invalid',error=error,claim_status=None))
    finally:
        signal.alarm(0); sys.stdout.flush(); sys.stderr.flush()
        sys.stdout.stream.close(); sys.stderr.stream.close(); sys.stdout,sys.stderr=original_out,original_err
        row=store.finish(code,error)
        print(json.dumps(dict(run_id=cfg['run_id'],status=row['status'],gpu_hours=row['gpu_hours'])))
    return code


if __name__=='__main__': sys.exit(main())
