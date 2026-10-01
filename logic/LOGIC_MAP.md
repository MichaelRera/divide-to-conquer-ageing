# Logical structure of "Divide to conquer" (round-3 text), checked in Lean 4

Source: `geromed_v3_tracked.docx`, with tracked changes accepted. The Google Doc argues the same way, but it could not be read because the browser extension was offline.
Formal file: `DivideToConquer.lean`. It type-checks under Lean 4.34.1 (core only) with 0 errors and no `sorry`. Every theorem uses only Lean's standard foundational axioms.

## 1. Definitions (the paper's vocabulary, made precise)

| | Definition | Where in the text |
|---|---|---|
| D1 | **Nonlinearity**: the rate of change is not constant. Non-monotonicity (waves) is a special case. | Intro ¶4 |
| D2 | **Discontinuity**: a transition between *qualitatively different states* | Abstract, Intro ¶4 |
| D3 | **Heterogeneity**: population heterogeneity (same trajectory, different rate/onset) or system heterogeneity (different organs, different timing) | "Unified phased ageing" |
| D4 | **Phase**: in the Lean file, a two-valued state per individual (`Phase.one`/`Phase.two`) that an assay reads at a given age | Smurf model |

## 2. What is *proven* (Part I of the Lean file)

- **Theorem A: aggregation hides discontinuity.** If every individual switches state at a different age, the population curve rises linearly. The paper says "Population-level homogeneity is not evidence against individual-level discontinuity", and this is now a theorem. It is also the logic of the Tricoire & Rera AMP re-analysis (Figure 2).
- **Lemma: the population curve counts phase-2 individuals.** This holds for every cohort, not just the example: what a cross-sectional study sees is *phase composition*.
- **Theorem B: the two concepts are independent.** An individual can show nonlinear change without ever changing state. A cohort of individuals who all change state can still show a linear population trend. Neither concept entails the other, so treating the terms as interchangeable is a logical error, not only a stylistic one. This is the paper's central conceptual claim.
- **Theorem C: a binary readout does not settle the mechanism.** A continuously accumulating variable read through a threshold gives *identical* per-individual readouts to a true two-state switch.

## 3. The argument graph (Part II)

```
 C2 concepts distinct ──┬──► C3 Table-2 taxonomy ──┐
 (Theorem B)            ├──► C8 frailty mapping    ├──► C7 "the discontinuous cluster reflects
                        │                          │      biphasic ageing"  (hypothesis)
 C1 terms conflated ────┴──► C10 the framework     │
 (vocabulary + review)                             │
                                                   │
 C4 two observed phases ──┬───────────────────────┘
 (Smurf, per individual)  ├──► C5 population trend = phase composition (+ Theorem A)
                          ├──► C6 proximity to death organises state
                          └──► C9 a two-phase life history can be selected (Roget 2024)
```

**Separation (proven):** C3 (the taxonomy) is not among the premises of C4 (the two phases) or of C5. This is Michael's key point, now made mechanical: conceding circularity for the taxonomy cannot reach the paper's own claim.

**How each critique lands (computed by `decide`):**

| Claim | Circularity (R2) | Detection artefact (R3, Carbonneau) | Representativeness (R2) |
|---|---|---|---|
| C3 taxonomy | **falls** (conceded) | n/a | **falls** without the review |
| C7 cluster = biology | **falls**, so correctly stated as a hypothesis | n/a | falls |
| C1 terms conflated | stands only because of the sampled review | n/a | stands only because of the review |
| C4 two phases | stands | stands | stands |
| C5 composition | stands | stands | stands |
| C6 death organises | stands (one support is observational) | stands | stands |
| C9 selection | stands | stands | stands |

The sampled review is therefore **load-bearing for C1**, not decoration. Without it, "the field conflates these terms" rests only on authors' vocabulary, which is exactly what R2 attacks.

## 4. Weak points the formalisation exposes (suggested fixes)

1. **The uniqueness claim in the abstract is contradicted by the paper's own citation.** The abstract calls the Smurf model "to date the only framework in which two physiologically distinct phases have been directly observed at the individual level". The text itself cites medfly "waiting/reproductive" modes that "individuals were observed to switch" between [58]. The sampled review also found machine-scored individual states in isogenic *C. elegans* (PMID 22610697). *Fix:* "the only framework in which a directly observed, per-individual phase **predicts imminent death**". The review supports that narrower claim: none of the 109 relevant records has such a marker.
2. **Direct observation answers Carbonneau, but not the threshold model (Theorem C).** The Carbonneau paragraph says a null model "has no purchase … because there is no inferred structure for it to dissolve". That is true for *detection artefacts*. But a binary Smurf readout would look the same whether it comes from a continuous variable crossing a threshold (the saturating-removal model [77]) or from a real change of state. For "discontinuity" in the strong sense of D2 you need an extra premise: the two phases are *qualitatively* different. That premise has evidence behind it: coordinated change across transcriptome, metabolome and behaviour at the transition, and a short remaining lifespan after it that does not depend on age. *Fix:* one sentence in that paragraph citing this evidence explicitly. This also matches the Conclusion, which already lists "threshold" and "programme" as open alternatives.
3. **Two sentences say "does" where only "can" is established.**
    - *Conclusion:* "what is observed in a cohort … **emerges** from a discontinuous transition occurring at different times in different individuals." Theorem A proves *compatibility*, not that it happens in every cohort. Change "emerges" to "**can emerge**", or restrict the claim to cohorts where phase has been measured.
    - *"Lifespan and life history":* the claim that midlife "waves" may reflect phase composition is correctly hedged ("may"). Keep it that way.
4. **The sorting of the discontinuous group is internally inconsistent.** Pridham 2024 [41] is placed in the discontinuous group. But its own Table 2 row reads "primarily continuous/approximately linear drift with possible late-life … tipping point". Under the paper's own definitions it belongs in the intermediate or continuous group, or needs a note. [33, 34] describe disease transitions (lung injury, liver cancer), not ageing. The "four axes" paragraph partly handles this, but the group list in "From continuous non-linearity to discontinuity" does not.
5. **Scope needs to be stated in the abstract.** The abstract ends by calling biphasic ageing "a hypothesis to be tested". The introduction says "Such a phase is not hypothetical". These do not contradict each other: the first is about C7 (what the *literature cluster* means), the second about C4 (the *observed* phases in model organisms). But a reviewer reading the abstract alone will see a contradiction. *Fix:* in the abstract, say that the phases are observed in flies, mice and other organisms, and that whether the *literature cluster* reflects them is the hypothesis. This also addresses R3's comment on how the review is pitched.
6. **Minor points.**
    - "The Smurf transition is, in practice, near-irreversible" ("four axes") sits next to "whether they are reversible" as future work (Conclusion). Say what "near" rests on.
    - The frailty mapping (C8) rests only on vocabulary. The text already calls it "conceptual rather than empirically diagnostic", which is consistent.
