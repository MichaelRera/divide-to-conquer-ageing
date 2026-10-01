"""Codebook and validation rules (PROTOCOL.md, including every change-log rule)."""
import pandas as pd

CODEBOOK = {
    "screen_relevant": ["yes", "no"],
    "trajectory_code": ["P", "NC", "D", "U", "DEV"],
    "explicitness": ["explicit", "implicit"],
    "level": ["molecular", "cellular", "tissue-organ", "physiological-functional",
              "whole-organism", "population-demographic"],
    "scale": ["individual", "population"],
    "observation": ["observed", "inferred"],
    "anchor": ["chronological age", "proximity to death", "disease or pathology",
               "physiological state", "none stated"],
    "reversibility": ["irreversible stated", "reversible stated", "not stated"],
    "organism": ["human", "mouse-rat", "Drosophila", "C. elegans", "other", "multiple", "none"],
}

RULES = [
    "DEV replaces U for pre-adult development/maturation papers (neonates, postnatal development).",
    "A plain young-vs-old comparison with no trajectory language is U.",
    "Wording such as 'declines/increases with (advancing) age', 'age-related reduction/accumulation', "
    "or 'ageing leads to reduced X' is P implicit. A bare between-group difference with no such attribution stays U.",
    "E = explicit only when the study measures or formally models the trajectory (three or more ages, "
    "or continuous age) or the paper's own claim is about the shape. A background adjective "
    "('the progressive loss of...') is implicit.",
    "A change of slope anchored to an event (death, diagnosis) is NC, even when the authors call it a "
    "'transition', 'inflection point' or 'terminal decline'. D requires qualitatively distinct states "
    "(a new state or phase, not only a faster rate).",
    "Arm B: screen first. Relevant only if the abstract claims something about the shape of an ageing "
    "trajectory (organism, organ, function or molecular layer, over age or the life course). "
    "If not relevant, leave every other code field empty (organism may still be filled).",
    "Arm B: record the authors' own shape vocabulary in notes as [authors: \"...\"] when it differs from your code.",
]

CODE_FIELDS = ["screen_relevant", "trajectory_code", "explicitness", "level", "scale", "observation",
               "anchor", "reversibility", "meaning", "organism"]
SHEET_COLUMNS = (["review_id", "priority_10pct", "arm", "stratum", "pmid", "year", "journal", "title", "abstract"]
                 + CODE_FIELDS + ["evidence_quote", "notes", "coder_id", "coding_date"])

SHAPED = {"P", "NC", "D"}
DETAIL = {"NC", "D"}


def blank(x) -> bool:
    return pd.isna(x) or str(x).strip() in {"", "-"}


def is_coded(row) -> bool:
    """A row counts as coded once the coder has made the decision that row requires."""
    if row["arm"] == "B":
        return not blank(row["screen_relevant"])
    return not blank(row["trajectory_code"])


def blocking(errors: list[str]) -> list[str]:
    return [e for e in errors if not e.startswith("warning: ")]


def validation_errors(row) -> list[str]:
    errors = []
    for field, allowed in CODEBOOK.items():
        if not blank(row.get(field)) and str(row[field]).strip() not in allowed:
            errors.append(f"{field}: '{row[field]}' not in codebook")
    if row["arm"] == "B":
        rel = str(row["screen_relevant"]).strip()
        if rel == "no":
            for f in CODE_FIELDS[1:-1]:  # everything except screen_relevant and organism
                if not blank(row[f]):
                    errors.append(f"irrelevant Arm B record has {f}")
            return errors
        if rel == "yes" and blank(row["trajectory_code"]):
            errors.append("relevant Arm B record needs trajectory_code")
            return errors
    elif not blank(row["screen_relevant"]):
        errors.append("screen_relevant must be empty in Arm A")
    t = str(row["trajectory_code"]).strip()
    if blank(t):
        return errors
    if row["arm"] == "B" and t == "U":
        errors.append("relevant Arm B record coded U (should it be screened out?)")
    if t in SHAPED and blank(row["explicitness"]):
        errors.append("explicitness required for P/NC/D")
    if t not in SHAPED and not blank(row["explicitness"]):
        errors.append("explicitness must be empty for U/DEV")
    for f in ["level", "scale", "observation", "anchor"]:
        if t in DETAIL and blank(row[f]):
            # the trajectory code stays usable; detail kappas use only records where both coders filled f
            errors.append(f"warning: {f} required for NC/D")
        if t not in DETAIL and not blank(row[f]):
            # both coders sometimes add detail to P records; ignored by kappa, so logged but not blocking
            errors.append(("warning: " if t == "P" else "") + f"{f} must be empty outside NC/D")
    for f in ["reversibility", "meaning"]:
        if t == "D" and blank(row[f]):
            errors.append(f"{f} required for D")
        if t != "D" and not blank(row[f]):
            errors.append(f"{f} must be empty outside D")
    if blank(row["organism"]):
        errors.append("organism required")
    return errors
