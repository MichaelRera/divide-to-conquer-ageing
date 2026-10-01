"""Response Figure R2: logical structure of the argument, as checked in Lean (DivideToConquer.lean).
Left: the literature map (rests on authors' descriptions and the sampled survey).
Centre: definitions and theorems. Right: the two-phase model (rests on per-individual measurement).
Nothing in the centre or on the right depends on anything left of the dashed line (separation theorem)."""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

INK, MUTED = "#0b0b0b", "#52514e"
C_VOC, C_SURV, C_FORM, C_EMP = "#eb6834", "#2a78d6", "#7a5bc7", "#1baf7a"
OK, KO = "#14895f", "#c62f2f"

fig, ax = plt.subplots(figsize=(11.5, 6.6))
ax.set_xlim(-0.1, 18.5); ax.set_ylim(0, 9.4); ax.axis("off")
B = {}


def node(k, x, y, text, col, w=2.5, h=1.0, fill="#ffffff", lw=1.8, size=6.9, bold=False, verdict=None, vcol=None):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=fill, ec=col, lw=lw))
    ty = y + (0.17 if verdict else 0)
    ax.text(x, ty, text, ha="center", va="center", fontsize=size, color=INK, linespacing=1.25,
            fontweight="bold" if bold else "normal")
    if verdict:
        ax.text(x, y - h / 2 + 0.1, verdict, ha="center", va="bottom", fontsize=6.2, color=vcol, fontweight="bold",
                linespacing=1.15)
    B[k] = (x, y, w, h)


def P(k, side, f=0.5):
    x, y, w, h = B[k]
    return {"top": (x - w / 2 + f * w, y + h / 2), "bottom": (x - w / 2 + f * w, y - h / 2),
            "left": (x - w / 2, y - h / 2 + f * h), "right": (x + w / 2, y - h / 2 + f * h)}[side]


def arrow(p, q):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.0, shrinkA=0, shrinkB=0))


# sources (bottom row)
node("voc", 1.6, 0.8, "Authors' own descriptions\nof their data", C_VOC, w=3.0, fill="#fdf0e9")
node("surv", 4.85, 0.8, "Sampled survey of\n750 abstracts (§2.1)", C_SURV, w=3.0, fill="#eaf2fc")
node("form", 8.35, 0.8, "Definitions and Theorems A–C\n(Appendix; checked in Lean)", C_FORM, w=3.2, fill="#f2eefa")
node("smurf", 14.4, 0.8, "Smurf assay: phase measured\nin each individual [22, 32]", C_EMP, w=3.3, fill="#e8f7f1")
# literature map
node("tax", 1.6, 3.3, "Table 2: reviewed studies\nin three categories", C_VOC, w=3.0, h=1.35,
     verdict="✗ circular (R2): conceded;\na map of authors' descriptions", vcol=KO)
node("conf", 4.85, 3.3, "The field uses 'switch', 'wave',\n'phase' for different structures", C_VOC, w=3.0, h=1.35,
     verdict="✓ stands thanks to the survey", vcol=OK)
node("clus", 1.6, 5.9, "The discontinuous cluster\nreflects biphasic ageing", C_VOC, w=3.0, lw=1.2, h=1.35,
     verdict="✗ inherits that circularity:\nstated only as a hypothesis", vcol=KO)
# definitions
node("dist", 8.35, 4.6, "Nonlinearity and discontinuity\nare independent concepts", C_FORM, w=3.2, h=1.35,
     verdict="✓ Theorems A and B", vcol=OK)
node("frame", 8.35, 8.1, "A shared framework for comparing\nstructures of age-related change", INK, w=4.0,
     size=7.6, bold=True)
# two-phase model
node("phases", 14.4, 3.0, "Ageing has two observed phases\n(flies, worms, fish, mice)", C_EMP, w=3.3)
node("comp", 11.85, 5.6, "Population trends can be\nphase composition\n(Fig. 1; Fig. R1)", C_EMP, w=2.5, h=1.2)
node("death", 14.45, 5.6, "Proximity to death,\nnot age, organises\nlate-life state", C_EMP, w=2.5, h=1.2)
node("sel", 17.05, 5.6, "A two-phase life\nhistory can be\nselected [Roget 2024]", C_EMP, w=2.5, h=1.2)
ax.text(14.45, 6.45, "✓ not exposed to circularity (R2) nor to detection artefacts (R3)", ha="center", va="bottom",
        fontsize=6.6, color=OK, fontweight="bold")

arrow(P("voc", "top"), P("tax", "bottom"))
arrow(P("voc", "top", 0.85), P("conf", "bottom", 0.25))
arrow(P("surv", "top", 0.55), P("conf", "bottom", 0.6))
arrow(P("tax", "top"), P("clus", "bottom"))
arrow(P("form", "top"), P("dist", "bottom"))
arrow(P("dist", "left", 0.75), P("tax", "top", 0.9))
arrow(P("dist", "top"), P("frame", "bottom", 0.5))
arrow(P("conf", "top", 0.5), P("frame", "left", 0.3))
arrow(P("smurf", "top"), P("phases", "bottom"))
arrow(P("phases", "top", 0.2), P("comp", "bottom", 0.6))
arrow(P("phases", "top", 0.55), P("death", "bottom", 0.5))
arrow(P("phases", "top", 0.9), P("sel", "bottom", 0.35))
arrow(P("form", "right", 0.8), P("comp", "bottom", 0.2))

ax.plot([6.6, 6.6], [0.2, 6.7], color=MUTED, lw=1.0, ls=(0, (5, 3)))
ax.text(6.7, 6.7, "nothing to the right of this line\ndepends on anything to its left", fontsize=6.2,
        color=MUTED, ha="left", va="top", style="italic")
ax.text(3.2, 9.05, "The literature map (conceptual)", ha="center", fontsize=8.8, color=C_VOC, fontweight="bold")
ax.text(14.45, 9.05, "The two-phase model (empirical)", ha="center", fontsize=8.8, color=C_EMP, fontweight="bold")

plt.savefig("Fig_logic.pdf", bbox_inches="tight"); plt.savefig("Fig_logic.png", dpi=220, bbox_inches="tight")
print("ok")
