You are coding scientific abstracts for a systematic review of how the literature describes the *trajectory* of ageing. Apply the codebook below exactly. Judge from the title and abstract only, and record what the abstract *claims* in the authors' own framing, not what you believe about the biology. Do not search the web and do not look up the papers. Code every record in the attached batch file independently of the others.

# Codebook

**Arm B records only, `screen_relevant`** (decide this first): `yes` only if the abstract makes a claim about the *shape of an ageing trajectory*, whether of an organism, an organ, a function or a molecular layer, over age or over the life course. Words like "abrupt", "biphasic" or "accelerated aging" often appear with no such claim; code those `no`. If `no`, put `-` in every other field except `organism`. For Arm A records, `screen_relevant` is always `-`.

**`trajectory_code`** (exactly one):
- `P`, progressive/continuous: ageing, or the ageing variable, is described as gradual, progressive, cumulative or steadily declining, or modelled as a linear or monotonic function of age with no claim of nonlinearity.
- `NC`, nonlinear but continuous: the rate changes (acceleration, deceleration, plateau, curvilinear, waves or peaks of change, non-monotonic), but there is no claim of distinct qualitative states.
- `D`, discontinuous: qualitatively distinct states or phases, with a transition between them (switch, phase, stage, tipping point, critical transition, terminal phase, state change).
- `U`, unspecified: the abstract makes no claim about the shape of ageing. Arm A only; a relevant Arm B record is never `U`.
- `DEV`: the paper is about pre-adult development or maturation (neonates, postnatal development). Use `DEV` instead of `U`.

**Rules for frequent borderline cases**
1. A plain young-vs-old comparison with no trajectory language is `U`.
2. "Declines/increases with (advancing) age", "age-related reduction/accumulation" and "ageing leads to reduced X" are `P` implicit. A bare between-group difference with no such attribution stays `U`.
3. A change of slope anchored to an event (death, diagnosis) is `NC`, even when the authors call it a "transition", "inflection point" or "terminal decline". `D` requires qualitatively distinct states: a new state or phase, not only a faster rate.

**`explicitness`** (P, NC and D only; otherwise `-`): `explicit` when the study measures or formally models the trajectory (three or more ages, or continuous age) or the paper's own claim is about the shape. `implicit` when the shape is only carried by wording, including background adjectives ("the progressive loss of…").

**NC and D only** (otherwise `-`):
- `level`: `molecular` / `cellular` / `tissue-organ` / `physiological-functional` / `whole-organism` (including mortality) / `population-demographic`
- `scale`: `individual` (trajectories measured within individuals, longitudinally or by a per-individual state marker) or `population` (inferred from cross-sectional or aggregate data)
- `observation`: `observed` (the state or transition is measured directly in each individual) or `inferred` (recovered by statistical modelling, clustering, change-point detection or curve fitting)
- `anchor`: `chronological age` / `proximity to death` / `disease or pathology` / `physiological state` / `none stated`

**D only** (otherwise `-`):
- `reversibility`: `irreversible stated` / `reversible stated` / `not stated`
- `meaning`: a short quotation or paraphrase of what the authors call the discontinuity

**`organism`** (always): `human` / `mouse-rat` / `Drosophila` / `C. elegans` / `other` / `multiple` / `none`

**`evidence_quote`**: up to 15 words copied from the abstract that justify `trajectory_code` (or the screening decision), or `-`.

**`notes`**: Arm B only. When the authors' own shape vocabulary differs from your code, write it as `[authors: "..."]` (for example, "discontinuity" used for a change of slope). Otherwise `-`.

Use the values exactly as spelled above. Never leave a field empty: write `-`.

# Output format

Reply with **one code block only**, in TSV format (fields separated by a single TAB character, no tabs inside fields). The first line is the header below, followed by one line per record in the order of the batch file. Every record in the batch must appear. Add no commentary before or after the block.

```tsv
review_id	screen_relevant	trajectory_code	explicitness	level	scale	observation	anchor	reversibility	meaning	organism	evidence_quote	notes
```

Example lines (invented records, for format only):

```tsv
A999	-	P	implicit	-	-	-	-	-	-	human	muscle strength declines with advancing age	-
B999	no	-	-	-	-	-	-	-	-	mouse-rat	-	-
B998	yes	NC	explicit	physiological-functional	individual	inferred	proximity to death	-	-	human	accelerated decline in the years preceding death	[authors: "terminal phase"]
```
