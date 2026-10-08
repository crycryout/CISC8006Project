# Third-party provenance and redistribution

| Component | Source / license | Project use and redistribution |
|---|---|---|
| Official StreamingLLM code | [MIT license at pinned commit](https://github.com/mit-han-lab/streaming-llm/blob/2e5042606d69933d88fbf909bd77907456b9b4dd/LICENSE) | Vendored files unchanged; preserve upstream notice. Adapter lives in `src/`. |
| Pythia2.8B weights/tokenizer | [Pinned model card](https://huggingface.co/EleutherAI/pythia-2.8b/blob/2a259cdd96a4beb1cdf467512e3904197345f6a9/README.md), Apache2.0 | Download by revision/hash; weights excluded from Git/release. Not described as MIT. |
| PG19 benchmark/split metadata | [DeepMind PG19](https://github.com/google-deepmind/pg19), Apache2.0 metadata license | Download original processed GCS texts, verify hashes. Texts excluded from Git/release; underlying Gutenberg works need jurisdiction-specific reuse checks for redistribution. |
| StreamingLLM paper | [arXiv v4](https://arxiv.org/html/2309.17453v4), CC BY4.0 | Cite mechanisms; generate own measured plots; no copied paper figures in deliverables. |
| Transformers / PyTorch / NumPy / analysis tools | Distribution LICENSE notices in installed wheels | Pinned installation; no dependency source relicense or claims of common MIT coverage. |
| Course materials | User-provided course body, hashes in execution plan | No Moodle HTML, personal session fields or private approvals bundled. |

This table records sources and intended artifact contents, not a blanket license for every dependency or underlying book. Preserve upstream notices. Repository-authored code has no newly assigned license without owner instruction.
