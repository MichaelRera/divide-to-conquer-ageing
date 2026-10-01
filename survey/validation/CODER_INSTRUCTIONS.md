# Instructions for the independent coder

You receive two files: this one and `data/coding/coding_sheet.xlsx`. **Do not open anything else in `systematic_review/`.** The original codes, the notes and the report are there, and seeing them would break blinding.

## What to do

1. Open `coding_sheet.xlsx`. There is one row per record: a title and an abstract (748 in all). Edit only the yellow columns. Each coded field has a drop-down list.
2. **Do the rows with `priority_10pct = 1` first.** There are 75 (35 in Arm A, 40 in Arm B), and they are sorted to the top of each arm. These rows alone are enough for the planned κ. Everything beyond them is a bonus.
3. Judge from the title and abstract only. Record what the *abstract claims*, in the authors' own framing, not what you believe about the biology.
4. Fill in `coder_id` (initials, or the model name and version) and `coding_date` on every row you code.
5. After each session, run `notebooks/03_validate_coding.ipynb` (or ask whoever runs the pipeline to do it) and fix any errors it lists.

## Codebook

**Arm B only, `screen_relevant`** (decide this first): `yes` only if the abstract makes a claim about the *shape of an ageing trajectory*, whether of an organism, an organ, a function or a molecular layer, over age or over the life course. Words like "abrupt" or "accelerated aging" often appear with no shape claim; mark those `no`. If `no`, leave every other field empty except `organism`. Arm A: leave `screen_relevant` empty.

**`trajectory_code`** (exactly one):
- `P`, progressive/continuous: ageing, or the ageing variable, is described as gradual, progressive, cumulative or steadily declining, or modelled as a linear or monotonic function of age with no claim of nonlinearity.
- `NC`, nonlinear but continuous: the rate changes (acceleration, deceleration, plateau, curvilinear, waves or peaks of change, non-monotonic), but there is no claim of distinct qualitative states.
- `D`, discontinuous: qualitatively distinct states or phases, with a transition between them (switch, phase, stage, tipping point, critical transition, terminal phase, state change).
- `U`, unspecified: the abstract makes no claim about the shape of ageing.
- `DEV`: the paper is about pre-adult development or maturation (neonates, postnatal development). Use `DEV` instead of `U`.

**Rules that settle frequent borderline cases**
- A plain young-vs-old comparison with no trajectory language is `U`.
- "Declines/increases with (advancing) age", "age-related reduction/accumulation" and "ageing leads to reduced X" are `P` implicit. A bare between-group difference with no such attribution stays `U`.
- A change of slope anchored to an event (death, diagnosis) is `NC`, even when the authors call it a "transition", "inflection point" or "terminal decline". `D` requires qualitatively distinct states: a new state or phase, not only a faster rate.

**`explicitness`** (P, NC and D only): `explicit` when the study measures or formally models the trajectory (three or more ages, or continuous age) or the paper's own claim is about the shape. `implicit` when the shape is only carried by wording, including background adjectives ("the progressive loss of…").

**NC and D only** (leave empty otherwise):
- `level`: molecular / cellular / tissue-organ / physiological-functional / whole-organism (including mortality) / population-demographic.
- `scale`: `individual` (trajectories measured within individuals, longitudinally or by a per-individual state marker) or `population` (inferred from cross-sectional or aggregate data).
- `observation`: `observed` (the state or transition is measured directly in each individual) or `inferred` (recovered by statistical modelling, clustering, change-point detection or curve fitting).
- `anchor`: chronological age / proximity to death / disease or pathology / physiological state / none stated.

**D only:**
- `reversibility`: irreversible stated / reversible stated / not stated.
- `meaning`: a short quotation or paraphrase of what the authors call the discontinuity.

**`organism`** (every coded row): human / mouse-rat / Drosophila / C. elegans / other / multiple / none.

**Optional but helpful:** `evidence_quote`, a few words from the abstract behind your code. `notes`: in Arm B, write the authors' own shape vocabulary as `[authors: "..."]` whenever it differs from your code (for example, "discontinuity" used for a change of slope).

## If the coder is a language model

- Use a **fresh session** with no project files, memory or CLAUDE.md. Give it only this file and the sheet, or the rows as text.
- Record the exact model name and version in `coder_id`.
- A model from another developer (not Anthropic) gives more independence from the original Claude Opus 5.5 coding than another Claude model does. Report whichever you use as such.
