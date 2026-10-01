"""Print a batch of sampled abstracts for coding: python3 batch.py ARM START N"""
from paths import DATA, FIG  # noqa: E402
import json, sys

arm, start, n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
recs = [r for k, v in json.load(open(str(DATA / "sample.json"))).items() if k.startswith(arm + "_") for r in v]
for i, r in enumerate(recs[start:start + n], start):
    print(f"#{i} PMID {r['pmid']} ({r['year']}, {r['journal'][:40]})\nT: {r['title']}\nA: {r['abstract'][:1100]}\n")
