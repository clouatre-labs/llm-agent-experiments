import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

models   = ["haiku-4.5\n(baseline)", "gemini-3-flash\n(exp3)", "devstral-2512\n(exp3)", "minimax-m2.5\n(exp4)", "kimi-k2.5\n(exp4)", "deepseek-v3.2\n(exp4)"]
scores   = [5.8, 4.2, 3.0, 6.0, 7.0, 1.0]
verdicts = ["baseline", "fail", "fail", "pass", "pass", "fail"]

colors = {"baseline": "#1f77b4", "pass": "#2ca02c", "fail": "#d62728"}
bar_colors = [colors[v] for v in verdicts]

fig, ax = plt.subplots(figsize=(9, 5))

bars = ax.bar(range(len(models)), scores, color=bar_colors, width=0.6, zorder=3)

ax.axhline(y=5.3, color="gray", linestyle="--", linewidth=1, label="Gate threshold (5.3)")
ax.axhline(y=5.8, color="#1f77b4", linestyle="--", linewidth=1, alpha=0.4, label="Baseline mean (5.8)")

for bar, score in zip(bars, scores):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
            f"{score}", ha="center", va="bottom", fontsize=10, fontweight="bold")

ax.set_xticks(range(len(models)))
ax.set_xticklabels(models, fontsize=9)
ax.set_ylim(0, 8.5)
ax.set_ylabel("Mean total score (0-8)", fontsize=11)
ax.set_title("Mean score per model -- exp3 and exp4", fontsize=12)
ax.legend(fontsize=9, loc="upper right")
ax.yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig("figures/mean-score-bar.png", dpi=150, bbox_inches="tight")
print("Saved figures/mean-score-bar.png")
