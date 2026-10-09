# Pilot selection state

The user authorized both validation pilots and delegated the frozen selection rule on 2026-10-09. Execution follows the running main reproduction automatically. Both causal candidates/controls are implemented and tested; development IDs 1022, 11155 and 13089 and fixed parameters were recorded before losses. `configs/pilot_matrix.yaml` defines actual three-seed baseline/H1/H2 jobs on matched H800 MIG instances.

Selection rule is fixed in `docs/protocol_amendments.md`: invalid candidates cannot enter comparison; compare paired macro loss and measured cost under 1.10 ratio limits; prefer the lower acceptable-cost negative mean loss; evaluate H1 as the preregistered negative-result fallback if neither qualifies. `build_results.py` writes all comparisons and an immutable proposal. `complete_study.py` records its actual SHA and applies the rule under the owner delegation before any full improvement run. The actor is labelled as agent execution, never human review. No additional confirmation is required.

No test result selects a threshold, anchor set, seed or book. Until real pilot outputs exist, their values and nomination remain pending. Machine outputs live in `results/pilots/`; the actual selection record is `docs/approval_decisions.json`. Placeholder names are not experimental evidence.
