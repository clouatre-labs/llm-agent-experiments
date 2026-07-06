import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

models    = ["minimax-m2.5", "gemini-3-flash", "deepseek-v3.2", "mistral-small-2603", "kimi-k2.5", "devstral-2512", "haiku-4.5", "mercury-2", "gemma-4-26b-a4b"]
eff_cpqp  = [0.0179,         0.0217,           0.0210,          0.0023,               0.0401,       0.045,           0.1505,      0.0007,      0.0000468]
verdicts  = ["pass",         "fail",           "fail",          "fail",               "pass",       "fail",          "baseline",  "fail",      "fail"]

# Sort by eff_cpqp ascending
sorted_data = sorted(zip(eff_cpqp, models, verdicts))
eff_cpqp_s, models_s, verdicts_s = zip(*sorted_data)

colors_map = {"baseline": "#1f77b4", "pass": "#2ca02c", "fail": "#d62728"}
bar_colors = [colors_map[v] for v in verdicts_s]

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.barh(models_s, eff_cpqp_s, color=bar_colors, height=0.6)

ax.set_xlabel("Effective cost per quality point (USD, log scale) -- lower is better", fontsize=11)
ax.set_title("Efficiency metric: eff_cost_per_qp -- exp3, exp4, exp6, and exp7 candidates", fontsize=12)
ax.set_xscale("log")
ax.set_xlim(0.00003, 0.3)

# Note: exp7 (Gemma 4) costs are from actual Bedrock Mantle API pricing, not accumulated session tokens

# Annotate bars with values
for bar, val in zip(bars, eff_cpqp_s):
    ax.text(val * 1.15, bar.get_y() + bar.get_height() / 2,
            f"${val:.5f}", va="center", fontsize=9)

from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#1f77b4", markersize=9, label="Baseline"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#2ca02c", markersize=9, label="Pass"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#d62728", markersize=9, label="Fail"),
]
ax.legend(handles=legend_elements, loc="lower right", fontsize=9)

plt.tight_layout()
plt.savefig("eff-cost-bar.png", dpi=150, bbox_inches="tight")
print("Saved eff-cost-bar.png")
