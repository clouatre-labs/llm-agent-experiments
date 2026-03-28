import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

models    = ["minimax-m2.5", "gemini-3-flash", "deepseek-v3.2", "mistral-small-2603", "kimi-k2.5", "devstral-2512", "haiku-4.5", "mercury-2"]
eff_cpqp  = [0.0179,         0.0217,           0.0210,          0.0023,               0.0401,       0.045,           0.1505,      0.0007]
verdicts  = ["pass",         "fail",           "fail",          "fail",               "pass",       "fail",          "baseline",  "exp6"]

# Sort by eff_cpqp ascending
sorted_data = sorted(zip(eff_cpqp, models, verdicts))
eff_cpqp_s, models_s, verdicts_s = zip(*sorted_data)

colors_map = {"baseline": "#1f77b4", "pass": "#2ca02c", "fail": "#d62728", "exp6": "#ff7f0e"}
bar_colors = [colors_map[v] for v in verdicts_s]

fig, ax = plt.subplots(figsize=(8, 4))
bars = ax.barh(models_s, eff_cpqp_s, color=bar_colors, height=0.6)

ax.set_xlabel("Effective cost per quality point (USD) -- lower is better", fontsize=11)
ax.set_title("Efficiency metric: eff_cost_per_qp -- exp3, exp4, and exp6 candidates", fontsize=12)
ax.set_xlim(0, 0.17)

# Annotate bars with values
for bar, val, model in zip(bars, eff_cpqp_s, models_s):
    label = f"${val:.4f}" + (" *" if model == "mercury-2" else "")
    ax.text(val + 0.002, bar.get_y() + bar.get_height() / 2,
            label, va="center", fontsize=9)

ax.text(0.01, -0.5, "* exp6 (frontmatter task; not directly comparable to exp3/exp4)", fontsize=7, color="#ff7f0e", transform=ax.get_yaxis_transform())

from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#1f77b4", markersize=9, label="Baseline"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#2ca02c", markersize=9, label="Pass"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#d62728", markersize=9, label="Fail"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#ff7f0e", markersize=9, label="Exp6 (different task)"),
]
ax.legend(handles=legend_elements, loc="lower right", fontsize=9)

plt.tight_layout()
plt.savefig("figures/eff-cost-bar.png", dpi=150, bbox_inches="tight")
print("Saved figures/eff-cost-bar.png")
