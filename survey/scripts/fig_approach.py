"""Supplementary figure: study design (PRISMA-style flow). Counts are read from the data files when present."""
from paths import DATA, FIG  # noqa: E402
import json, os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

INK, MUTED, LINE = "#1f2328", "#57606a", "#8c959f"
FILL = {"pop": "#eef2f6", "A": "#e3eefb", "B": "#fbeede", "C": "#e6f4ea", "V": "#f1e8f8", "out": "#ffffff"}


def n_or(path, fn, default):
    try:
        return fn(json.load(open(path))) if os.path.exists(path) else default
    except Exception:
        return default


samp = n_or(str(DATA / "sample.json"), lambda d: d, {})
nA = sum(len(v) for k, v in samp.items() if k.startswith("A_")) or 350
nB = sum(len(v) for k, v in samp.items() if k.startswith("B_")) or 400
codesB = [l.split("\t") for l in open(str(DATA / "codes_B.tsv")).read().splitlines()[1:]] if os.path.exists(str(DATA / "codes_B.tsv")) else []
nB_rel = sum(1 for c in codesB if c[1] == "yes") if codesB else None
nW = n_or(str(DATA / "corpus_works.json"), len, 4326)
nE = sum(1 for _ in open(str(DATA / "edges.tsv"))) if os.path.exists(str(DATA / "edges.tsv")) else 3850

fig, ax = plt.subplots(figsize=(14, 8))
ax.set_xlim(0, 110); ax.set_ylim(0, 72); ax.axis("off")


def box(x, y, w, h, text, kind, bold_first=True, size=8.0):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.2",
                                fc=FILL[kind], ec=LINE, lw=0.9))
    lines = text.split("\n")
    ax.text(x + w / 2, y + h - 1.6, lines[0], ha="center", va="top", fontsize=size + 0.4,
            fontweight="bold" if bold_first else "normal", color=INK)
    ax.text(x + w / 2, y + h - 4.6, "\n".join(lines[1:]), ha="center", va="top", fontsize=size,
            color=MUTED, linespacing=1.35)


def arrow(x0, y0, x1, y1):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>", color=LINE, lw=1.0, shrinkA=0, shrinkB=0))


box(30, 60, 50, 10.5, 'Population: PubMed, "Aging" as MeSH major topic\nEnglish, 1990–2025 · N = 139,501 records\n(indexing by NLM, not by the authors)', "pop")

# four arms
cols = [(1, "A"), (28.5, "B"), (56, "C"), (83.5, "V")]
titles = {
    "A": f"Arm A · representative sample\nStratified random draw,\n50 per 5-year bin (7 bins)\nn = {nA} abstracts",
    "B": f"Arm B · targeted sample\nQuery: population AND\ntrajectory-shape terms (N = 4,318)\n100 per decade · {nB} draws (398 distinct)",
    "C": f"Arm C · citation network\nFull Arm B corpus + 20 seed papers\n(Table 2, Smurf chain) via OpenAlex\n{nW:,} works · {nE:,} citation links",
    "V": "Vocabulary timeline\nYearly share of papers using each\nof 8 trajectory-vocabulary families\n(counts over the whole population)",
}
for x, k in cols:
    arrow(55, 60, x + 12.75, 50.5)
    box(x, 38, 25.5, 12, titles[k], k)

steps = {
    "A": "Coding (single codebook)\nFraming: progressive · nonlinear-\ncontinuous · discontinuous ·\nunspecified; explicit vs implicit",
    "B": "Screening → coding\nRelevant = claims a trajectory shape"
         + (f"\n(n relevant = {nB_rel})" if nB_rel is not None else "\n(n relevant: after screening)")
         + "\nsame codebook + level, scale,\nobserved/inferred, anchor, reversibility",
    "C": "Network analysis\nLouvain communities; position of\nthe manuscript's papers; do\ndiscontinuity papers cite each other?",
    "V": "Density per 1,000 ageing papers\n3-year moving average",
}
outs = {
    "A": "How ageing is framed across\nthe literature, 1990–2025\n(Figure 3)",
    "B": "What 'nonlinear' and 'discontinuous'\nactually mean, by level and\nkind of evidence (Section 2.1)",
    "C": "Communities of trajectory\nresearch and where the\nmanuscript sits (Fig. S2)",
    "V": "When each vocabulary\nentered the field\n(Fig. S3)",
}
for x, k in cols:
    arrow(x + 12.75, 38, x + 12.75, 33.5)
    box(x, 19, 25.5, 14.5, steps[k], "out")
    arrow(x + 12.75, 19, x + 12.75, 15.5)
    box(x, 3, 25.5, 12.5, "Output\n" + outs[k], k)

ax.text(1, 2.2, "Coding: title and abstract, written codebook fixed before reading (Claude Opus); every record re-coded blind by two other\n"
        "language models (Gemini, Perplexity; Cohen's κ). Protocol, PMIDs, the three codings and scripts in the supplementary data.",
        fontsize=7.4, color=MUTED, ha="left", va="top")
plt.savefig(str(FIG / "FigS_approach.pdf"), bbox_inches="tight"); plt.savefig(str(FIG / "FigS_approach.png"), dpi=300, bbox_inches="tight")
print("saved")
