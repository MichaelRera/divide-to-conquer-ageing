"""Vocabulary-density timeline: share of ageing papers (MeSH major 'Aging') using each trajectory vocabulary."""
from paths import DATA, FIG  # noqa: E402
import json
import matplotlib.pyplot as plt
from style import INK, MUTED

d = json.load(open(str(DATA / "vocab_counts.json")))
years = sorted(int(y) for y in d["total"])
tot = [d["total"][str(y)] for y in years]
fams = [f for f in d if f != "total"]
# two groups: continuous-framing vocabulary vs. shape vocabulary; one hue per family, fixed order
colors = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]


def ma3(v):
    return [sum(v[max(0, i - 1):i + 2]) / len(v[max(0, i - 1):i + 2]) for i in range(len(v))]


fig, axes = plt.subplots(2, 4, figsize=(12, 5.2), sharex=True)
for ax, fam, col in zip(axes.flat, fams, colors):
    dens = [1000 * d[fam][str(y)] / t if t else 0 for y, t in zip(years, tot)]
    ax.plot(years, dens, color=col, lw=0.8, alpha=0.35)
    ax.plot(years, ma3(dens), color=col, lw=2)
    ax.set_title(fam, loc="left", fontsize=8.5, color=INK, fontweight="bold")
    ax.set_ylim(bottom=0)
    ax.axvspan(2022, 2025.5, color="#efeeea", zorder=0)
    first = next((y for y in years if d[fam][str(y)] > 0), None)
    ax.text(0.02, 0.9, f"total {sum(d[fam].values()):,}", transform=ax.transAxes, fontsize=7, color=MUTED)
for ax in axes[1]:
    ax.set_xticks([1990, 2000, 2010, 2020])
for ax in axes[:, 0]:
    ax.set_ylabel("per 1,000 ageing papers")
fig.suptitle("When each trajectory vocabulary entered the ageing literature (PubMed, MeSH major 'Aging', 1990–2025)",
             x=0.01, ha="left", fontsize=9.5, color=INK, fontweight="bold")
fig.text(0.01, -0.02, "Thin line: yearly density; thick line: 3-year moving average. Title/abstract matches. Shaded: 2022–2025, when NLM moved to "
         "automated MeSH indexing, so read the most recent densities with caution. Search strings in vocab.py.",
         fontsize=6.8, color=MUTED)
fig.tight_layout()
plt.savefig(str(FIG / "Fig_vocab.pdf"), bbox_inches="tight"); plt.savefig(str(FIG / "Fig_vocab.png"), dpi=200, bbox_inches="tight")
for fam in fams:
    early = sum(d[fam][str(y)] for y in range(1990, 2000)) / sum(d["total"][str(y)] for y in range(1990, 2000)) * 1000
    late = sum(d[fam][str(y)] for y in range(2015, 2026)) / sum(d["total"][str(y)] for y in range(2015, 2026)) * 1000
    print(f"{fam:40s} 1990s {early:6.2f}  2015-25 {late:6.2f}  x{late / early if early else float('nan'):.1f}")
