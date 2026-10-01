/-
  Logical structure of "Divide to conquer: Two phases to make ageing as one"
  (Ünsal, Lemoine, Rera; revision round 3, text of geromed_v3_tracked.docx).

  Three layers.
  Part I   — a minimal concrete model in which the paper's *mathematical* claims are
             theorems, proven here (no `sorry`).
  Part II  — the argument graph: claims, what each claim rests on, which critiques hit which
             kind of support, and what depends on what. All verdicts are computed by `decide`.
  Part III — the empirical premises the argument cannot prove, stated as named axioms so that
             every load-bearing assumption is visible.

  Lean 4 core only (no Mathlib). Check with:  lean DivideToConquer.lean
-/

namespace Geromed

/-! ## Part I — the mathematical core -/

/-- Physiological phase of an individual in the two-phase (Smurf) model. -/
inductive Phase where
  | one   -- non-Smurf
  | two   -- Smurf: end-of-life phase
  deriving DecidableEq, Repr

/-- An individual is characterised by the age at which it enters phase 2. -/
structure Indiv where
  transition : Nat
  deriving Repr

def phaseAt (i : Indiv) (t : Nat) : Phase :=
  if t < i.transition then .one else .two

/-- A marker read in one individual: flat within each phase, different between phases
    (e.g. antimicrobial-peptide expression, Rera et al. 2012). -/
def marker (i : Indiv) (t : Nat) : Nat :=
  match phaseAt i t with
  | .one => 0
  | .two => 1

/-- An individual trajectory is *discontinuous* (in the paper's sense) when the individual
    changes qualitative state at some age. -/
def Discontinuous (i : Indiv) : Prop := ∃ t, phaseAt i t ≠ phaseAt i (t + 1)

/-- A cohort and its population-level (summed) marker, as a cross-sectional study sees it. -/
abbrev Cohort := List Indiv

def popMarker : Cohort → Nat → Nat
  | [], _ => 0
  | i :: c, t => marker i t + popMarker c t

/-- The population curve rises by the same amount at every step on `[0, n]`: a *linear,
    progressive* trend, the shape classical definitions of ageing assume (Table 1). -/
def PopLinearOn (c : Cohort) (n : Nat) : Prop :=
  ∀ t, t < n → popMarker c (t + 1) = popMarker c t + popMarker c 1 - popMarker c 0

instance (c : Cohort) (n : Nat) : Decidable (PopLinearOn c n) := by
  unfold PopLinearOn; exact inferInstance

/-- General lemma: the population signal counts the individuals already in phase 2.
    What a cohort shows is **phase composition**, not within-individual change. -/
theorem popMarker_counts (c : Cohort) (t : Nat) :
    popMarker c t = (c.filter (fun i => decide (i.transition ≤ t))).length := by
  induction c with
  | nil => rfl
  | cons i c ih =>
    simp only [popMarker, marker, phaseAt, List.filter_cons, ih]
    by_cases h : t < i.transition
    · have : ¬ (i.transition ≤ t) := by omega
      simp [h, this]
    · have : i.transition ≤ t := by omega
      simp [h, this]; omega

/-- A cohort of five individuals whose transitions are staggered over ages 1–5. -/
def staggered : Cohort := [⟨1⟩, ⟨2⟩, ⟨3⟩, ⟨4⟩, ⟨5⟩]

theorem staggered_all_discontinuous : ∀ i ∈ staggered, Discontinuous i := by
  intro i hi
  refine ⟨i.transition - 1, ?_⟩
  simp [staggered] at hi
  rcases hi with h | h | h | h | h <;> subst h <;> decide

theorem staggered_pop_linear : PopLinearOn staggered 5 := by decide

/-- **Theorem A (aggregation).** A perfectly linear, progressive population trend is compatible
    with every individual being discontinuous. Hence population-level progressivity is not
    evidence against individual-level discontinuity (Conclusion; Tricoire & Rera 2015
    re-analysis of the AMP data; Figure 2). -/
theorem aggregation_hides_discontinuity :
    ∃ c : Cohort, PopLinearOn c 5 ∧ ∀ i ∈ c, Discontinuous i :=
  ⟨staggered, staggered_pop_linear, staggered_all_discontinuous⟩

/-- A continuous trajectory is represented by an individual that never changes phase while its
    measured value changes at a non-constant rate. -/
def nonlinearValue (t : Nat) : Nat := t * t

theorem nonlinear_witness :
    nonlinearValue 2 - nonlinearValue 1 ≠ nonlinearValue 1 - nonlinearValue 0 := by decide

theorem one_state_throughout (t : Nat) (h : t + 1 < 1000) :
    phaseAt ⟨1000⟩ t = phaseAt ⟨1000⟩ (t + 1) := by
  have h1 : t < 1000 := by omega
  simp [phaseAt, h, h1]

/-- **Theorem B (the two concepts are independent).** An individual can follow an accelerating
    (nonlinear) value while staying in one single state over its observed life (ages < 1000),
    and — Theorem A — a cohort of individuals that all switch state can show a linear population
    trend. Neither property entails the other, so "nonlinear" and "discontinuous" cannot be used
    interchangeably: the paper's central conceptual claim. -/
theorem nonlinearity_without_discontinuity :
    nonlinearValue 2 - nonlinearValue 1 ≠ nonlinearValue 1 - nonlinearValue 0 ∧
    ∀ t, t + 1 < 1000 → phaseAt ⟨1000⟩ t = phaseAt ⟨1000⟩ (t + 1) :=
  ⟨nonlinear_witness, one_state_throughout⟩

/-- **Theorem C (what a binary readout does not settle).** A continuously accumulating
    variable read through a threshold gives exactly the same per-individual readout as a true
    two-state switch. So direct observation of a binary phenotype rules out *detection
    artefacts* (Carbonneau et al.), but by itself does not decide between "continuous process +
    threshold" (saturating-removal model [77]) and "loss of stability / new attractor"
    (the bifurcation reading). The paper states both as open mechanistic hypotheses
    (Conclusion); this theorem marks where that openness sits. -/
def thresholdReadout (k t : Nat) : Phase := if t < k then .one else .two

theorem readout_underdetermines_mechanism (k t : Nat) :
    thresholdReadout k t = phaseAt ⟨k⟩ t := rfl

/-! ## Part II — the argument graph -/

/-- The kinds of support a claim can rest on. -/
inductive Support where
  | authorsVocabulary        -- how the original authors describe their own data
  | populationInference      -- smoothing / clustering / curve fitting on (mostly cross-sectional) data
  | individualObservation    -- per-individual phase assignment by a direct assay (Smurf)
  | formalModel              -- mathematics: Part I, Strehler–Mildvan, [77], Roget 2024
  | sampledReview            -- the new systematic, sampled review (random samples + network)
  deriving DecidableEq, Repr

/-- The critiques raised by the reviewers. -/
inductive Critique where
  | circularity              -- R2: categories built from authors' vocabulary
  | detectionArtefact        -- R3: Carbonneau 2026; Meyer & Schumacher 2024
  | frailtyComposition       -- Vaupel-type survivor/composition effects on cross-sectional data
  | unrepresentative         -- R2: hand-picked papers, predefined categories
  deriving DecidableEq, Repr

/-- Which critique undermines which kind of support. -/
def hits : Critique → Support → Bool
  | .circularity,        .authorsVocabulary   => true
  | .detectionArtefact,  .populationInference => true
  | .frailtyComposition, .populationInference => true
  | .unrepresentative,   .authorsVocabulary   => true
  | _, _ => false

/-- The paper's claims. -/
inductive Claim where
  | C1_termsConflated     -- "switch", "wave", "phase", "nonlinear" used interchangeably for distinct structures
  | C2_conceptsDistinct   -- nonlinearity ≠ discontinuity; discontinuity ⊋ heterogeneity
  | C3_taxonomy           -- Table 2: continuous-nonlinear / intermediate / discontinuous sorting
  | C4_twoPhases          -- in Drosophila (and mice, other organisms) life has two observed phases
  | C5_trendIsComposition -- population "progressive" trends can be phase composition (AMP re-analysis)
  | C6_deathOrganises     -- proximity to death, not chronological age, organises late-life state
  | C7_clusteringMeaning  -- the discontinuous cluster reflects biphasic ageing (stated as hypothesis)
  | C8_frailtyMapping     -- phenotype model ↔ discontinuity; deficit index ↔ continuous-nonlinear
  | C9_selected           -- a two-phase life history can be selected (evolutionary rationale)
  | C10_framework         -- the paper's contribution: a shared vocabulary for comparing findings
  deriving DecidableEq, Repr

/-- What each claim rests on, as the text states it. -/
def support : Claim → List Support
  | .C1_termsConflated     => [.authorsVocabulary, .sampledReview]
  | .C2_conceptsDistinct   => [.formalModel]
  | .C3_taxonomy           => [.authorsVocabulary]
  | .C4_twoPhases          => [.individualObservation]
  | .C5_trendIsComposition => [.individualObservation, .formalModel]
  | .C6_deathOrganises     => [.individualObservation, .populationInference]
  | .C7_clusteringMeaning  => [.authorsVocabulary]
  | .C8_frailtyMapping     => [.authorsVocabulary]
  | .C9_selected           => [.formalModel]
  | .C10_framework         => [.formalModel]

/-- Which claims each claim uses as premises. -/
def dependsOn : Claim → List Claim
  | .C1_termsConflated     => []
  | .C2_conceptsDistinct   => []
  | .C3_taxonomy           => [.C2_conceptsDistinct]
  | .C4_twoPhases          => []
  | .C5_trendIsComposition => [.C4_twoPhases]
  | .C6_deathOrganises     => [.C4_twoPhases]
  | .C7_clusteringMeaning  => [.C3_taxonomy, .C4_twoPhases]
  | .C8_frailtyMapping     => [.C2_conceptsDistinct]
  | .C9_selected           => [.C4_twoPhases]
  | .C10_framework         => [.C1_termsConflated, .C2_conceptsDistinct]

def allClaims : List Claim :=
  [.C1_termsConflated, .C2_conceptsDistinct, .C3_taxonomy, .C4_twoPhases, .C5_trendIsComposition,
   .C6_deathOrganises, .C7_clusteringMeaning, .C8_frailtyMapping, .C9_selected, .C10_framework]

/-- Transitive premises (fuel = number of claims is enough: the graph is acyclic). -/
def premisesAux : Nat → Claim → List Claim
  | 0, _ => []
  | n + 1, c => (dependsOn c).flatMap (fun d => d :: premisesAux n d)

def premises (c : Claim) : List Claim := premisesAux allClaims.length c

/-- A claim *survives* a critique if at least one of its supports is not hit by it,
    and every premise it depends on also survives. -/
def ownSurvives (k : Critique) (c : Claim) : Bool := (support c).any (fun s => !hits k s)

def survives (k : Critique) (c : Claim) : Bool :=
  ownSurvives k c && (premises c).all (ownSurvives k)

/-- **Separation theorem.** The paper's own two-phase claim does not depend on the literature
    taxonomy (Michael's point: the two must not be conflated). -/
theorem twoPhases_independent_of_taxonomy : Claim.C3_taxonomy ∉ premises .C4_twoPhases := by
  decide

theorem composition_independent_of_taxonomy : Claim.C3_taxonomy ∉ premises .C5_trendIsComposition := by
  decide

/-- **R2 conceded where it lands, and only there.** The taxonomy falls to circularity;
    the two-phase claim and its consequences do not. -/
theorem circularity_verdicts :
    survives .circularity .C3_taxonomy = false ∧
    survives .circularity .C7_clusteringMeaning = false ∧
    survives .circularity .C4_twoPhases = true ∧
    survives .circularity .C5_trendIsComposition = true ∧
    survives .circularity .C9_selected = true := by decide

/-- **R3 (Carbonneau) lands on inferred nonlinearity, not on observed phases.** -/
theorem detection_verdicts :
    survives .detectionArtefact .C4_twoPhases = true ∧
    survives .detectionArtefact .C5_trendIsComposition = true ∧
    survives .detectionArtefact .C6_deathOrganises = true := by decide

/-- Without the sampled review, C1 (the field conflates terms) would rest on vocabulary alone
    and fall to the representativeness critique; the review is what keeps it standing. -/
theorem review_rescues_C1 :
    survives .unrepresentative .C1_termsConflated = true ∧
    ([Support.authorsVocabulary].any (fun s => !hits .unrepresentative s)) = false := by decide

/-- C7 (the discontinuous cluster reflects biology) is correctly stated in the text as a
    hypothesis: it inherits the taxonomy's vulnerability. -/
theorem C7_is_only_a_hypothesis : survives .circularity .C7_clusteringMeaning = false := by decide

/-! ## Part III — empirical premises (not provable here; stated so they are visible) -/

/-- Observed in *Drosophila*: a per-individual assay assigns each animal to phase 1 or 2
    independently of chronological age [22]; confirmed across omics, behaviour, tissues and
    organisms [23–25, 32]. This is the premise C4 rests on. -/
axiom P_smurf_observed : Prop

/-- The Smurf phases are *qualitatively* distinct (coordinated multi-level change, short
    age-independent remaining lifespan), not only two readings of one threshold. Needed for
    "discontinuity" in the strong sense; Theorem C shows the readout alone cannot give it. -/
axiom P_phases_qualitative : Prop

/-- Carbonneau-type null models concern structure recovered by detection algorithms from
    high-dimensional population data [84, 87]. -/
axiom P_artefact_scope : Prop

/-- Table 2 categories are assigned from the authors' own descriptions (conceded to R2). -/
axiom P_taxonomy_from_vocabulary : Prop

/-- The abstract's "to date the only framework in which two physiologically distinct phases have
    been directly observed at the individual level". CONTESTED: the text itself cites medfly
    waiting/reproductive modes between which "individuals were observed to switch" [58]; the
    sampled review also finds machine-scored individual states in isogenic C. elegans
    (PMID 22610697). What the review supports is narrower: the only per-individual phase marker
    *that predicts death*. -/
axiom P_uniqueness_CONTESTED : Prop

end Geromed
