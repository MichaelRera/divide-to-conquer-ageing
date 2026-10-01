"""Agreement among Opus 5.5 (original coder), Perplexity and Gemini, all blind to each other.

    python3 three_coders.py "<Gemini model name>"

Inputs: the coding sheet (Perplexity codes, imported by perplexity_batches.py) and LLM_valid/gemini/*_coded*.txt.
Outputs in outputs/tables/:
  kappa_three_coders.tsv          pairwise kappa, planned 10% subset and all records coded by all three
  gemini_intra_rater.tsv          Gemini's agreement with itself on records it coded in two chats
  distributions_three_coders.tsv  P/NC/D/U/DEV (Arm A) and screen, NC/D (Arm B) per coder, Wilson CIs
  majority_three_coders.tsv       per record: three codes, majority, who is in the minority
  D_records_three_coders.tsv      every record that any coder called D, with the three codes
"""
import itertools
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from io_utils import ROOT, TABLES, load_coder_sheet, load_opus_codes, settings  # noqa: E402
from coding_schema import blocking, is_coded, validation_errors  # noqa: E402
from stats_utils import distribution, kappa_summary, landis_koch  # noqa: E402
from perplexity_batches import read_returned  # noqa: E402

model = sys.argv[1] if len(sys.argv) > 1 else "model not recorded"
GEM = f"Gemini {model}"
S = settings()


def batch_no(name: str) -> int:
    return int(re.search(r"batch_(\d+)", name).group(1))


# --- Gemini codes. A record returned by two chats keeps the code from its own batch's chat.
batches = {int(f.stem[-2:]): {l[4:8] for l in f.read_text().splitlines() if l.startswith("### ")}
           for f in (ROOT / "LLM_valid/batches").glob("batch_*.txt")}
files = sorted((ROOT / "LLM_valid/gemini").glob("*_coded*.txt"))
gem_all = pd.concat([read_returned(f).assign(_batch=batch_no(f.name)) for f in files], ignore_index=True)
gem_all["own_batch"] = [rid in batches[b] for rid, b in zip(gem_all.review_id, gem_all._batch)]
gem = gem_all[gem_all.own_batch].drop_duplicates("review_id")
extra = gem_all[~gem_all.own_batch]

sheet = load_coder_sheet()
meta = sheet[["review_id", "arm", "pmid", "priority_10pct"]]
gem = gem.merge(meta, on="review_id", how="left")
assert gem.pmid.notna().all(), "unknown review_id in Gemini output"
errs = [validation_errors(r) for _, r in gem.iterrows()]
n_block = sum(bool(blocking(e)) for e in errs)
print(f"Gemini: {len(gem)} records ({len(files)} files); blocking errors {n_block}; "
      f"warnings only {sum(bool(e) for e in errs) - n_block}; coded twice {len(extra)}")
gem.assign(coder_id=GEM).to_csv(TABLES / "gemini_codes.tsv", sep="\t", index=False)

ppx = sheet[[is_coded(r) for _, r in sheet.iterrows()]]
opus = load_opus_codes().merge(meta, on=["arm", "pmid"])
coders = {"Opus 5.5": opus, "Perplexity": ppx, GEM: gem}


def T_all(df):  # Arm B not-relevant becomes its own category
    return df.trajectory_code.where(df.screen_relevant != "no", "not relevant")


# --- Gemini intra-rater (same model, two chats)
twice = extra.merge(gem[["review_id", "screen_relevant", "trajectory_code"]], on="review_id", suffixes=("_a", "_b"))
ta = twice.trajectory_code_a.where(twice.screen_relevant_a != "no", "not relevant")
tb = twice.trajectory_code_b.where(twice.screen_relevant_b != "no", "not relevant")
intra = kappa_summary(ta.values, tb.values, reps=S["bootstrap_reps"], seed=S["bootstrap_seed"])
pd.DataFrame([{"comparison": "T, Gemini chat A vs chat B"} | intra]).to_csv(TABLES / "gemini_intra_rater.tsv", sep="\t", index=False)
print(f"Gemini intra-rater on {intra['n']} records: agreement {intra['percent_agreement']:.2f}, kappa {intra['cohen_kappa']:.2f}")

# --- pairwise kappa
common = sorted(set.intersection(*(set(d.review_id) for d in coders.values())))
view = {k: d.set_index("review_id").loc[common] for k, d in coders.items()}
prio = view["Opus 5.5"].priority_10pct == "1"
rows = []
for subset, mask in {"planned 10% subset": prio, "all coded by all three": prio | ~prio}.items():
    for a, b in itertools.combinations(coders, 2):
        x, y = view[a][mask], view[b][mask]
        B = x.arm == "B"
        tests = {"T, both arms (Arm B not-relevant as a category)": (T_all(x), T_all(y)),
                 "T, Arm A": (x.trajectory_code[~B], y.trajectory_code[~B]),
                 "Arm B relevance screen": (x.screen_relevant[B], y.screen_relevant[B]),
                 "D vs not-D, both arms": (T_all(x) == "D", T_all(y) == "D")}
        for name, (u, v) in tests.items():
            r = kappa_summary(u.astype(str).values, v.astype(str).values, reps=S["bootstrap_reps"], seed=S["bootstrap_seed"])
            rows.append({"subset": subset, "pair": f"{a} vs {b}", "comparison": name} | r
                        | {"interpretation": landis_koch(r["cohen_kappa"])})
kap = pd.DataFrame(rows)
kap.to_csv(TABLES / "kappa_three_coders.tsv", sep="\t", index=False)

# --- distributions per coder
dist = []
for k, v in view.items():
    A, B = v[v.arm == "A"], v[v.arm == "B"]
    for label, vals, levels in [("A: all", A.trajectory_code, ["P", "NC", "D", "U", "DEV"]),
                                ("B: screen", B.screen_relevant, ["yes", "no"]),
                                ("B: relevant (own screen)", B.trajectory_code[B.screen_relevant == "yes"], ["P", "NC", "D"])]:
        d = distribution(vals, levels)
        d.insert(0, "coder", k); d.insert(0, "table", label)
        dist.append(d)
dist = pd.concat(dist, ignore_index=True)
dist["cell"] = [f"{c}/{n} ({100 * p:.1f}%; {100 * lo:.1f}-{100 * hi:.1f})"
                for c, n, p, lo, hi in dist[["count", "n", "proportion", "ci_low", "ci_high"]].itertuples(index=False)]
dist.to_csv(TABLES / "distributions_three_coders.tsv", sep="\t", index=False)

# --- majority vote per record
T = pd.DataFrame({k: T_all(v) for k, v in view.items()})
maj = T.mode(axis=1)
T["majority"] = [m[0] if (T.loc[i, list(coders)] == m[0]).sum() >= 2 else "none (3-way split)"
                 for i, m in zip(T.index, maj.itertuples(index=False))]
for k in coders:
    T[f"{k} in minority"] = (T.majority != "none (3-way split)") & (T[k] != T.majority)
T = T.join(view["Opus 5.5"][["arm", "pmid"]])
T.to_csv(TABLES / "majority_three_coders.tsv", sep="\t")
anyD = T[(T[list(coders)] == "D").any(axis=1)].join(sheet.set_index("review_id")[["title"]])
anyD.to_csv(TABLES / "D_records_three_coders.tsv", sep="\t")

pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 70)
print(kap.round(2).drop(columns=["kappa_ci_low", "kappa_ci_high"]).assign(
    ci=[f"{a:.2f}-{b:.2f}" for a, b in zip(kap.kappa_ci_low, kap.kappa_ci_high)]).to_string(index=False))
print(dist.pivot_table(index=["table", "level"], columns="coder", values="cell", aggfunc="first", sort=False).to_string())
print("\nrecords where each coder is the odd one out (of", len(T), "):")
print(T[[f"{k} in minority" for k in coders]].sum().to_string())
print("3-way splits:", int((T.majority == "none (3-way split)").sum()))
print(f"\nrecords any coder called D: {len(anyD)}; majority D: {int((anyD.majority == 'D').sum())}")
print(anyD[list(coders) + ["majority", "title"]].to_string())
