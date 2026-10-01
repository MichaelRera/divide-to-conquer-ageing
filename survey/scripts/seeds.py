"""Replace PMID-guessed seeds by DOI-resolved seeds (manuscript reference numbers) and rebuild edges."""
from paths import DATA, FIG  # noqa: E402
import json, urllib.parse
from network import get

SEEDS = {  # manuscript ref -> DOI
    "[22] Rera 2012": "10.1073/pnas.1215849110", "[23] Zane 2023": "10.1111/acel.13946",
    "[24] Cansell 2025": "10.1186/s12915-025-02421-6", "[25] Dambroise 2016": "10.1038/srep23523",
    "[32] Tricoire & Rera 2015": "10.1371/journal.pone.0141920", "[33] Chen 2012": "10.1038/srep00342",
    "[34] Liu 2019": "10.1093/nsr/nwy162", "[35] Timmons 2019": "10.1111/acel.12970",
    "[36] Lehallier 2019": "10.1038/s41591-019-0673-2", "[37] Holzscheck 2020": "10.18632/aging.103499",
    "[38] Akagi 2023": "10.3390/cells12182297", "[39] Li 2023": "10.1016/j.medj.2023.06.010",
    "[40] Okada 2023": "10.1186/s40246-023-00453-z", "[41] Pridham 2024": "10.1093/gerona/glae021",
    "[42] Olecka 2024": "10.1038/s41467-024-47316-2", "[43] Shen 2024": "10.1038/s43587-024-00692-2",
    "[44] Dohm-Hansen 2024": "10.1016/j.tins.2024.02.001", "[45] Scott 2025": "10.1016/j.isci.2025.113115",
    "[58] Carey 1998": "10.1126/science.281.5379.996", "[81] Roget 2024": "10.7554/eLife.92914",
}
sel = "id,ids,title,publication_year,referenced_works,cited_by_count,primary_topic"
works = json.load(open(str(DATA / "corpus_works.json")))
works = [w for w in works if w["in_query"]]  # drop wrongly resolved PMID seeds
for w in works:
    w["seed"] = ""
byid = {w["id"]: w for w in works}
f = "doi:" + "|".join(SEEDS.values())
res = get("https://api.openalex.org/works?" + urllib.parse.urlencode(dict(filter=f, select=sel, per_page=50)))["results"]
doi2lab = {v.lower(): k for k, v in SEEDS.items()}
for r in res:
    lab = doi2lab.get((r["ids"].get("doi") or "").replace("https://doi.org/", "").lower(), "")
    r["pmid"] = (r["ids"].get("pmid") or "").rsplit("/", 1)[-1]
    if r["id"] in byid:
        byid[r["id"]]["seed"] = lab
    else:
        r.update(seed=lab, in_query=False)
        works.append(r); byid[r["id"]] = r
print("seeds resolved", len(res), "of", len(SEEDS), "| already in query corpus:",
      sum(1 for w in works if w["seed"] and w["in_query"]))
print("missing:", sorted(set(SEEDS) - {w["seed"] for w in works if w["seed"]}))
ids = set(byid)
edges = [(w["id"], r) for w in works for r in w.get("referenced_works", []) if r in ids]
json.dump(works, open(str(DATA / "corpus_works.json"), "w"))
open(str(DATA / "edges.tsv"), "w").writelines(f"{a}\t{b}\n" for a, b in edges)
print("works", len(works), "edges", len(edges))
