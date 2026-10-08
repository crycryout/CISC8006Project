# Audit resolution

Current source was compared after fast-forwarding to `48e57c6`. The remote update adds only the execution plan; audited implementation issues remain present.

| Issue | Confirmed location / cause | Repair evidence |
|---|---|---|
| P0-01 | evaluator never enables upstream raw-K position shift | pending adapter, independent layer reference and 2×2 diagnostic |
| P0-02 | argparse nonempty defaults override YAML | pending strict defaults→YAML→explicit CLI merge |
| P0-03 | paired analyzer accepts book intersection | pending full manifest/seed/contract validation |
| P0-04 | fixed R0001 / exist_ok output overwrites | pending exclusive IDs and atomic output |
| P0-05 | top-level micro mean confused with primary macro | pending named estimands and known-answer fixture |
| P0-06 | oracle checks only first K; repeated helper is not RoPE proof | pending every-layer K/V and independent real attention |
| P1-01–04 | untracked position arrays, weak registry, end-time commit, batch-only writes | pending lossless traces, launch snapshot and failure tests |
| P1-05–12 / P2 | provenance, policy, data, figure mapping, seeds, memory and budget | pending verified documentation and release checks |

Historical file SHA256 values are frozen in `wp0_inventory.json`; legacy evidence will never be rewritten into v2 evidence.
