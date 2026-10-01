"""Arm A figure: how ageing's trajectory is framed across the literature, per 5-year bin."""
from paths import DATA, FIG  # noqa: E402
import csv, json, collections
import matplotlib.pyplot as plt
from style import FRAME_COLORS, FRAME_LABELS, INK, MUTED, wilson

codes = {r["pmid"]: r for r in csv.DictReader(open(str(DATA / "codes_A.tsv")), delimiter="\t")}
samp = json.load(open(str(DATA / "sample.json")))
bins = [k for k in samp if k.startswith("A_")]
labels = [k[2:].replace("-", "–") for k in bins]

fig, (a, b) = plt.subplots(1, 2, figsize=(10, 3.9), gridspec_kw=dict(width_ratios=[1.35, 1], wspace=0.32))

# (a) composition of senescence-relevant records per bin, 100% stacked, 2px surface gaps
order = ["P", "NC", "D", "U"]
table = []
for i, k in enumerate(bins):
    rs = [codes[r["pmid"]] for r in samp[k] if codes[r["pmid"]]["T"] != "DEV"]
    n = len(rs); cnt = collections.Counter(r["T"] for r in rs)
    table.append((k, n, cnt))
    bottom = 0
    for t in order:
        h = 100 * cnt[t] / n
        a.bar(i, h, bottom=bottom, width=0.72, color=FRAME_COLORS[t], edgecolor="white", linewidth=1.2)
        bottom += h
    a.text(i, 101.5, f"n={n}", ha="center", va="bottom", fontsize=7, color=MUTED)
a.set_xticks(range(len(bins)), [l.replace("–","–\n") for l in labels], fontsize=7.2)
a.set_ylim(0, 108); a.set_ylabel("% of senescence-relevant abstracts")
a.set_title("a  Framing of ageing's trajectory, per 5-year period", loc="left", fontsize=9, color=INK, fontweight="bold")
a.grid(axis="x", visible=False)
handles = [plt.Rectangle((0, 0), 1, 1, color=FRAME_COLORS[t]) for t in order]
a.legend(handles, [FRAME_LABELS[t] for t in order], loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=4, fontsize=7.2,
         handlelength=1, columnspacing=1.2)

# (b) among records that do frame a trajectory: share of each framing, pooled, with Wilson 95% CI
framed = [codes[r["pmid"]] for k in bins for r in samp[k] if codes[r["pmid"]]["T"] in ("P", "NC", "D")]
N = len(framed); c = collections.Counter(r["T"] for r in framed)
for j, t in enumerate(["P", "NC", "D"]):
    p, lo, hi = wilson(c[t], N)
    b.barh(2 - j, 100 * p, height=0.55, color=FRAME_COLORS[t], edgecolor="white")
    b.errorbar(100 * p, 2 - j, xerr=[[100 * (p - lo)], [100 * (hi - p)]], fmt="none", ecolor=INK, elinewidth=1, capsize=3)
    b.text(100 * hi + 2, 2 - j, f"{100 * p:.0f}%  ({c[t]}/{N})", va="center", fontsize=8, color=INK)
    ex = sum(1 for r in framed if r["T"] == t and r["E"] == "explicit")
    b.text(100 * hi + 2, 2 - j - 0.2, f"explicit: {ex} of {c[t]}", fontsize=6.8, color=MUTED, va="top")
b.set_yticks([2, 1, 0], [FRAME_LABELS[t] for t in ["P", "NC", "D"]])
b.set_xlim(0, 110); b.set_xlabel("% of abstracts that frame a trajectory (95% CI)")
b.set_title("b  When a shape is claimed, which one?", loc="left", fontsize=9, color=INK, fontweight="bold")
b.grid(axis="y", visible=False)

n_dev = sum(1 for k in bins for r in samp[k] if codes[r["pmid"]]["T"] == "DEV")
fig.text(0.01, -0.09, f"PubMed records with 'Aging' as MeSH major topic, 1990–2025; 50 drawn at random per 5-year bin (n = {sum(len(samp[k]) for k in bins)}). "
         f"{n_dev} records about pre-adult development are excluded. Coding of title and abstract with a fixed codebook (see protocol).",
         fontsize=6.8, color=MUTED)
plt.savefig(str(FIG / "Fig_armA.pdf"), bbox_inches="tight"); plt.savefig(str(FIG / "Fig_armA.png"), dpi=220, bbox_inches="tight")
with open(str(DATA / "armA_table.tsv"), "w") as f:
    f.write("bin\tn_senescence\tP\tNC\tD\tU\n")
    for k, n, cnt in table:
        f.write(f"{k}\t{n}\t{cnt['P']}\t{cnt['NC']}\t{cnt['D']}\t{cnt['U']}\n")
print("framed N", N, dict(c))
