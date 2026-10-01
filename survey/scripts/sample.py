"""Stratified random sampling of PubMed records for the ageing-trajectory review (see PROTOCOL.md)."""
from paths import DATA, FIG  # noqa: E402
import json, random, time, sys, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
SEED = 20260925
POP = '"Aging"[Majr] AND english[la]'
SHAPE = ('(nonlinear[tiab] OR non-linear[tiab] OR discontinu*[tiab] OR biphasic[tiab] OR "two-phase"[tiab] '
         'OR "two phase"[tiab] OR "two phases"[tiab] OR "phase transition"[tiab] OR "tipping point"[tiab] '
         'OR "tipping points"[tiab] OR "critical transition"[tiab] OR "critical transitions"[tiab] '
         'OR "state transition"[tiab] OR "transition point"[tiab] OR "breakpoint"[tiab] OR "change point"[tiab] '
         'OR "changepoint"[tiab] OR "inflection point"[tiab] OR "waves of"[tiab] OR "switch-like"[tiab] '
         'OR "abrupt"[tiab] OR "stepwise"[tiab] OR "terminal decline"[tiab] OR "phases of aging"[tiab] '
         'OR "phases of ageing"[tiab] OR "stages of aging"[tiab] OR "stages of ageing"[tiab] '
         'OR "accelerat* aging"[tiab] OR "Smurf"[tiab])')
ARMS = {
    "A": (POP, [(1990, 1994), (1995, 1999), (2000, 2004), (2005, 2009), (2010, 2014), (2015, 2019), (2020, 2025)], 50),
    "B": (f"{POP} AND {SHAPE}", [(1990, 1999), (2000, 2009), (2010, 2019), (2020, 2025)], 100),
}


def get(endpoint, **params):
    url = EUTILS + endpoint + "?" + urllib.parse.urlencode(params)
    for attempt in range(5):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                data = r.read()
            time.sleep(0.35)
            return data
        except Exception as e:
            print("retry", endpoint, e, file=sys.stderr)
            time.sleep(2 + attempt * 2)
    raise RuntimeError(url)


def search(term, mindate, maxdate, retstart=0, retmax=0):
    for attempt in range(6):
        d = json.loads(get("esearch.fcgi", db="pubmed", term=term, mindate=mindate, maxdate=maxdate,
                           datetype="pdat", retmode="json", retstart=retstart, retmax=retmax)).get("esearchresult", {})
        if "count" in d:
            return int(d["count"]), d.get("idlist", [])
        print("bad esearch response, retrying", d, file=sys.stderr)
        time.sleep(5 + 5 * attempt)
    raise RuntimeError("esearch failed")


def month_counts(term, y0, y1):
    out = []
    for y in range(y0, y1 + 1):
        n, _ = search(term, f"{y}/01/01", f"{y}/12/31")
        if n < 9000:
            out.append((f"{y}/01/01", f"{y}/12/31", n))
        else:
            for m in range(1, 13):
                last = [31, 29 if y % 4 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
                a, b = f"{y}/{m:02d}/01", f"{y}/{m:02d}/{last}"
                out.append((a, b, search(term, a, b)[0]))
    return out


def fetch(pmids):
    recs = {}
    for i in range(0, len(pmids), 150):
        root = ET.fromstring(get("efetch.fcgi", db="pubmed", id=",".join(pmids[i:i + 150]), retmode="xml"))
        for art in root.findall(".//PubmedArticle"):
            pmid = art.findtext(".//PMID")
            title = "".join(art.find(".//ArticleTitle").itertext()) if art.find(".//ArticleTitle") is not None else ""
            abst = " ".join(("".join(x.itertext())) for x in art.findall(".//Abstract/AbstractText"))
            year = art.findtext(".//PubDate/Year") or (art.findtext(".//PubDate/MedlineDate") or "")[:4]
            journal = art.findtext(".//Journal/Title") or ""
            pts = [p.text for p in art.findall(".//PublicationType")]
            recs[pmid] = dict(pmid=pmid, year=year, journal=journal, title=title, abstract=abst, pubtypes=pts)
    return recs


def main():
    import os
    out = json.load(open(str(DATA / "sample.json"))) if os.path.exists(str(DATA / "sample.json")) else {}
    for arm, (term, strata, n_per) in ARMS.items():
        for (y0, y1) in strata:
            if f"{arm}_{y0}-{y1}" in out:
                continue
            rng = random.Random(f"{SEED}-{arm}-{y0}-{y1}")  # per-stratum seed: resumable and reproducible
            cells = month_counts(term, y0, y1)
            total = sum(c[2] for c in cells)
            idx = rng.sample(range(total), min(total, int(n_per * 1.6)))  # overdraw to replace no-abstract records
            pmids = []
            for k in idx:
                for a, b, n in cells:
                    if k < n:
                        _, ids = search(term, a, b, retstart=k, retmax=1)
                        pmids += ids
                        break
                    k -= n
            recs = fetch(pmids)
            kept = [recs[p] for p in pmids if p in recs and len(recs[p]["abstract"]) > 200][:n_per]
            for r in kept:
                r.update(arm=arm, stratum=f"{y0}-{y1}", stratum_total=total)
            out[f"{arm}_{y0}-{y1}"] = kept
            print(arm, y0, y1, "stratum N =", total, "kept", len(kept), file=sys.stderr, flush=True)
            with open(str(DATA / "sample.json"), "w") as f:
                json.dump(out, f, indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
