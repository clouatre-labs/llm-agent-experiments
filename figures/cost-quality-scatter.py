import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

models     = ["haiku-4.5", "kimi-k2.5", "minimax-m2.5", "gemini-3-flash", "devstral-2512", "deepseek-v3.2", "mistral-small-2603", "mercury-2"]
cost_usd   = [0.0222, 0.0122, 0.0043, 0.0021, 0.0025, 0.0011, 0.0078, 0.0029]
mean_score = [5.8, 6.6, 6.4, 4.2, 3.0, 1.0, 5.4, 4.6]
verdicts   = ["baseline", "pass", "pass", "fail", "fail", "fail", "fail", "exp6"]

colors  = {"baseline": "#1f77b4", "pass": "#2ca02c", "fail": "#d62728", "exp6": "#ff7f0e"}
markers = {"baseline": "D", "pass": "o", "fail": "x", "exp6": "^"}
offsets = {
    "haiku-4.5":      (8, -12),
    "kimi-k2.5":      (8,   4),
    "minimax-m2.5":   (8, -12),
    "gemini-3-flash": (8,   4),
    "devstral-2512":  (8, -12),
    "deepseek-v3.2":  (8,   4),
    "mistral-small-2603": (8, -12),
    "mercury-2":      (8,   4),
}

fig, ax = plt.subplots(figsize=(8, 5))

ax.axhline(y=5.3, color="gray",    linestyle="--", linewidth=1)
ax.axhline(y=5.8, color="#1f77b4", linestyle="--", linewidth=1, alpha=0.4)

for m, c, s, v in zip(models, cost_usd, mean_score, verdicts):
    ax.scatter(c, s, color=colors[v], marker=markers[v], s=120, zorder=5)
    ax.annotate(m, (c, s), xytext=offsets[m], textcoords="offset points",
                fontsize=9, ha="left", va="center")

ax.set_xscale("log")
ax.set_xlim(0.0005, 0.1)
ax.set_ylim(0, 8.5)
ax.set_xlabel("Estimated cost per run (USD, log scale)", fontsize=11)
ax.set_ylabel("Mean total score (0-8)", fontsize=11)
ax.set_title("Quality vs. Cost -- exp3, exp4, and exp6 candidates", fontsize=12)

legend_elements = [
    Line2D([0], [0], marker="D", color="w", markerfacecolor="#1f77b4", markersize=9, label="Baseline"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor="#2ca02c", markersize=9, label="Pass"),
    Line2D([0], [0], marker="x", color="#d62728",                      markersize=9, label="Fail"),
    Line2D([0], [0], marker="^", color="w", markerfacecolor="#ff7f0e", markersize=9, label="Exp6 (different task)"),
]
ax.legend(handles=legend_elements, loc="lower right", fontsize=9)

plt.tight_layout()
plt.savefig("figures/cost-quality-scatter.png", dpi=150, bbox_inches="tight")
print("Saved figures/cost-quality-scatter.png")
