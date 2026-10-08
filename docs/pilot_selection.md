# Pilot selection state

No approved validation pilot has run. Both causal candidates and controls are implemented and tested; the first three eligible validation books and fixed parameters were recorded before losses. `configs/pilot_matrix.yaml` defines actual three-seed baseline/H1/H2 jobs.

Selection rule is fixed in `docs/protocol_amendments.md`: eliminate invalid candidates, compare paired macro loss and measured cost under1.10 ratio limits, prefer lower acceptable-cost loss, and nominate H1 for a complete negative-result evaluation if neither improves. `build_results.py` will write all candidate comparisons and a nomination, not a human decision. A real team review must confirm the nomination before test improvement execution.

No test result has selected a threshold, anchor set, seed or book. Actual pilot values, failures, nomination and reviewer decision remain pending; placeholder method names are not experimental evidence.
