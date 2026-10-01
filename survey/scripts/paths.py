"""Folder layout of the survey (see ../README.md). Scripts live in scripts/, inputs and results in data/, figures in figures/."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FIG = ROOT / "figures"
CONFIG = ROOT / "config"
