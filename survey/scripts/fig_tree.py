"""Figure 2: decision tree for classifying a study's claim about the trajectory of ageing,
populated with the coded abstracts of the sampled survey (both random samples pooled)."""
from paths import DATA, FIG  # noqa: E402
import csv, collections
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from style import FRAME_COLORS, INK, MUTED

A = list(csv.DictReader(open(str(DATA / "codes_A.tsv")), delimiter="\t"))
B = list(csv.DictReader(open(str(DATA / "codes_B.tsv")), delimiter="\t"))
claims = [r for r in A if r["T"] in ("P", "NC", "D")] + [r for r in B if r["relevant"] == "yes"]
n_all = len(A) + len(B)
n_none = n_all - len(claims)
n_dev = sum(r["T"] == "DEV" for r in A)
T = collections.Counter(r["T"] for r in claims)
NC = [r for r in claims if r["T"] == "NC"]
D = [r for r in claims if r["T"] == "D"]
organismal = [r for r in D if r["L"] in ("whole-organism", "physiological-functional")]
local = [r for r in D if r not in organismal]
org_obs = [r for r in organismal if r["O"] == "observed" and r["S"] == "individual"]
org_inf = [r for r in organismal if r not in org_obs]
nc_inf = sum(r["O"] == "inferred" for r in NC)
nc_age = sum(r["A"] == "chronological age" for r in NC)

fig, ax = plt.subplots(figsize=(7.4, 9.0))
ax.set_xlim(-0.1, 10.2); ax.set_ylim(0, 12.4); ax.axis("off")
LIGHT_GREEN = "#a9e3cc"


def box(x, y, w, h, text, fc="#ffffff", ec=MUTED, lw=1.0, bold=False, size=8.0):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=fc, ec=ec, lw=lw))
    ax.text(x, y, text, ha="center", va="center", fontsize=size, color=INK,
            fontweight="bold" if bold else "normal", linespacing=1.3)


def leaf(x, y, w, h, title, n, detail, col):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc="#ffffff", ec=col, lw=2.2))
    ax.text(x - w / 2 + 0.16, y + h / 2 - 0.16, title, ha="left", va="top", fontsize=8.0, fontweight="bold", color=INK)
    ax.text(x - w / 2 + 0.16, y + h / 2 - 0.50, f"n = {n}", ha="left", va="top", fontsize=8.0, fontweight="bold", color=INK)
    ax.text(x - w / 2 + 0.16, y + h / 2 - 0.86, detail, ha="left", va="top", fontsize=6.5, color=MUTED, linespacing=1.3)


def arrow(x1, y1, x2, y2, label=None, lx=None, ly=None, ha="left"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.1, shrinkA=0, shrinkB=0))
    if label:
        ax.text(lx, ly, label, fontsize=7.6, color=INK, fontweight="bold", ha=ha, va="center")


QX, QW, QH = 2.45, 4.75, 0.95
LX, LW = 7.8, 4.6
L0 = LX - LW / 2
def exit_right(y, label, h):
    arrow(QX + QW / 2, y, L0, y, label, lx=(QX + QW / 2 + L0) / 2, ly=y + 0.17, ha="center")

box(QX, 11.85, QW + 0.5, 0.8, f"{n_all} abstracts on ageing, coded with a fixed codebook\n"
    f"(representative sample, {len(A)}; vocabulary sample, {len(B)})", fc="#f3f2ee", size=7.0)
arrow(QX, 11.45, QX, 10.97)
box(QX, 10.5, QW, QH, "Q1. Does the study make a claim\nabout the shape of an ageing trajectory?", bold=True)
exit_right(10.5, "no", 1.3)
leaf(LX, 10.5, LW, 1.35, "No claim about shape", n_none,
     f"young-vs-old contrasts, mechanisms,\nage as a covariate ({n_dev} on development)", FRAME_COLORS["U"])
arrow(QX, 10.02, QX, 9.32, f"yes  (n = {len(claims)})", lx=QX + 0.12, ly=9.67)
box(QX, 8.85, QW, QH, "Q2. Is the rate of change constant\n(steady, gradual decline or increase)?", bold=True)
exit_right(8.85, "yes", 1.3)
leaf(LX, 8.85, LW, 1.35, "Progressive, continuous", T["P"],
     "the classical definitions of ageing (Table 1);\nmostly asserted rather than tested", FRAME_COLORS["P"])
arrow(QX, 8.37, QX, 7.67, f"no  (n = {T['NC'] + T['D']})", lx=QX + 0.12, ly=8.02)
box(QX, 7.2, QW, QH, "Q3. Does the system pass between\nqualitatively distinct states?", bold=True)
exit_right(7.2, "no", 1.5)
leaf(LX, 7.2, LW, 1.5, "Nonlinear, continuous", T["NC"],
     f"accelerations, plateaus, waves; {nc_inf} of {len(NC)} inferred\nstatistically, {nc_age} anchored to chronological age\n"
     "Table 2: [35, 36, 39, 40, 43, 44]", FRAME_COLORS["NC"])
arrow(QX, 6.72, QX, 6.02, f"yes  (n = {len(D)})", lx=QX + 0.12, ly=6.37)
box(QX, 5.55, QW, QH, "Q4. Is the transition a property\nof the whole organism?", bold=True)
exit_right(5.55, "no", 1.5)
leaf(LX, 5.55, LW, 1.5, "Local discontinuity (intermediate)", len(local),
     "a cell type, tissue or organ changes state;\norganismal discontinuity remains an inference\nTable 2: [37, 42]",
     LIGHT_GREEN)
arrow(QX, 5.07, QX, 4.37, f"yes  (n = {len(organismal)})", lx=QX + 0.12, ly=4.72)
box(QX, 3.9, QW, QH, "Q5. Is each individual's phase measured,\nor inferred from population-level data?", bold=True)
arrow(QX - 1.2, 3.42, QX - 1.2, 2.72, "inferred", lx=QX - 1.08, ly=3.07)
arrow(QX + 1.2, 3.42, QX + 3.35, 2.72, "measured", lx=QX + 2.35, ly=3.2)
leaf(1.55, 1.85, 3.0, 1.7, "Discontinuous, inferred", len(org_inf),
     "change points, pseudotime,\nnetwork early-warning signals\nTable 2: [33, 34, 38, 41, 45]", FRAME_COLORS["D"])
leaf(6.55, 1.85, 5.9, 1.7, "Discontinuous, measured in each individual", len(org_obs),
     "per-individual state markers (e.g. morphological states in worms);\nin the sample, none is a phase marker that predicts death,\n"
     "which the Smurf assay provides: two-phase model [22, 32]", FRAME_COLORS["D"])
ax.text(0.0, 0.55, "Counts: coded titles and abstracts from both random samples of the survey (Section 2.1), pooled; Table 2 references "
        "show where\nthe studies analysed here fall. For any nonlinear or discontinuous claim, also record what anchors the "
        "change (age, death,\ndisease or physiological state) and whether it is reversible.", fontsize=6.7, color=MUTED, va="center")
plt.savefig(str(FIG / "Fig_tree.pdf"), bbox_inches="tight"); plt.savefig(str(FIG / "Fig_tree.png"), dpi=220, bbox_inches="tight")
print(n_all, n_none, len(claims), dict(T), len(local), len(organismal), len(org_obs), len(org_inf), nc_inf, nc_age)
