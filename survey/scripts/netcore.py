"""Deterministic citation graph + Louvain partition (node/edge order sorted so results do not depend on hash seed)."""
from paths import DATA, FIG  # noqa: E402
import json
import networkx as nx


def load():
    W = json.load(open(str(DATA / "corpus_works.json")))
    by = {w["id"]: w for w in W}
    E = sorted(tuple(l.split("\t")) for l in open(str(DATA / "edges.tsv")).read().split("\n") if l)
    G = nx.DiGraph(); G.add_nodes_from(sorted(by)); G.add_edges_from(E)
    giant = sorted(max(nx.connected_components(G.to_undirected()), key=len))
    H = nx.Graph(); H.add_nodes_from(giant)
    H.add_edges_from(sorted(tuple(sorted(e)) for e in E if e[0] in set(giant)))
    cm = sorted((sorted(c) for c in nx.community.louvain_communities(H, seed=1)), key=lambda c: (-len(c), c[0]))
    return W, by, G, H, cm
