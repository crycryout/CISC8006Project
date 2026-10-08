"""Configuration contract: defaults < YAML < explicitly supplied CLI."""
import argparse
import re
import uuid
from pathlib import Path
import yaml

DEFAULTS = dict(model="EleutherAI/pythia-2.8b", model_revision="2a259cdd96a4beb1cdf467512e3904197345f6a9",
    precision="fp16", scorer_precision="fp32", position_policy="cache_relative", run_id=None,
    method=None, book_files=None, sink_tokens=None, recent_tokens=None, max_tokens_per_book=None,
    min_scored_idx=None, output_dir=None, seed=0, phase="diagnostic", protocol_id="reproduction-v2-candidate",
    assets_manifest="data/assets_manifest.json", manifest_split="test", asset_root="data/pg19", offline=True,
    device="cuda", calibration_start=64, calibration_end=512, selection_threshold=0.90, max_gpu_seconds=3600,
    parent_run_id=None, environment_id="h800-torch214-transformers433", inject_failure_after_book=None)
METHODS = {"window","streaming","h1_adaptive_sink","h2_sink_selection","fixed_sink","calibration_control","h2_forced_prefix","random_anchors","h2_no_first"}
PHASES = {"diagnostic","smoke","reproduction","pilot","improvement","ablation"}


def validate(cfg):
    if set(cfg)-set(DEFAULTS):
        raise ValueError(f"unknown configuration keys: {sorted(set(cfg)-set(DEFAULTS))}")
    for key in ("model","model_revision","protocol_id","assets_manifest","asset_root","environment_id"):
        if not isinstance(cfg[key],str) or not cfg[key]: raise ValueError(f"invalid {key}")
    if cfg["method"] not in METHODS or cfg["phase"] not in PHASES: raise ValueError("unknown method/phase")
    if cfg["precision"] not in {"fp16","bf16","fp32"} or cfg["scorer_precision"] not in {"fp32","legacy_forward_dtype"}: raise ValueError("unknown precision/scorer")
    if cfg["position_policy"] not in {"legacy_implicit","cache_relative"}: raise ValueError("unknown position policy")
    if cfg["manifest_split"] not in {"test","dev"} or cfg["device"] not in {"cpu","cuda"}: raise ValueError("unknown split/device")
    if type(cfg["offline"]) is not bool: raise ValueError("offline must be boolean")
    for key in ("sink_tokens","recent_tokens","max_tokens_per_book","seed","calibration_start","calibration_end","max_gpu_seconds"):
        if type(cfg[key]) is not int or cfg[key]<0: raise ValueError(f"{key} must be nonnegative integer")
    budget=cfg["sink_tokens"]+cfg["recent_tokens"]
    if budget!=1024 or cfg["recent_tokens"]<=0 or cfg["max_tokens_per_book"]<=budget+2: raise ValueError("requires budget 1024, recent>0 and positive scored region")
    if cfg["method"]=="window" and cfg["sink_tokens"]!=0: raise ValueError("window requires zero sinks")
    if cfg["method"] in {"streaming","calibration_control","h2_forced_prefix","h2_sink_selection","random_anchors","h2_no_first"} and cfg["sink_tokens"]!=4: raise ValueError("method requires four sinks/anchors")
    if cfg["min_scored_idx"] is None: cfg["min_scored_idx"]=budget+1
    if type(cfg["min_scored_idx"]) is not int or cfg["min_scored_idx"]!=budget+1: raise ValueError("scoring begins at budget+1")
    books=cfg["book_files"]
    if not isinstance(books,list) or not books or any(not isinstance(x,str) or not x for x in books): raise ValueError("book_files must be nonempty path list")
    if len({Path(x).stem for x in books})!=len(books): raise ValueError("duplicate book IDs")
    if not 0<=cfg["calibration_start"]<cfg["calibration_end"]<budget: raise ValueError("calibration must finish before eviction")
    if type(cfg["selection_threshold"]) not in {int,float} or not 0<cfg["selection_threshold"]<=1: raise ValueError("invalid selection threshold")
    if cfg["max_gpu_seconds"]<=0: raise ValueError("timeout must be positive")
    if cfg["phase"] in {"reproduction","improvement","pilot","ablation"}:
        if cfg["position_policy"]!="cache_relative" or cfg["scorer_precision"]!="fp32": raise ValueError("scientific phases require faithful positions and fp32 scoring")
        expected_cap=16384 if cfg["phase"] in {"reproduction","improvement"} else 8192
        if cfg["max_tokens_per_book"]!=expected_cap or cfg["precision"]!="fp16" or cfg["seed"] not in {0,1,2}: raise ValueError("wrong frozen cap/precision/seed")
        expected_split="test" if cfg["phase"] in {"reproduction","improvement"} else "dev"
        if cfg["manifest_split"]!=expected_split: raise ValueError("test/development isolation violated")
        if cfg["model"]!=DEFAULTS["model"] or cfg["model_revision"]!=DEFAULTS["model_revision"]: raise ValueError("wrong pinned model")
    if cfg["run_id"] is None: cfg["run_id"]="auto-"+uuid.uuid4().hex[:16]
    if not isinstance(cfg["run_id"],str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,95}",cfg["run_id"]): raise ValueError("unsafe run ID")
    return cfg


def parse_config(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument("--config")
    ints={"sink_tokens","recent_tokens","max_tokens_per_book","min_scored_idx","seed","calibration_start","calibration_end","max_gpu_seconds","inject_failure_after_book"}
    for key in DEFAULTS:
        flags=["--"+key]+(["--"+key.replace("_","-")] if "_" in key else [])
        opts={"default":argparse.SUPPRESS}
        if key=="book_files": opts["nargs"]="+"
        elif key=="offline": opts["action"]=argparse.BooleanOptionalAction
        elif key in ints: opts["type"]=int
        elif key=="selection_threshold": opts["type"]=float
        parser.add_argument(*flags,**opts)
    supplied=vars(parser.parse_args(argv)); path=supplied.pop("config"); cfg=dict(DEFAULTS)
    if path:
        loaded=yaml.safe_load(Path(path).read_text())
        if not isinstance(loaded,dict): parser.error("configuration must be a mapping")
        if set(loaded)-set(DEFAULTS): parser.error(f"unknown keys: {sorted(set(loaded)-set(DEFAULTS))}")
        cfg.update(loaded)
    cfg.update(supplied)
    try: return validate(cfg)
    except ValueError as error: parser.error(str(error))
