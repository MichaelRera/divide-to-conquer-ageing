"""Wilson intervals and Cohen's kappa (numpy only, so no statsmodels/sklearn dependency)."""
import numpy as np
import pandas as pd

Z95 = 1.959963984540054


def wilson(k: int, n: int, z: float = Z95) -> dict:
    if n == 0:
        return {"n": 0, "count": int(k), "proportion": np.nan, "ci_low": np.nan, "ci_high": np.nan}
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return {"n": int(n), "count": int(k), "proportion": p, "ci_low": centre - half, "ci_high": centre + half}


def distribution(values: pd.Series, levels: list[str]) -> pd.DataFrame:
    n = len(values)
    return pd.DataFrame([{"level": lv} | wilson(int((values == lv).sum()), n) for lv in levels])


def cohen_kappa(x, y, labels=None) -> float:
    x, y = np.asarray(x, dtype=object), np.asarray(y, dtype=object)
    labels = sorted(set(x) | set(y)) if labels is None else list(labels)
    idx = {lab: i for i, lab in enumerate(labels)}
    m = np.zeros((len(labels), len(labels)))
    for a, b in zip(x, y):
        m[idx[a], idx[b]] += 1
    n = m.sum()
    if n == 0:
        return np.nan
    po = np.trace(m) / n
    pe = (m.sum(0) * m.sum(1)).sum() / n ** 2
    return np.nan if pe == 1 else (po - pe) / (1 - pe)  # a single category in both: kappa undefined


def kappa_summary(x, y, labels=None, reps: int = 2000, seed: int = 20260925) -> dict:
    """Agreement, kappa, and a percentile bootstrap CI resampling records (not labels)."""
    x, y = np.asarray(x, dtype=object), np.asarray(y, dtype=object)
    n = len(x)
    out = {"n": n, "percent_agreement": float((x == y).mean()) if n else np.nan,
           "cohen_kappa": cohen_kappa(x, y, labels), "kappa_ci_low": np.nan, "kappa_ci_high": np.nan}
    if n >= 20 and reps:
        rng = np.random.default_rng(seed)
        boots = [cohen_kappa(x[i], y[i], labels) for i in (rng.integers(0, n, n) for _ in range(reps))]
        boots = np.array([b for b in boots if not np.isnan(b)])
        if len(boots) >= 0.9 * reps:  # otherwise too many resamples are degenerate for a CI
            out["kappa_ci_low"], out["kappa_ci_high"] = np.percentile(boots, [2.5, 97.5])
    return out


def landis_koch(k: float) -> str:
    if np.isnan(k):
        return ""
    for cut, word in [(0, "poor"), (0.2, "slight"), (0.4, "fair"), (0.6, "moderate"), (0.8, "substantial")]:
        if k <= cut:
            return word
    return "almost perfect"
