# How is ageing's trajectory conceptualised? A systematic, sampled review (1990–2025)

Protocol fixed on 2026-09-25, **before any abstract was read**. Any later change is logged at the bottom with its reason.

## Purpose

This answers Reviewer 2's objection: the manuscript's classification rests on a hand-picked set of 15 papers and on categories we defined in advance. We therefore ask two questions of a sample drawn by rule:

1. **Representativeness (Arm A).** Across the ageing literature as a whole, how is the trajectory of ageing framed: progressive/continuous, nonlinear but continuous, or discontinuous? How often is it left unspecified?
2. **Meaning (Arm B).** Among papers that use trajectory-shape vocabulary (nonlinear, phases, transitions, switches, waves…), what do they actually mean by it?

## Source and population

- Database: PubMed (NCBI E-utilities), queried on 2026-09-25.
- Population: `"Aging"[Majr] AND english[la]`, publication date 1990-01-01 to 2025-12-31. This gives 139,501 records: papers indexed by NLM as having ageing as a *major topic*. Indexing is done by NLM, not by us.
- Records without an abstract are excluded after retrieval and replaced by the next random draw from the same stratum.

## Arm A: representative sample

- Stratified random sample: **50 records per 5-year bin** (1990–94, 1995–99, 2000–04, 2005–09, 2010–14, 2015–19, 2020–25), 350 in total.
- Draws use random offsets into each stratum's PubMed ID list, with a fixed seed (20260925).

## Arm B: targeted sample

- Query: the Arm A population AND at least one trajectory-shape term in title/abstract. The exact string is in `search_strings.txt`. There are 4,318 hits for 1990–2025.
- Stratified random sample: **100 records per decade** (1990–99, 2000–09, 2010–19, 2020–25), 400 in total. Same seed and method.
- Terms such as "abrupt" or "accelerated aging" catch many irrelevant uses, so every Arm B record is first **screened**. It is relevant only if the abstract makes a claim about the *shape of an ageing trajectory* (of an organism, an organ, a function or a molecular layer, over age or over the life course).

## Unit and level of evidence

The unit is the title and abstract. Full texts are not read, which is a stated limitation. Coding records what the abstract *claims*, in the authors' own framing.

## Codebook (applied identically to both arms)

**T: trajectory framing** (exactly one):
- `P`: progressive/continuous. Ageing, or the ageing variable, is described as gradual, progressive, cumulative or steadily declining, or modelled as a linear or monotonic function of age with no claim of nonlinearity.
- `NC`: nonlinear but continuous. The rate changes (acceleration, deceleration, plateau, curvilinear, waves or peaks of change, non-monotonic), but there is no claim of distinct qualitative states.
- `D`: discontinuous. Qualitatively distinct states or phases with a transition between them (switch, phase, stage, tipping point, critical transition, terminal phase, state change).
- `U`: unspecified. The abstract makes no claim about the shape of ageing (e.g. it compares young vs old, or the trajectory is not at issue).

**E: explicitness** (for P, NC, D): `explicit` if the shape is stated or modelled; `implicit` if it is only carried by wording such as "age-related decline".

For NC and D records only:
- **L: level**: molecular / cellular / tissue-organ / physiological-functional / whole-organism (incl. mortality) / population-demographic.
- **S: scale of inference**: `individual` (trajectories measured within individuals, longitudinally or by a per-individual state marker) or `population` (inferred from cross-sectional or aggregate data).
- **O: observed vs inferred**: `observed` (the state or transition is measured directly per individual) or `inferred` (recovered by statistical modelling, clustering, change-point or curve fitting).
- **A: anchor of the transition**: `chronological age` / `proximity to death` / `disease or pathology` / `physiological state` / `none stated`.
- **R: reversibility** (D only): `irreversible stated` / `reversible stated` / `not stated`.
- **M: meaning** (D only): short free text quoting or paraphrasing what the authors call the discontinuity.

**Organism**: human / mouse-rat / Drosophila / C. elegans / other / multiple / none.

## Analysis

- Arm A: proportions of P / NC / D / U overall and per 5-year bin, with 95% Wilson confidence intervals. Proportion explicit vs implicit.
- Arm B: proportion relevant after screening; among relevant records, NC vs D per decade; for D, the distribution of L, S, O, A, R, plus a qualitative synthesis of M.
- Direct test of the manuscript's claim: are discontinuity claims more often individual-level/observed or population-level/inferred?
- Reproducibility: PMIDs, abstracts, codes and scripts are all saved here.

## Known limitations

- There is a single coder (Claude), applying a written codebook. Planned check: Michael or Ekin blindly re-codes a random 10% subset, and Cohen's κ is reported.
- MeSH indexing lags for the newest records (2025), and MeSH choices can themselves vary.
- Coding is at abstract level only.

## Change log

- 2026-09-25, before any abstract was read: the first sampling run crashed on a PubMed error response (rate limit) after 5 strata, and nothing had been saved. The sampler was made resumable. Each stratum now uses its own seed, the string `"20260925-<arm>-<y0>-<y1>"`, and is saved as soon as it is drawn. All strata were then drawn afresh. This changes which records are drawn, not how.
- 2026-09-25, after coding the first 25 Arm A records (1990–94): **codebook addition `DEV`.** Many records indexed under MeSH "Aging" concern pre-adult development or maturation (neonates, postnatal development). They are coded `DEV` instead of `U`. Results are reported both over all records and over senescence-relevant records only (excluding `DEV`). Two operational rules are also fixed for consistency. First, a plain young-vs-old comparison with no trajectory language is `U`. Second, wording such as "declines/increases with (advancing) age" or "age-related reduction/accumulation" counts as `P` implicit. Clarified after 128 records: an abstract that attributes a decline, loss or increase to ageing as a process ("aging leads to reduced X", "impairment occurs with aging") is `P` implicit. A bare between-group difference with no such attribution stays `U`. One earlier record (PMID 8601381) was re-coded under this clarification. Clarified after 214 records: **E = explicit** only when the study measures or formally models the trajectory (three or more ages, or continuous age) or the paper's own claim is about the shape. A background or definitional adjective ("the progressive loss of…") is implicit. Three earlier records (15571490, 12516005, 19725392) were re-coded to implicit.
- 2026-09-25, before coding Arm B: in Arm B notes, the authors' own shape vocabulary is recorded as `[authors: "..."]` whenever it differs from the structural code (e.g. "discontinuity" used for a slope change). This allows a direct vocabulary-versus-structure comparison, which is R2's circularity point. Also noted: Arm B stratum totals from month/year-split counting (521, 814, …) can slightly exceed single-query decade counts (521, 763, …), because records with cross-year publication dates are counted in both years. Sampling within strata is unaffected.
- 2026-09-25, after 215 Arm B records: rule made explicit. **A change of slope anchored to an event (death, diagnosis) is `NC`, even when the authors call it a "transition", "inflection point" or "terminal decline".** `D` requires qualitatively distinct states (a new state or phase, not only a faster rate). One earlier record (PMID 18808249, terminal decline in speed variability) was re-coded from D to NC. The authors' vocabulary stays recorded in the notes.
- 2026-09-25, at Michael's request (before coding started): **Arm C, citation network.** The *full* Arm B corpus (4,318 PubMed records, no sampling) is retrieved from OpenAlex (works matched by PMID) with reference lists; edges are citations between corpus papers. The manuscript's Table 2 papers, the Smurf-model chain, Carey 1998 and Roget 2024 (20 papers, resolved by DOI) are added as labelled seeds; 10 of the 20 were already retrieved by the Arm B query. Nodes in the Arm B sample carry their hand-codes, and the rest are uncoded. Questions: do discontinuity-framing papers cite each other (a shared convention) or arise independently? Which external works anchor the corpus? Where do the manuscript's papers sit? Scripts: `network.py`, `seeds.py`.
- 2026-09-25, after the network was built (analysis step, not coding): Louvain results varied between runs because node order depended on Python's string-hash seed. The graph is now built with sorted nodes and edges (`netcore.py`), and the partition is identical across hash seeds. The qualitative result did not change: 18 of 20 manuscript papers sit in one community in every run. A 10% blind re-coding sheet (`kappa_sheet.tsv`, 35 A + 40 B, seed `"20260925-kappa"`) was drawn.
- 2026-09-28, after all coding (reliability check): **the planned human re-coding of the 10% subset was replaced by blind re-coding of every record by two language models from other developers**, Gemini Flash 3.6 (Google) and Perplexity (default model, not disclosed by the service). Each received only the written codebook (`validation/CODER_INSTRUCTIONS.md`, `validation/LLM_valid/PROMPT.md`) and the titles and abstracts, in batches of 50, with web search off. No original code was shown to either. The κ is reported for the pre-drawn 10% subset (`kappa_sheet.tsv`) and for all records. Disagreements were not adjudicated; the reported counts use the original coding, and the limitation is stated in the manuscript. Also found: two Arm B PMIDs (27959617, 39505152) were drawn twice by the sampler, so Arm B has 398 distinct records; both duplicates were coded not relevant, so no reported proportion is affected beyond its denominator. Files were reorganised into `config/`, `data/`, `scripts/`, `figures/` and `validation/` (`MOVES_2026-09-28.tsv`). In Supplementary Figure S1, the cross-reference was corrected to Figure 3 (the survey figure after renumbering), the footer to the actual reliability check, and the Arm B count to "400 draws (398 distinct)".
