"""Writes the notebooks from the cell sources below, so they stay reviewable as plain Python."""
from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).resolve().parent
SETUP = """import sys
from pathlib import Path
ROOT = Path.cwd().resolve().parent
sys.path.insert(0, str(ROOT / "src"))
import pandas as pd, numpy as np
pd.set_option("display.max_colwidth", 80)"""

NB = {}

NB["00_setup_and_codebook"] = [
    ("md", "# 00: Setup and codebook\nWrites the codebook and a run manifest. The codebook is PROTOCOL.md "
           "including every change-log rule; it is the only coding guidance the independent coder receives."),
    ("code", SETUP),
    ("code", """import json, platform, scipy, networkx, yaml
from io_utils import settings, DERIVED
from coding_schema import CODEBOOK, RULES
manifest = {"settings": settings(), "python": sys.version, "platform": platform.platform(),
            "pandas": pd.__version__, "numpy": np.__version__, "scipy": scipy.__version__}
(DERIVED / "codebook.json").write_text(json.dumps({"codebook": CODEBOOK, "rules": RULES}, indent=2))
(DERIVED / "run_manifest.json").write_text(json.dumps(manifest, indent=2))
for r in RULES: print("-", r)"""),
]

NB["01_freeze_existing_sample"] = [
    ("md", "# 01: Freeze the existing sample\nThe workflow's PubMed sampling step is **replaced**: the independent "
           "coder must code the same 750 records that Claude Opus 5.5 coded, otherwise no kappa can be computed. "
           "This notebook freezes that frame with content hashes and checks it against the Opus code files "
           "(same PMIDs, same order). No live query is made."),
    ("code", SETUP),
    ("code", """import json
from io_utils import load_sample_records, load_opus_codes, source, sha256, FROZEN
rec = load_sample_records()
opus = load_opus_codes(dedupe=False)
assert len(rec) == len(opus) == 750
for arm in "AB":
    assert rec.loc[rec.arm == arm, "pmid"].tolist() == opus.loc[opus.arm == arm, "pmid"].tolist(), arm
# The 2026-09-25 draw contains within-arm duplicates (same PMID drawn twice in Arm B; Opus coded both
# copies 'not relevant'). Each record is coded once here; the duplicates are logged.
dups = rec[rec.duplicated(["arm", "pmid"], keep="first")]
dups.to_csv(FROZEN / "within_arm_duplicates_dropped.tsv", sep="\t", index=False)
print("within-arm duplicates dropped:", dups[["arm", "stratum", "pmid"]].values.tolist())
rec = rec.drop(dups.index).reset_index(drop=True)
assert (rec["abstract"].str.strip() != "").all(), "records without abstract"
rec.insert(0, "review_id", [f"{a}{i:03d}" for a, i in zip(rec.arm, rec.groupby("arm").cumcount() + 1)])
rec.to_csv(FROZEN / "sample_frame.tsv", sep="\\t", index=False)
hashes = {k: sha256(source(k)) for k in ["sample_json", "opus_codes_A", "opus_codes_B", "kappa_sheet"]}
(FROZEN / "input_hashes.json").write_text(json.dumps(hashes, indent=2))
rec.groupby(["arm", "stratum"]).size()"""),
]

NB["02_prepare_coding"] = [
    ("md", "# 02: Prepare the blind coding sheet\nOne row per record, **no Opus codes, notes or vocabulary**. "
           "Rows are shuffled within arm (fixed seed) so stratum order and the original coding order are not "
           "reproduced. The 75 records of the planned 10% subset (`kappa_sheet.tsv`) are flagged "
           "`priority_10pct = 1`: a coder with limited time does those first; everything else is a bonus. "
           "The xlsx has drop-down lists for every coded field. **Never overwrites a sheet that already contains codes.**"),
    ("code", SETUP),
    ("code", """import hashlib, datetime
from io_utils import FROZEN, CODING, source, load_coder_sheet, settings
from coding_schema import SHEET_COLUMNS, CODE_FIELDS, CODEBOOK
frame = pd.read_csv(FROZEN / "sample_frame.tsv", sep="\\t", dtype=str, keep_default_na=False)
prio = set(pd.read_csv(source("kappa_sheet"), sep="\\t", dtype=str)["pmid"])
assert len(prio) == 75 and prio <= set(frame.pmid)  # 75 distinct PMIDs
frame["priority_10pct"] = frame.pmid.isin(prio).map({True: "1", False: ""})
seed = settings()["sheet_order_seed"]
frame["_k"] = [hashlib.sha256(f"{seed}-{p}".encode()).hexdigest() for p in frame.pmid]
frame = (frame.sort_values(["arm", "priority_10pct", "_k"], ascending=[True, False, True])
              .drop(columns="_k"))
for c in SHEET_COLUMNS:
    if c not in frame:
        frame[c] = ""
sheet = frame[SHEET_COLUMNS].reset_index(drop=True)
xlsx, tsv = CODING / "coding_sheet.xlsx", CODING / "coding_sheet.tsv"
if xlsx.exists() and (load_coder_sheet(xlsx)[CODE_FIELDS] != "").any().any():
    raise SystemExit("coding_sheet.xlsx already contains codes: not overwritten")
sheet.to_csv(tsv, sep="\\t", index=False)
sheet.shape, sheet.priority_10pct.eq("1").sum()"""),
    ("code", """from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter
wb = Workbook()
ws = wb.active; ws.title = "coding"
ws.append(SHEET_COLUMNS)
for row in sheet.itertuples(index=False):
    ws.append(list(row))
lists = wb.create_sheet("lists")
widths = {"title": 45, "abstract": 90, "notes": 40, "evidence_quote": 40, "meaning": 30, "journal": 20}
code_fill = PatternFill("solid", fgColor="FFF4CC")
for j, col in enumerate(SHEET_COLUMNS, 1):
    L = get_column_letter(j)
    ws.column_dimensions[L].width = widths.get(col, 14)
    ws.cell(1, j).font = Font(bold=True)
    if col in CODE_FIELDS + ["evidence_quote", "notes"]:
        ws.cell(1, j).fill = code_fill
    if col in CODEBOOK:
        k = list(CODEBOOK).index(col) + 1
        LL = get_column_letter(k)
        lists.cell(1, k, col)
        for i, v in enumerate(CODEBOOK[col], 2):
            lists.cell(i, k, v)
        dv = DataValidation(type="list", formula1=f"=lists!${LL}$2:${LL}${len(CODEBOOK[col]) + 1}", allow_blank=True)
        ws.add_data_validation(dv); dv.add(f"{L}2:{L}{len(sheet) + 1}")
for r in range(2, len(sheet) + 2):
    ws.row_dimensions[r].height = 120
    for c in (SHEET_COLUMNS.index("title") + 1, SHEET_COLUMNS.index("abstract") + 1):
        ws.cell(r, c).alignment = Alignment(wrap_text=True, vertical="top")
ws.freeze_panes = "J2"
lists.sheet_state = "hidden"
wb.save(xlsx)
print("wrote", xlsx.name, "and", tsv.name, datetime.date.today())"""),
]

NB["03_validate_coding"] = [
    ("md", "# 03: Validate the coder's sheet\nRun after every coding batch. Checks codebook values and the "
           "conditional-field rules. Downstream notebooks refuse to run while errors remain."),
    ("code", SETUP),
    ("code", """from io_utils import load_coder_sheet, FROZEN, TABLES
from coding_schema import is_coded, validation_errors, blocking
sheet = load_coder_sheet()
frame = pd.read_csv(FROZEN / "sample_frame.tsv", sep="\\t", dtype=str)
assert sheet.review_id.is_unique and set(sheet.pmid) == set(frame.pmid), "sheet rows altered"
merged = sheet.merge(frame[["review_id", "pmid"]], on="review_id", suffixes=("", "_frame"))
assert (merged.pmid == merged.pmid_frame).all(), "review_id/pmid mismatch"
sheet["coded"] = [is_coded(r) for _, r in sheet.iterrows()]
coded = sheet[sheet.coded].copy()
coded["errors"] = [validation_errors(r) for _, r in coded.iterrows()]
problems = coded[coded.errors.map(bool).astype(bool)]
n_block = int(coded.errors.map(lambda e: bool(blocking(e))).sum())
problems[["review_id", "pmid", "arm", "errors"]].to_csv(TABLES / "coding_validation_errors.tsv", sep="\\t", index=False)
print(sheet.groupby("arm").coded.agg(["sum", "size"]).rename(columns={"sum": "coded", "size": "total"}))
print("priority 10% coded:", int(sheet.loc[sheet.priority_10pct == "1", "coded"].sum()), "/ 75")
print("records with blocking errors:", n_block, "| with warnings only:", len(problems) - n_block)
problems[["review_id", "pmid", "errors"]].head(30)"""),
]

GATE = """from io_utils import load_coder_sheet, load_opus_codes, TABLES
from coding_schema import is_coded, validation_errors, blocking
coder = load_coder_sheet()
coder = coder[coder.apply(is_coded, axis=1)].copy()
assert len(coder), "nothing coded yet"
assert not any(blocking(validation_errors(r)) for _, r in coder.iterrows()), "run 03 and fix validation errors first"
opus = load_opus_codes()
both = coder.merge(opus, on=["arm", "pmid"], suffixes=("_ind", "_opus"))
assert len(both) == len(coder)
print(len(both), "records coded by both;", both.priority_10pct.eq("1").sum(), "of them in the planned 10% subset")"""

NB["04_compare_distributions"] = [
    ("md", "# 04: Distributions, independent coder vs Opus\nSame records, two coders: proportions of P/NC/D/U/DEV "
           "(Arm A) and relevance and NC/D (Arm B), with Wilson 95% CIs. If only part of the sample is coded, "
           "the Opus column is restricted to the same records."),
    ("code", SETUP),
    ("code", GATE),
    ("code", """from stats_utils import distribution
from coding_schema import CODEBOOK
rows = []
def add(label, sub, field, levels, drop=None):
    for who in ["ind", "opus"]:
        v = sub[f"{field}_{who}"]
        d = distribution(v[v != drop] if drop else v, levels)
        d.insert(0, "coder", {"ind": "independent", "opus": "Opus 5.5"}[who]); d.insert(0, "table", label)
        rows.append(d)
A = both[both.arm == "A"]
add("A: all", A, "trajectory_code", CODEBOOK["trajectory_code"])
add("A: senescence-relevant (each coder's own DEV excluded)", A, "trajectory_code", ["P", "NC", "D", "U"], drop="DEV")
B = both[both.arm == "B"]
add("B: screen", B, "screen_relevant", ["yes", "no"])
add("B: relevant-by-both, NC vs D", B[(B.screen_relevant_ind == "yes") & (B.screen_relevant_opus == "yes")],
    "trajectory_code", ["P", "NC", "D"])
dist = pd.concat(rows, ignore_index=True)
dist["cell"] = dist.apply(lambda r: f"{r['count']}/{r['n']} ({100*r['proportion']:.1f}%; {100*r['ci_low']:.1f}-{100*r['ci_high']:.1f})", axis=1)
dist.to_csv(TABLES / "distributions_independent_vs_opus.tsv", sep="\\t", index=False)
dist.pivot_table(index=["table", "level"], columns="coder", values="cell", aggfunc="first", sort=False)"""),
    ("md", "## The manuscript's direct claim, per coder\nAmong D records: individual/observed vs population/inferred "
           "(residual combinations reported, not dropped)."),
    ("code", """out = []
for who in ["ind", "opus"]:
    d = both[both[f"trajectory_code_{who}"] == "D"]
    combo = d[f"scale_{who}"] + " / " + d[f"observation_{who}"]
    out.append(combo.value_counts().rename({"ind": "independent", "opus": "Opus 5.5"}[who]))
claim = pd.concat(out, axis=1).fillna(0).astype(int)
claim.to_csv(TABLES / "D_scale_observation_by_coder.tsv", sep="\\t")
claim"""),
]

NB["06_kappa"] = [
    ("md", "# 06: Agreement (Cohen's kappa)\nAgreement between the independent coder and Opus 5.5 on the same "
           "records, reported for the planned 10% subset and for everything coded. Bootstrap 95% CIs resample "
           "records. Sparse secondary fields get confusion matrices and raw agreement; do not over-read their kappa."),
    ("code", SETUP),
    ("code", GATE),
    ("code", """from stats_utils import kappa_summary, landis_koch
from io_utils import settings
from coding_schema import DETAIL
s = settings(); reps, seed = s["bootstrap_reps"], s["bootstrap_seed"]
def T_all(df, who):  # Arm B not-relevant becomes its own category so all records enter one kappa
    t = df[f"trajectory_code_{who}"].where(df[f"screen_relevant_{who}"] != "no", "not relevant")
    return t
subsets = {"planned 10% subset": both[both.priority_10pct == "1"], "all coded": both}
res = []
for sname, df in subsets.items():
    A, B = df[df.arm == "A"], df[df.arm == "B"]
    rb = B[(B.screen_relevant_ind == "yes") & (B.screen_relevant_opus == "yes")]
    tests = {
        "T, both arms (Arm B not-relevant as a category)": (T_all(df, "ind"), T_all(df, "opus")),
        "T, Arm A": (A.trajectory_code_ind, A.trajectory_code_opus),
        "Arm B relevance screen": (B.screen_relevant_ind, B.screen_relevant_opus),
        "T, Arm B relevant by both": (rb.trajectory_code_ind, rb.trajectory_code_opus),
        "T collapsed D vs not-D, both arms": (T_all(df, "ind").eq("D"), T_all(df, "opus").eq("D")),
    }
    same_detail = df[(df.trajectory_code_ind == df.trajectory_code_opus) & df.trajectory_code_ind.isin(DETAIL)]
    for f in ["scale", "observation", "anchor", "level"]:
        filled = same_detail[(same_detail[f"{f}_ind"] != "") & (same_detail[f"{f}_opus"] != "")]
        tests[f"{f}, NC/D records with same T"] = (filled[f"{f}_ind"], filled[f"{f}_opus"])
    shaped = df[(df.trajectory_code_ind == df.trajectory_code_opus) & df.trajectory_code_ind.isin(["P", "NC", "D"])]
    shaped = shaped[(shaped.explicitness_ind != "") & (shaped.explicitness_opus != "")]
    tests["explicitness, P/NC/D records with same T"] = (shaped.explicitness_ind, shaped.explicitness_opus)
    tests["organism"] = (df.organism_ind, df.organism_opus)
    for name, (x, y) in tests.items():
        r = kappa_summary(x.astype(str).values, y.astype(str).values, reps=reps, seed=seed)
        res.append({"subset": sname, "comparison": name} | r | {"interpretation": landis_koch(r["cohen_kappa"])})
kappa = pd.DataFrame(res)
kappa.to_csv(TABLES / "kappa_independent_vs_opus.tsv", sep="\\t", index=False)
kappa.round(3)"""),
    ("code", """for sname, df in subsets.items():
    cm = pd.crosstab(T_all(df, "opus").rename("Opus 5.5"), T_all(df, "ind").rename("independent"), margins=True)
    cm.to_csv(TABLES / f"confusion_T_{sname.replace(' ', '_').replace('%', 'pct')}.tsv", sep="\\t")
    print(sname); display(cm)"""),
    ("md", "## Disagreements\nEvery record where T differs, with both coders' notes, for adjudication. "
           "Opus notes are shown here only, after coding is finished."),
    ("code", """dis = both[T_all(both, "ind") != T_all(both, "opus")].assign(T_ind=T_all(both, "ind"), T_opus=T_all(both, "opus"))
dis = dis[["review_id", "pmid", "arm", "year", "title", "T_opus", "T_ind", "note", "notes", "evidence_quote"]]
dis = dis.rename(columns={"note": "opus_note", "notes": "independent_notes"})
dis.to_csv(TABLES / "disagreements_T.tsv", sep="\\t", index=False)
print(len(dis), "disagreements on T"); dis.head(40)"""),
]


def build():
    for name, cells in NB.items():
        nb = nbf.v4.new_notebook()
        nb.cells = [nbf.v4.new_markdown_cell(src) if kind == "md" else nbf.v4.new_code_cell(src) for kind, src in cells]
        nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
        nbf.write(nb, HERE / "notebooks" / f"{name}.ipynb")
        print("wrote", name)


if __name__ == "__main__":
    build()
