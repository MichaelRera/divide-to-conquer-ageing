"""Shared figure style: one colour per framing, used identically in every figure."""
import matplotlib as mpl

FRAME_COLORS = {"P": "#2a78d6", "NC": "#eb6834", "D": "#1baf7a", "U": "#d9d8d4", "DEV": "#efeeea"}
FRAME_LABELS = {"P": "Progressive / continuous", "NC": "Nonlinear, continuous", "D": "Discontinuous",
                "U": "Shape not addressed", "DEV": "Development, not senescence"}
INK, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#e6e5e1", "#ffffff"

mpl.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "legend.frameon": False, "pdf.fonttype": 42,
})


def wilson(k, n, z=1.96):
    if n == 0:
        return (0, 0, 0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return p, max(0, c - h), min(1, c + h)
