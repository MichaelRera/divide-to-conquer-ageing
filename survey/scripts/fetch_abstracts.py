"""Restore the abstract text removed from the public copy of the data.

Abstracts are not redistributed in this repository (they are often under publisher copyright).
This script downloads them again from PubMed (NCBI E-utilities) for every PMID in the sample and
writes them back into the files that originally held them:

    data/sample.json                                  ("abstract" field of each record)
    data/kappa_sheet.tsv                              ("abstract" column, after "title")
    ../validation/data/frozen/sample_frame.tsv        ("abstract" column, after "title")
    ../validation/data/coding/coding_sheet.tsv        ("abstract" column, after "title")

Only the figure-free steps need them: rebuilding the coding batches (validation/perplexity_batches.py),
the coding helper (batch.py) and the validation notebooks. The figures and the agreement analysis
(validation/three_coders.py) run without them.

Usage:  python3 fetch_abstracts.py            (optionally set NCBI_API_KEY to raise the rate limit)
"""
import csv
import json
import os
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
SURVEY = HERE.parent
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
KEY = os.environ.get("NCBI_API_KEY", "")


def fetch(pmids):
    out = {}
    for i in range(0, len(pmids), 150):
        q = dict(db="pubmed", id=",".join(pmids[i:i + 150]), retmode="xml")
        if KEY:
            q["api_key"] = KEY
        with urllib.request.urlopen(EUTILS + "?" + urllib.parse.urlencode(q), timeout=120) as r:
            root = ET.fromstring(r.read())
        for art in root.iter("PubmedArticle"):
            pmid = art.findtext(".//PMID")
            parts = ["".join(a.itertext()).strip() for a in art.iter("AbstractText")]
            out[pmid] = " ".join(p for p in parts if p)
        time.sleep(0.12 if KEY else 0.4)
    return out


def add_column(path, abstracts):
    path = Path(path)
    if not path.exists():
        return
    rows = list(csv.reader(open(path, encoding="utf-8"), delimiter="\t"))
    head = rows[0]
    if "abstract" in head:
        return
    i = head.index("title") + 1
    p = head.index("pmid")
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(head[:i] + ["abstract"] + head[i:])
        for r in rows[1:]:
            w.writerow(r[:i] + [abstracts.get(r[p], "")] + r[i:])
    print("restored", path)


def main():
    sample_path = SURVEY / "data" / "sample.json"
    sample = json.load(open(sample_path))
    pmids = sorted({r["pmid"] for recs in sample.values() for r in recs})
    print(f"fetching {len(pmids)} abstracts from PubMed")
    abstracts = fetch(pmids)
    missing = [p for p in pmids if not abstracts.get(p)]
    for recs in sample.values():
        for r in recs:
            r["abstract"] = abstracts.get(r["pmid"], "")
    json.dump(sample, open(sample_path, "w"), indent=1, ensure_ascii=False)
    print("restored", sample_path)
    for p in [SURVEY / "data" / "kappa_sheet.tsv",
              SURVEY / "validation" / "data" / "frozen" / "sample_frame.tsv",
              SURVEY / "validation" / "data" / "coding" / "coding_sheet.tsv"]:
        add_column(p, abstracts)
    if missing:
        print(f"{len(missing)} PMIDs returned no abstract text: {missing[:10]}")


if __name__ == "__main__":
    main()
