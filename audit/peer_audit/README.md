# Independent peer-audit packet

State: prepared; **no independent person has performed or signed this audit**. Agent clean-checkout verification is engineering verification only.

1. Clone the execution branch; record actual reviewer identity, date and checkout SHA. Read `docs/review_packet.md` and approval status. Do not receive private caches/credentials/Moodle sessions.
2. Run `bash scripts/setup_env.sh .venv-peer` and `.venv-peer/bin/python -m pip check`; save exact command, exit code and failure log. Record OS/Python/driver if GPU available.
3. Run `CISC_PYTHON=.venv-peer/bin/python bash scripts/run_smoke.sh --mode cpu`; record unique ID. Deliberately retry the ID and verify nonzero refusal with original hashes unchanged. CPU smoke requires no model/network/assets beyond committed fixture sources.
4. Recover public assets via `scripts/prepare_data.py`, run `verify_assets.py`, and inspect formal run checksums/NPZ reconstruction with `validate_runs.py` and `audit_scientific_results.py`. The current user authorized H800 resources and scientific execution; use unique IDs for any additional smoke and keep all frozen study artifacts unchanged.
5. Document findings, exact failures and fixes in a signed reviewer note, link run/log/commit and state pass/partial/fail. Verify the raw-K reference is independent and a missing-book analysis fails. Send findings through the team's authorized channel; agent does not contact peers automatically.

Personal checklist: explain scoring1025/3070/6115/15358, macro/micro distinction, why3 seeds are not30 books, cache-relative K positions, calibration causality, extra cost, negative outcomes, owner authorization and still-unknown human course facts. No live agent impersonates a member during assessment.
