import copy
import math
import pytest
import torch
import yaml
from src.config import DEFAULTS, parse_config, validate
from src.io_utils import object_hash
from src.metrics import aggregate, bootstrap, scored_count, token_nll
from src.paired import analyze_pairs, validate_result


def config():
    return dict(DEFAULTS,method="window",sink_tokens=0,recent_tokens=1024,book_files=["a.txt"],max_tokens_per_book=4096)


def test_yaml_cli_precedence(tmp_path):
    path=tmp_path/"cfg.yaml"; cfg=config(); cfg.update(model="CONFIG_MODEL",model_revision="CONFIG_REV",precision="bf16")
    path.write_text(yaml.safe_dump(cfg))
    result=parse_config(["--config",str(path)])
    assert (result["model"],result["model_revision"],result["precision"])==("CONFIG_MODEL","CONFIG_REV","bf16")
    assert parse_config(["--config",str(path),"--precision","fp32"])["precision"]=="fp32"
    assert parse_config(["--method","window","--sink_tokens","0","--recent_tokens","1024","--book_files","a.txt","--max_tokens_per_book","4096"])["min_scored_idx"]==1025


@pytest.mark.parametrize("key,value",[("precision","typo"),("book_files",[]),("book_files",["a.txt","a.txt"]),("sink_tokens",-1),("max_tokens_per_book",-2),("recent_tokens",1023),("position_policy","fake"),("seed",True),("unknown",2),("selection_threshold",float('nan')),("min_scored_idx",1024)])
def test_invalid_config(key,value):
    cfg=config(); cfg[key]=value
    with pytest.raises(ValueError): validate(cfg)


def test_nll_known_and_uniform():
    nll=token_nll(torch.tensor([[0.5,0.5],[0.25,0.75]],dtype=torch.float64).log(),torch.tensor([0,0]))
    assert nll.tolist()==pytest.approx([math.log(2),math.log(4)],abs=1e-6)
    assert math.exp(nll.mean().item())==pytest.approx(math.sqrt(8),rel=1e-6)
    assert token_nll(torch.zeros(2,11),torch.tensor([2,5])).tolist()==pytest.approx([math.log(11)]*2)


def test_macro_micro():
    out=aggregate([dict(mean_nll_scored=1,scored_tokens=1),dict(mean_nll_scored=3,scored_tokens=3)])
    assert out["macro_book_nll"]==2
    assert out["micro_token_nll"]==2.5


@pytest.mark.parametrize("tokens,expected",[(1025,0),(1026,0),(1027,1),(4096,3070),(7141,6115),(16384,15358)])
def test_boundary(tokens,expected): assert scored_count(tokens)==expected


@pytest.mark.parametrize("deltas,status",[([-1,-1],"supported"),([1,1],"not_supported"),([0,0],"inconclusive"),([-1,1],"inconclusive"),([-1,0],"inconclusive")])
def test_states(deltas,status): assert bootstrap(deltas)["claim_status"]==status


def fixture_result(seed=0,method="window"):
    manifest=dict(model="m",model_revision="r",tokenizer_revision="r",test_books=[dict(book_id=str(i),text_sha256="text"+str(i),full_token_length=16384,input_tokens=16384,token_cap=16384,token_ids_sha256="tok"+str(i)) for i in range(2)])
    contract=dict(model="m",model_revision="r",tokenizer_revision="r",assets_manifest_sha256="manifest",precision="fp16",scorer_precision="fp32",position_policy="cache_relative",cache_budget=1024,min_scored_idx=1025,max_tokens_per_book=16384,add_special_tokens=True,eviction="after_forward",environment_id="env",numerical_source_sha256="source",protocol_id="test",seed=seed,split="test",determinism=dict(enabled=True))
    books=[dict(b,scored_tokens=15358,mean_nll_scored=2.0,sum_nll_scored=2.0*15358,ppl_scored=math.exp(2),scored_mask_sha256="mask") for b in manifest["test_books"]]
    r=dict(run_id=f"{method}-{seed}",schema_version=2,method=method,status="completed",validation_status="valid",contract=contract,contract_sha256=object_hash(contract),book_ids=[b["book_id"] for b in books],per_book=books,**aggregate(books))
    return r,manifest


@pytest.mark.parametrize("fault",["missing","extra","duplicate","nan","infinity","revision","mask_boundary","zero","tokens","aggregate","sum","incomplete"])
def test_fail_closed(fault):
    r,m=fixture_result()
    if fault=="missing": r["per_book"].pop(); r["book_ids"].pop()
    elif fault=="extra": r["per_book"].append(dict(r["per_book"][0],book_id="X")); r["book_ids"].append("X")
    elif fault=="duplicate": r["per_book"][1]=copy.deepcopy(r["per_book"][0]); r["book_ids"][1]="0"
    elif fault in {"nan","infinity"}: r["per_book"][0]["mean_nll_scored"]=float('nan' if fault=='nan' else 'inf')
    elif fault=="revision": r["contract"]["model_revision"]="bad"
    elif fault=="mask_boundary": r["contract"]["min_scored_idx"]=1024
    elif fault=="zero": r["per_book"][0]["scored_tokens"]=0
    elif fault=="tokens": r["per_book"][0]["token_ids_sha256"]="wrong"
    elif fault=="aggregate": r["macro_book_nll"]=1
    elif fault=="sum": r["per_book"][0]["sum_nll_scored"]=0
    elif fault=="incomplete": r["status"]="failed"
    r["contract_sha256"]=object_hash(r["contract"])
    with pytest.raises(ValueError): validate_result(r,m)


def test_seed_clusters():
    windows=[]; streams=[]
    for seed in range(3):
        w,m=fixture_result(seed); s,_=fixture_result(seed,"streaming")
        for b in s["per_book"]: b.update(mean_nll_scored=1.0,sum_nll_scored=15358,ppl_scored=math.e)
        s.update(aggregate(s["per_book"])); windows.append(w); streams.append(s)
    out=analyze_pairs(windows,streams,m)
    assert out["n_books"]==2 and out["paired_macro_delta_nll"]==-1 and out["claim_status"]=="supported"
    with pytest.raises(ValueError): analyze_pairs(windows[:1],streams[:1],m)
    streams[0]["per_book"][0]["scored_mask_sha256"]="different"
    with pytest.raises(ValueError): analyze_pairs(windows,streams,m)
