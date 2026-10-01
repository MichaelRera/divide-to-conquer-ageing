# Divide to conquer: code and data

Code, data and results supporting Ünsal, Lemoine & Rera, *Divide to conquer: Two phases to make ageing as one* (*Geromedicine*, under revision).

The repository has two parts:

| Folder | What it supports |
|---|---|
| `survey/` | the sampled survey of the ageing literature (Section 2.1; Figures 2 and 3; Supplementary Figures S1–S3) |
| `logic/` | the formal check of the argument in Lean 4, and the logic diagram (Appendix and Response Figure R2 of the response to reviewers) |

## `survey/`: how the ageing literature frames the trajectory of ageing

| Path | Contents |
|---|---|
| `PROTOCOL.md` | protocol and codebook, written before any abstract was read, with the dated change log |
| `METHODS_section_2.1.md` | Methods, reliability and limitations text of Section 2.1, with the source of every number |
| `config/search_strings.txt` | exact PubMed queries |
| `data/sample.json` | the two stratified random samples (PMID, year, journal, title) |
| `data/codes_A.tsv`, `data/codes_B.tsv` | original coding of every record (representative sample A, vocabulary-matched sample B) |
| `data/corpus_works.json`, `edges.tsv`, `communities.json`, `network_stats.json` | OpenAlex citation network of the 4,318 vocabulary-matched papers and its Louvain communities |
| `data/vocab_counts.json` | yearly counts behind the vocabulary timeline |
| `data/*.tsv` (others) | derived tables and the pre-drawn 10% subset (`kappa_sheet.tsv`) |
| `scripts/` | sampling, network, vocabulary and figure scripts (`fig_*.py`); `fetch_abstracts.py` restores abstract text |
| `figures/` | every figure as PNG and PDF |
| `validation/` | blind re-coding of every record by two other language models (Gemini Flash 3.6, Perplexity), and the agreement analysis; see `validation/README.md` |

### Codebook

Each title and abstract receives one trajectory code: progressive/continuous (`P`), continuous-nonlinear (`NC`), discontinuous (`D`, qualitatively distinct states separated by a transition), no claim about shape (`U`), or pre-adult development (`DEV`). Nonlinear and discontinuous claims are further coded for level, scale of inference (individual or population), whether the transition is observed or inferred, its anchor (chronological age, proximity to death, disease, physiological state) and reversibility. The full codebook and every later clarification are in `PROTOCOL.md`; the version given to the blind re-coders is `validation/CODER_INSTRUCTIONS.md`.

### Regenerating the figures

```bash
cd survey/scripts
for f in fig_armA fig_vocab fig_tree fig_network fig_approach; do python3 $f.py; done
cd ../validation && python3 three_coders.py "Flash 3.6"     # agreement statistics
```

Requires Python 3 with matplotlib, networkx and pandas. These steps use only the local data.
`sample.py`, `network.py`, `seeds.py` and `vocab.py` query PubMed or OpenAlex and would overwrite the frozen data; do not re-run them unless you intend a new, clearly named draw.

### Abstracts are not included

PubMed abstracts are often under publisher copyright, so their text has been removed from this copy (from `data/sample.json`, `data/kappa_sheet.tsv`, `validation/data/frozen/sample_frame.tsv`, `validation/data/coding/coding_sheet.tsv` and the coding batches in `validation/LLM_valid/batches/`). Titles, PMIDs and all codes are kept. To restore the abstracts:

```bash
cd survey/scripts && python3 fetch_abstracts.py     # set NCBI_API_KEY to speed it up
```

They are needed only to rebuild the coding batches or re-run the validation notebooks. Because the abstracts were removed, `validation/data/frozen/input_hashes.json` no longer matches these files; it documents the files as they were coded.

## `logic/`: the argument, checked in Lean 4

| File | Contents |
|---|---|
| `DivideToConquer.lean` | definitions, the aggregation theorem, the independence of nonlinearity and discontinuity, what a binary readout settles, and the dependency graph of the paper's claims with the verdict of each reviewer critique |
| `LOGIC_MAP.md` | the same, in plain language |
| `fig_logic.py`, `Fig_logic.png/.pdf` | the logic diagram (Response Figure R2) |

Check with Lean 4 (core only, no Mathlib): `lean logic/DivideToConquer.lean`. It type-checks with no `sorry`.

## How this work was done

The survey was designed, and its primary coding performed, with AI assistance (Claude Opus, Anthropic) applying the written codebook; every record was then re-coded blind by two language models from other developers. The Lean formalisation and the scripts were also written with Claude. The authors directed and checked the work and take responsibility for it.

## Licence

Code: MIT (see `LICENSE`). Data, figures and text: CC BY 4.0. The OpenAlex metadata in `data/corpus_works.json` is CC0.
