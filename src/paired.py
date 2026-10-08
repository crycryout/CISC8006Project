"""Fail-closed pairing; model repeats never become independent books."""
import math
import hashlib
import numpy as np
from src.io_utils import object_hash
from src.metrics import aggregate, bootstrap, scored_count
from src.approvals import single_pass_allowed


def validate_result(r,manifest,split="test",formal=True):
    if r.get("schema_version")!=2 or r.get("status")!="completed" or r.get("validation_status")!="valid": raise ValueError("not completed/valid schema v2")
    c=r.get("contract",{})
    required={"model","model_revision","tokenizer_revision","assets_manifest_sha256","precision","scorer_precision","position_policy","cache_budget","min_scored_idx","max_tokens_per_book","add_special_tokens","eviction","environment_id","numerical_source_sha256","protocol_id","seed","split","determinism"}
    if required-set(c) or r.get("contract_sha256")!=object_hash(c): raise ValueError("incomplete or corrupted contract")
    books=r.get("per_book",[]); ids=[b["book_id"] for b in books]
    if not ids or len(ids)!=len(set(ids)) or r.get("book_ids")!=ids: raise ValueError("empty/duplicate/inconsistent books")
    expected_rows=manifest[split+"_books"]; expected={b["book_id"]:b for b in expected_rows}
    if formal and ids!=[b["book_id"] for b in expected_rows]: raise ValueError("missing/extra/reordered frozen books")
    if set(ids)-set(expected): raise ValueError("books outside manifest")
    if any(c[k]!=manifest[k] for k in ("model","model_revision","tokenizer_revision")): raise ValueError("wrong model/tokenizer revision")
    if c["split"]!=split or c["cache_budget"]!=1024 or c["min_scored_idx"]!=1025 or c["add_special_tokens"] is not True or c["eviction"]!="after_forward": raise ValueError("wrong split/budget/mask/tokenization/eviction")
    if formal and (c["position_policy"]!="cache_relative" or c["scorer_precision"]!="fp32" or c["precision"]!="fp16"): raise ValueError("formal numerical mismatch")
    for b in books:
        exp=expected[b["book_id"]]; length=min(exp["full_token_length"],c["max_tokens_per_book"])
        if b["text_sha256"]!=exp["text_sha256"] or b["input_tokens"]!=length or b["scored_tokens"]!=scored_count(length) or b["scored_tokens"]<=0: raise ValueError("text/length/scored mask mismatch")
        if not b.get("token_ids_sha256") or not b.get("scored_mask_sha256"): raise ValueError("missing token/mask digest")
        mask=np.arange(length-1)>=1025
        if b["scored_mask_sha256"]!=hashlib.sha256(mask.tobytes()).hexdigest(): raise ValueError("wrong scored mask digest")
        if formal and (c["max_tokens_per_book"]!=exp["token_cap"] or b["token_ids_sha256"]!=exp["token_ids_sha256"]): raise ValueError("wrong frozen token cap/hash")
        if any(not isinstance(b[k],(int,float)) or not math.isfinite(b[k]) for k in ("mean_nll_scored","sum_nll_scored","ppl_scored")): raise ValueError("nonfinite/nonnumeric metric")
        if b["mean_nll_scored"]<0 or not math.isclose(b["sum_nll_scored"],b["mean_nll_scored"]*b["scored_tokens"],rel_tol=1e-9,abs_tol=1e-8): raise ValueError("inconsistent NLL sum/mean")
        if not math.isclose(b["ppl_scored"],math.exp(b["mean_nll_scored"]),rel_tol=1e-9): raise ValueError("PPL inconsistency")
    for key,value in aggregate(books).items():
        if key not in r or not math.isclose(r[key],value,rel_tol=1e-9,abs_tol=1e-8): raise ValueError(f"aggregate inconsistency: {key}")
    return {b["book_id"]:b for b in books}


def analyze_pairs(windows,streams,manifest,split="test",formal=True,bootstrap_seed=0,n_boot=10000):
    if len(windows)!=len(streams) or not windows: raise ValueError("unmatched/empty seeds")
    wseed={r["contract"]["seed"]:r for r in windows}; sseed={r["contract"]["seed"]:r for r in streams}
    if len(wseed)!=len(windows) or len(sseed)!=len(streams) or set(wseed)!=set(sseed): raise ValueError("duplicate/missing seed")
    if formal and set(wseed)!={0,1,2}:
        scope="deterministic_selected_improvement" if any(r.get("phase")=="improvement" for r in streams) else "reproduction"
        if set(wseed)!={0} or split!="test" or not single_pass_allowed(scope): raise ValueError("actual model seeds 0,1,2 required; no approved single-pass exemption")
    ids=[r["run_id"] for r in windows+streams]
    if len(set(ids))!=len(ids): raise ValueError("run reused as repeat")
    if len({r.get("method") for r in windows})!=1 or len({r.get("method") for r in streams})!=1: raise ValueError("method changed across seed repeats")
    values={}; provenance=[]; across_seed=None
    for seed in sorted(wseed):
        wr,sr=wseed[seed],sseed[seed]
        w=validate_result(wr,manifest,split,formal); s=validate_result(sr,manifest,split,formal)
        if list(w)!=list(s) or wr["contract"]!=sr["contract"]: raise ValueError("paired contract/book list differs")
        base={k:v for k,v in wr["contract"].items() if k!="seed"}
        if across_seed is not None and across_seed!=base: raise ValueError("non-seed factors changed across repeats")
        across_seed=base
        for book in w:
            if any(w[book][k]!=s[book][k] for k in ("text_sha256","token_ids_sha256","scored_mask_sha256","input_tokens","scored_tokens")): raise ValueError("paired token/mask mismatch")
            values.setdefault(book,[]).append(dict(seed=seed,baseline_nll=w[book]["mean_nll_scored"],candidate_nll=s[book]["mean_nll_scored"],delta=s[book]["mean_nll_scored"]-w[book]["mean_nll_scored"],scored_tokens=w[book]["scored_tokens"]))
        provenance.append(dict(seed=seed,baseline_run=wr["run_id"],candidate_run=sr["run_id"]))
    per_book=[dict(book_id=b,baseline_nll=sum(x["baseline_nll"] for x in rows)/len(rows),candidate_nll=sum(x["candidate_nll"] for x in rows)/len(rows),delta=sum(x["delta"] for x in rows)/len(rows),seed_delta_min=min(x["delta"] for x in rows),seed_delta_max=max(x["delta"] for x in rows),scored_tokens=rows[0]["scored_tokens"]) for b,rows in values.items()]
    out=dict(validation_status="valid",provenance=provenance,per_book=per_book,seed_results=values,uncertainty_unit="book; seed-paired deltas averaged within book before bootstrap")
    out.update(bootstrap([b["delta"] for b in per_book],n_boot,bootstrap_seed) if formal else dict(claim_status=None,purpose="diagnostic only"))
    return out
