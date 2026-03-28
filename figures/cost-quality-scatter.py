import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

models     = ["haiku-4.5", "kimi-k2.5", "minimax-m2.5", "gemini-3-flash", "devstral-2512", "deepseek-v3.2", "mistral-small-2603", "mercury-2"]
cost_usd   = [0.0222, 0.0122, 0.0043, 0.0021, 0.0025, 0.0011, 0.0078, 0.0029]
mean_score = [5.8, 6.6, 6.4, 4.2, 3.0, 1.0, 5.4, 4.6]
verdicts   = ["baseline", "pass", "pass", "fail", "fail", "fail", "fail", "fail"]

colors  = {"baseline": "#1f77b4", "pass": "#2ca02c", "fail": "#d62728"}
markers = {"baseline": "D", "pass": "o", "fail": "x"}
offsets = {
    "haiku-4.5":          None,       # rendered as off-chart arrow
    "kimi-k2.5":          (-70,  4),
    "minimax-m2.5":       (8, -12),
    "gemini-3-flash":     (-75,  12),
    "devstral-2512":      (8,  12),
    "deepseek-v3.2":      (8,  -12),
    "mistral-small-2603": (8,   4),
    "mercury-2":          (8,  -12),
}

XMAX = 0.010

fig, ax = plt.subplots(figsize=(9, 5))

ax.axhline(y=5.3, color="gray",    linestyle="--", linewidth=1, label="Gate threshold (5.3)")
ax.axhline(y=5.8, color="#1f77b4", linestyle="--", linewidth=1, alpha=0.4, label="Baseline mean (5.8)")

for m, c, s, v in zip(models, cost_usd, mean_score, verdicts):
    if c > XMAX:
        # off-chart: draw arrow from right edge inward
        ax.annotate(
            f"{m}\n(${c:.4f})",
            xy=(XMAX, s),
            xytext=(XMAX - 0.0008, s),
            fontsize=8, ha="right", va="center", color=colors[v],
            arrowprops=dict(arrowstyle="->", color=colors[v], lw=1.2),
        )
        ax.scatter(XMAX, s, color=colors[v], marker=markers[v], s=120, zorder=5, clip_on=False)
    else:
        ax.scatter(c, s, color=colors[v], marker=markers[v], s=120, zorder=5)
        if offsets[m]:
            ax.annotate(m, (c, s), xytext=offsets[m], textcoords="offset points",
                        fontsize=9, ha="left" if offsets[m][0] > 0 else "right", va="center")

ax.set_xlim(0, XMAX)
ax.set_ylim(0, 8.5)
ax.set_xlabel("Estimated cost per run (USD)", fontsize=11)
ax.set_ylabel("Mean total score (0-8)", fontsize=11)
ax.set_title("Quality vs. Cost -- exp3, exp4, and exp6 candidates\n(haiku-4.5 $0.0222 and kimi-k2.5 $0.0122 off-chart right)", fontsize=11)

legend_elements = [
    Line2D([0], [0], marker="D", color="w", markerfacecolor="#1f77b4", markersize=9, label="Baseline"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor="#2ca02c", markersize=9, label="Pass"),
    Line2D([0], [0], marker="x", color="#d62728",                      markersize=9, label="Fail"),
]
ax.legend(handles=legend_elements, loc="lower right", fontsize=9)

plt.tight_layout()
plt.savefig("figures/cost-quality-scatter.png", dpi=150, bbox_inches="tight")
print("Saved figures/cost-quality-scatter.png")
