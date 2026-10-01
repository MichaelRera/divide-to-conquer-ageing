"""Yearly density of trajectory vocabulary in the ageing literature (PubMed, "Aging"[Majr], 1990-2025)."""
from paths import DATA, FIG  # noqa: E402
import json
import sample

FAMILIES = {
    "Progressive / gradual decline": '("progressive decline"[tiab] OR "gradual decline"[tiab] OR "progressive loss"[tiab] OR "gradual loss"[tiab] OR "progressive deterioration"[tiab] OR "gradual deterioration"[tiab])',
    "Nonlinear": '(nonlinear[tiab] OR non-linear[tiab])',
    "Accelerated ageing": '("accelerated aging"[tiab] OR "accelerated ageing"[tiab] OR "age acceleration"[tiab])',
    "Discontinuity": '(discontinuous[tiab] OR discontinuity[tiab] OR discontinuities[tiab])',
    "Phases / stages / biphasic": '(biphasic[tiab] OR "two-phase"[tiab] OR "two phase"[tiab] OR "two phases"[tiab] OR "phases of aging"[tiab] OR "phases of ageing"[tiab] OR "stages of aging"[tiab] OR "stages of ageing"[tiab] OR "phase transition"[tiab])',
    "Tipping points / critical transitions": '("tipping point"[tiab] OR "tipping points"[tiab] OR "critical transition"[tiab] OR "critical transitions"[tiab] OR "early warning signal"[tiab] OR "early warning signals"[tiab] OR bifurcation[tiab])',
    "Switches / waves / breakpoints": '("switch-like"[tiab] OR "waves of"[tiab] OR "inflection point"[tiab] OR breakpoint[tiab] OR breakpoints[tiab] OR "change point"[tiab] OR changepoint[tiab] OR "midlife switch"[tiab])',
    "Terminal decline": '("terminal decline"[tiab] OR "terminal phase"[tiab])',
}


def main():
    out = {"total": {}}
    for y in range(1990, 2026):
        d = (f"{y}/01/01", f"{y}/12/31")
        out["total"][y] = sample.search(sample.POP, *d)[0]
        for fam, q in FAMILIES.items():
            out.setdefault(fam, {})[y] = sample.search(f"{sample.POP} AND {q}", *d)[0]
        print(y, out["total"][y], flush=True)
    json.dump(out, open(str(DATA / "vocab_counts.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
