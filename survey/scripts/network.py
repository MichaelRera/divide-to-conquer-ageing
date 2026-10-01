"""Citation network of the full Arm B corpus (trajectory-shape papers on ageing), via OpenAlex.

Output: corpus_works.json (one record per corpus paper) and edges.tsv (citing -> cited, both in corpus).
Reference and seed papers (Table 2 + the Smurf chain) are added to the corpus even if not retrieved by the query.
"""
from paths import DATA, FIG  # noqa: E402
import os
import json, time, urllib.parse, urllib.request
import sample

SEED_PMIDS = {  # manuscript Table 2 papers and the lab's two-phase chain, added as labelled seeds
    "23213228": "Rera 2012 PNAS", "26528826": "Tricoire & Rera 2015", "27073035": "Dambroise 2016",
    "37602729": "Zane 2023", "40490712": "Cansell 2025",
}


def get(url):
    for a in range(5):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                d = json.loads(r.read())
            time.sleep(0.15)
            return d
        except Exception as e:
            print("retry", e); time.sleep(3 + 3 * a)
    raise RuntimeError(url)


def corpus_pmids():
    term = f"{sample.POP} AND {sample.SHAPE}"
    q = urllib.parse.urlencode(dict(db="pubmed", term=term, mindate="1990/01/01", maxdate="2025/12/31",
                                    datetype="pdat", retmode="json", retmax=9999))
    return get(sample.EUTILS + "esearch.fcgi?" + q)["esearchresult"]["idlist"]


def openalex(pmids):
    out = []
    sel = "id,ids,title,publication_year,referenced_works,cited_by_count,primary_topic"
    for i in range(0, len(pmids), 50):
        f = "ids.pmid:" + "|".join(pmids[i:i + 50])
        d = get("https://api.openalex.org/works?" + urllib.parse.urlencode(
            dict(filter=f, select=sel, per_page=50, mailto=os.environ.get("OPENALEX_MAILTO", ""))))
        out += d["results"]
    return out


def main():
    pmids = corpus_pmids()
    print("corpus PMIDs", len(pmids))
    # resolve seed PMIDs by title search would be fragile; seeds are looked up by PMID and flagged
    works = openalex(sorted(set(pmids) | set(SEED_PMIDS)))
    for w in works:
        pm = (w.get("ids", {}).get("pmid") or "").rsplit("/", 1)[-1]
        w["pmid"] = pm
        w["seed"] = SEED_PMIDS.get(pm, "")
        w["in_query"] = pm in set(pmids)
    ids = {w["id"] for w in works}
    edges = [(w["id"], r) for w in works for r in w.get("referenced_works", []) if r in ids]
    json.dump(works, open(str(DATA / "corpus_works.json"), "w"))
    with open(str(DATA / "edges.tsv"), "w") as f:
        f.writelines(f"{a}\t{b}\n" for a, b in edges)
    # most-cited outside references = intellectual anchors of the corpus
    from collections import Counter
    ext = Counter(r for w in works for r in w.get("referenced_works", []) if r not in ids)
    json.dump(ext.most_common(300), open(str(DATA / "external_anchors.json"), "w"))
    print("works", len(works), "internal edges", len(edges), "seeds found", sum(bool(w["seed"]) for w in works))


if __name__ == "__main__":
    main()
