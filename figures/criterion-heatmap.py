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
    'mistral-small-2603\n(fail)',
    'mercury-2\n(exp6*)',
]
criteria = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8']
data = np.array([
    [1.0, 1.0, 0.2, 1.0, 0.2, 0.4, 1.0, 1.0],  # haiku
    [1.0, 1.0, 0.6, 1.0, 0.4, 1.0, 1.0, 1.0],  # kimi
    [1.0, 1.0, 0.0, 1.0, 0.8, 0.4, 0.8, 1.0],  # minimax
    [1.0, 1.0, 0.0, 0.8, 0.2, 0.0, 0.2, 1.0],  # gemini
    [1.0, 0.8, 0.0, 0.0, 0.0, 0.0, 0.2, 1.0],  # devstral
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],  # deepseek
    [1.0, 1.0, 0.0, 1.0, 0.0, 0.6, 0.6, 1.0],  # mistral
    [1.0, 0.8, 0.8, 0.0, 1.0, 0.0, 0.0, 1.0],  # mercury-2 (exp6; C4/C6 structurally 0)
])

fig, ax = plt.subplots(figsize=(10, 6))
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
ax.axhline(y=6.5, color='#ff7f0e', linewidth=1.5, linestyle=':')

ax.text(7.6, 7, '* exp6\nfrontmatter\ntask;\nC4/C6\nstructurally 0', ha='left', va='center', fontsize=7, color='#ff7f0e')

plt.colorbar(im, ax=ax, label='Pass rate (0.0 = never, 1.0 = always)')
ax.set_title('Criterion pass rates across all evaluated models (exp3 + exp4 + exp6)', fontsize=12, pad=12)

plt.tight_layout()
plt.savefig('figures/criterion-heatmap.png', dpi=150, bbox_inches='tight')
print('Saved figures/criterion-heatmap.png')
