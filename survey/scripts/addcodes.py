"""Append codes keyed by sample index: python3 addcodes.py ARM < lines
Each input line: index<TAB>relevant<TAB>T<TAB>E<TAB>L<TAB>S<TAB>O<TAB>A<TAB>R<TAB>organism<TAB>note
The PMID is taken from sample.json, so it cannot be mistyped; the index must be the next one expected."""
from paths import DATA, FIG  # noqa: E402
import json, sys

arm = sys.argv[1]
recs = [r for k, v in json.load(open(str(DATA / "sample.json"))).items() if k.startswith(arm + "_") for r in v]
path = DATA / f"codes_{arm}.tsv"
try:
    have = open(path).read().splitlines()
except FileNotFoundError:
    have = ["pmid\trelevant\tT\tE\tL\tS\tO\tA\tR\torganism\tnote"]
nxt = len(have) - 1
out = []
for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    f = line.split("\t")
    idx = int(f[0])
    assert idx == nxt, f"expected index {nxt}, got {idx}"
    assert len(f) == 11, f"line {idx}: {len(f)} fields"
    assert f[2] in {"P", "NC", "D", "U", "DEV", "-"}, f"line {idx}: bad T {f[2]}"
    out.append("\t".join([recs[idx]["pmid"]] + f[1:]))
    nxt += 1
open(path, "w").write("\n".join(have + out) + "\n")
print(f"{path}: {nxt} coded of {len(recs)} sampled")
