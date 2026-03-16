import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

models = [
    'haiku-4.5\n(baseline)',
    'kimi-k2.5\n(pass)',
    'minimax-m2.5\n(pass)',
    'gemini-3-flash\n(fail)',
    'devstral-2512\n(fail)',
    'deepseek-v3.2\n(fail)',
]
criteria = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8']
data = np.array([
    [1.0, 1.0, 0.2, 1.0, 0.2, 0.4, 1.0, 1.0],  # haiku
    [1.0, 1.0, 0.6, 1.0, 0.4, 1.0, 1.0, 1.0],  # kimi
    [1.0, 1.0, 0.0, 1.0, 0.8, 0.4, 0.8, 1.0],  # minimax
    [1.0, 1.0, 0.0, 0.8, 0.2, 0.0, 0.2, 1.0],  # gemini
    [1.0, 0.8, 0.0, 0.0, 0.0, 0.0, 0.2, 1.0],  # devstral
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],  # deepseek
])

fig, ax = plt.subplots(figsize=(10, 5))
cmap = plt.get_cmap('RdYlGn')
im = ax.imshow(data, cmap=cmap, vmin=0, vmax=1, aspect='auto')

ax.set_xticks(range(len(criteria)))
ax.set_xticklabels(criteria, fontsize=11)
ax.set_yticks(range(len(models)))
ax.set_yticklabels(models, fontsize=10)

for i in range(len(models)):
    for j in range(len(criteria)):
        val = data[i, j]
        color = 'black' if 0.2 < val < 0.8 else ('white' if val < 0.3 else 'black')
        ax.text(j, i, f'{val:.1f}', ha='center', va='center', fontsize=10, color=color, fontweight='bold')

ax.axhline(y=0.5, color='#444', linewidth=1.5, linestyle='--')
ax.axhline(y=2.5, color='#444', linewidth=1.5, linestyle='--')

plt.colorbar(im, ax=ax, label='Pass rate (0.0 = never, 1.0 = always)')
ax.set_title('Criterion pass rates across all evaluated models (exp3 + exp4)', fontsize=12, pad=12)

plt.tight_layout()
plt.savefig('figures/criterion-heatmap.png', dpi=150, bbox_inches='tight')
print('Saved figures/criterion-heatmap.png')
