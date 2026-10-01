"""Paths and loaders. The Opus codes (../data/codes_*.tsv) are read only by notebooks 01, 04 and 06."""
import hashlib
import json
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent
FROZEN = ROOT / "data/frozen"
CODING = ROOT / "data/coding"
DERIVED = ROOT / "data/derived"
TABLES = ROOT / "outputs/tables"
FIGURES = ROOT / "outputs/figures"

OPUS_MAP = {"relevant": "screen_relevant", "T": "trajectory_code", "E": "explicitness", "L": "level",
            "S": "scale", "O": "observation", "A": "anchor", "R": "reversibility"}


def settings() -> dict:
    return yaml.safe_load((ROOT / "config/settings.yaml").read_text())


def source(key: str) -> Path:
    return (ROOT / settings()["source"][key]).resolve()


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_sample_records() -> pd.DataFrame:
    rows = [r for recs in json.loads(source("sample_json").read_text()).values() for r in recs]
    df = pd.DataFrame(rows)[["arm", "stratum", "pmid", "year", "journal", "title", "abstract"]]
    df["pmid"] = df["pmid"].astype(str)
    return df


def load_opus_codes(dedupe: bool = True) -> pd.DataFrame:
    parts = []
    for arm in ["A", "B"]:
        d = pd.read_csv(source(f"opus_codes_{arm}"), sep="\t", dtype=str, keep_default_na=False)
        d.insert(0, "arm", arm)
        parts.append(d)
    d = pd.concat(parts, ignore_index=True).rename(columns=OPUS_MAP)
    if dedupe:
        d = d.drop_duplicates(["arm", "pmid"], keep="first")  # see within_arm_duplicates_dropped.tsv
    for c in d.columns:
        d[c] = d[c].replace("-", "")
    return d


def load_coder_sheet(path: Path | None = None) -> pd.DataFrame:
    """Prefer the xlsx the coder edits; fall back to the tsv."""
    if path is None:
        xlsx, tsv = CODING / "coding_sheet.xlsx", CODING / "coding_sheet.tsv"
        path = xlsx if xlsx.exists() else tsv
    path = Path(path)
    if path.suffix == ".xlsx":
        df = pd.read_excel(path, sheet_name="coding", dtype=str, keep_default_na=False)
    else:
        df = pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)
    return df.apply(lambda c: c.str.strip())
