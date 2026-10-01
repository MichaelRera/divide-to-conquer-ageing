"""Citation network of the trajectory-vocabulary corpus: (a) research communities and the manuscript's papers,
(b) hand-coded papers (Arm B sample) by framing. Also writes network_stats.json."""
from paths import DATA, FIG  # noqa: E402
import csv, json, collections
import networkx as nx
from netcore import load
import matplotlib.pyplot as plt
from style import FRAME_COLORS, FRAME_LABELS, INK, MUTED

W, by, G, H, cm = load()
giant = set(H)
NAMES = ["Progeroid mouse models, DNA damage", "Biological-age measures", "Brain lifespan trajectories (MRI)",
         "Terminal decline (cognition, well-being)", "Epigenetic age acceleration", "Accelerated ageing after cancer, frailty",
         "Omics nonlinearity and two-phase ageing", "Stress, psychiatric illness and ageing", "Subjective age",
         "Pace of ageing", "Organ 'accelerated ageing' (COPD…)", "Loss of physiological complexity"]
MS = 6  # the community holding the manuscript's papers
K = 12
comm = {n: k for k, c in enumerate(cm) for n in c}
codes = {r["pmid"]: r for r in csv.DictReader(open(str(DATA / "codes_B.tsv")), delimiter="\t")}
pm2id = {w["pmid"]: w["id"] for w in W if w.get("pmid")}
coded = {pm2id[p]: r for p, r in codes.items() if p in pm2id and r["relevant"] == "yes"}
seeds = {w["id"]: w["seed"] for w in W if w.get("seed")}

# community graph: citations between the 12 largest communities
C = nx.Graph(); C.add_nodes_from(range(K))
for u, v in G.edges():
    cu, cv = comm.get(u), comm.get(v)
    if cu is not None and cv is not None and cu != cv and cu < K and cv < K:
        w = C.get_edge_data(cu, cv, {"w": 0})["w"]; C.add_edge(cu, cv, w=w + 1)
import math
ring = [6, 1, 9, 0, 10, 7, 4, 2, 11, 3, 8, 5]  # manuscript community at top; neighbours by shared citations
pos = {k: (math.sin(2 * math.pi * i / K), math.cos(2 * math.pi * i / K)) for i, k in enumerate(ring)}

fig, (a, b) = plt.subplots(1, 2, figsize=(15, 6.4), gridspec_kw=dict(width_ratios=[1.2, 1], wspace=0.9))
a.set_axis_off(); a.set_aspect("equal")
wmax = max(d["w"] for *_, d in C.edges(data=True))
for u, v, d in C.edges(data=True):
    a.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], color="#b8b7b2", lw=0.4 + 5 * d["w"] / wmax, zorder=1,
           solid_capstyle="round")
for k in range(K):
    ns = sum(1 for n in cm[k] if n in seeds)
    ms = k == MS
    a.scatter(*pos[k], s=6 * len(cm[k]), c="#1baf7a" if ms else "#e6e5e1", edgecolors=INK if ms else MUTED,
              linewidths=1.6 if ms else 0.6, zorder=2)
    x, y = pos[k]; r = 1.0 + 0.1 + 0.012 * len(cm[k]) ** 0.5 * 2
    ha = "center" if abs(x) < 0.2 else ("left" if x > 0 else "right")
    a.text(x * r, y * r, NAMES[k] + f" (n = {len(cm[k])})" + (f"\n★ {ns} of 20 manuscript papers" if ns else ""),
           ha=ha, va="center" if abs(y) < 0.9 else ("bottom" if y > 0 else "top"), fontsize=7.2, color=INK, zorder=3,
           fontweight="bold" if ms else "normal")
a.set_xlim(-1.9, 1.9); a.set_ylim(-1.45, 1.45)
a.set_title("a  Research communities in the citation network", loc="left", fontsize=9, color=INK, fontweight="bold", pad=34)

# (b) coded papers by community and framing
order = sorted(range(K), key=lambda k: -sum(1 for n in cm[k] if n in coded))
order = [k for k in order if any(n in coded for n in cm[k])]
for i, k in enumerate(order):
    left = 0
    for t in ["P", "NC", "D"]:
        c = sum(1 for n in cm[k] if n in coded and coded[n]["T"] == t)
        if c:
            b.barh(i, c, left=left, height=0.62, color=FRAME_COLORS[t], edgecolor="white", linewidth=1.2)
            b.text(left + c / 2, i, str(c), ha="center", va="center", fontsize=7, color="white" if t != "D" else INK)
        left += c
b.set_yticks(range(len(order)), [NAMES[k] for k in order], fontsize=7.5)
for lab, k in zip(b.get_yticklabels(), order):
    if k == MS: lab.set_fontweight("bold")
b.invert_yaxis(); b.grid(axis="y", visible=False); b.set_xlabel("coded papers (random sample of vocabulary-matched papers)")
b.legend([plt.Rectangle((0, 0), 1, 1, color=FRAME_COLORS[t]) for t in ["P", "NC", "D"]],
         [FRAME_LABELS[t] for t in ["P", "NC", "D"]], loc="lower right", fontsize=7.2)
b.set_title("b  How papers in each community frame the trajectory", loc="left", fontsize=9, color=INK, fontweight="bold")
fig.text(0.01, -0.02, f"Citation network of all 4,318 PubMed ageing papers using trajectory-shape vocabulary plus the 20 manuscript papers "
         f"(OpenAlex; {G.number_of_edges():,} citation links). Communities: Louvain on the largest connected component ({H.number_of_nodes():,} papers), "
         "12 largest shown, named from their most-cited papers.\nBubble area ∝ papers; line width ∝ citations between communities. "
         "The two manuscript papers outside the green community: Pridham 2024 (biological-age measures) and Carey 1998 (not connected).",
         fontsize=6.8, color=MUTED)
plt.savefig(str(FIG / "Fig_network.pdf"), bbox_inches="tight"); plt.savefig(str(FIG / "Fig_network.png"), dpi=200, bbox_inches="tight")

# statistics
stats = {"nodes": G.number_of_nodes(), "edges": G.number_of_edges(), "giant": len(giant),
         "communities": [{"name": NAMES[k] if k < len(NAMES) else f"c{k}", "size": len(c),
                          "seeds": sorted(seeds[n] for n in c if n in seeds),
                          "coded": dict(collections.Counter(coded[n]["T"] for n in c if n in coded))}
                         for k, c in enumerate(cm[:12])],
         "seeds_outside_giant": sorted(seeds[n] for n in seeds if n not in giant)}
# do discontinuity-framed papers cite each other? edges among coded nodes by framing pair
pairs = collections.Counter()
for u, v in G.edges():
    if u in coded and v in coded:
        pairs[f"{coded[u]['T']}->{coded[v]['T']}"] += 1
stats["edges_between_coded"] = dict(pairs)
# citations from the corpus into the manuscript cluster vs elsewhere
k7 = set(cm[MS])
stats["manuscript_cluster_in_citations_from_other_communities"] = sum(1 for u, v in G.edges() if v in k7 and u in giant and u not in k7)
json.dump(stats, open(str(DATA / "network_stats.json"), "w"), indent=1)
print(json.dumps(stats, indent=1)[:2500])
