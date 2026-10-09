# Bounded demonstration and fallback

Live target 2–3 minutes: run `bash scripts/demo.sh` on the recorded delivery source, show CPU fixtures and the saved strict paired results. The command validates a real full run, prints NLL/PPL/CI and traces one book NPZ through its source/result/figure hashes. It allocates no GPU. During incomplete stages it reports pending, without a false verdict.

Saved prior `presentation/demo_recording*/session.cast`, stdout and MP4 captures are historical diagnostic fallbacks. After scientific execution completes, record the current full-result demo in a new immutable directory. `presentation/demo_recording_manifest.json` selects the actual current capture with source/script/paired-result/artifact hashes and exit code. The video replays captured terminal events; it is not a desktop recording or a member rehearsal. A real team rehearsal remains pending.

To make a new recording after any source changes, use `python scripts/record_demo.py --out presentation/demo_recording_<unique-id> --video`. The output directory must be new; keep prior captures. Compare the receipt's `demo_script_sha256` and diagnostic hash with the selected delivery source. This does not substitute for a signed peer audit or individual defense.

`defense_draft.pptx` has 12 slides and speaker notes while execution is pending; the completed generator writes `defense.pptx` with actual main/pilot/full/control results on the slides. The suggested 15-minute presentation / 10-minute Q&A / 2-minute transition format comes from the supplied course body; final instructor time/template rules are unknown. Real members should assign speaking parts using their actual roster.
