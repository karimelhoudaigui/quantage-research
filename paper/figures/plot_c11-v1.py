"""Export descriptive scientific plots from saved C11 counts."""
import hashlib
import json
import os
from pathlib import Path
import platform

os.environ.setdefault('MPLBACKEND', 'Agg')
os.environ.setdefault('MPLCONFIGDIR', '/tmp/quantage-paper-matplotlib')
import matplotlib
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = ROOT / 'runs/20261113-c11-frozen-transfer/results/metrics.json'
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    methods = json.loads(source.read_text())['methods']
    keys = ['qwen_direct', 'qwen_unchecked', 'qwen_numeric', 'qwen_semantic']
    names = ['Décision', 'Données', 'Numérique', 'Veto v4']
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.3), layout='constrained')
    correct = [methods[k]['accepted_correct'] for k in keys]
    wrong = [methods[k]['accepted_wrong'] for k in keys]
    axes[0].bar(names, correct, label='Bonnes acceptations', color='#177e89')
    axes[0].bar(names, wrong, bottom=correct, label='Mauvaises acceptations', color='#d1495b')
    axes[0].set(ylabel='Nombre sur 128 cas', ylim=(0, 128), title='Même réponse, contrôles successifs')
    axes[0].legend(frameon=False, fontsize=8)
    for name, key in zip(names, keys):
        value = methods[key]
        axes[1].scatter(value['coverage_all'], value['risk_among_accepted'], s=45, color='#177e89')
        axes[1].annotate(name, (value['coverage_all'], value['risk_among_accepted']), xytext=(4, 7), textcoords='offset points', fontsize=9)
    value = methods['keywords']
    axes[1].scatter(value['coverage_all'], value['risk_among_accepted'], marker='x', s=45, color='#d1495b')
    axes[1].annotate('Mots-clés', (value['coverage_all'], value['risk_among_accepted']), xytext=(4, 7), textcoords='offset points', fontsize=9)
    axes[1].set(xlabel='Acceptés / 128', ylabel='Erronés / acceptés', xlim=(0, 1), ylim=(0, .65), title='Risque et couverture : points discrets')
    axes[1].text(.03, .04, 'Strict, Smol et consensus :\ncouverture 0 ; risque non défini', transform=axes[1].transAxes, fontsize=8)
    for ax in axes:
        ax.spines[['top', 'right']].set_visible(False)
        ax.grid(axis='y', alpha=.15)
        ax.set_axisbelow(True)
    out = ROOT / 'paper/figures'
    out.mkdir(exist_ok=True)
    paths = [out / 'c11-selective.pdf', out / 'c11-selective.png']
    if any(p.exists() for p in paths):
        raise ValueError('figure already exists; preserve it and select a new output for regeneration')
    for path in paths:
        fig.savefig(path, dpi=200, metadata={'Creator': 'QuantAge plot_c11.py'})
    plt.close(fig)
    after = hashlib.sha256(source.read_bytes()).hexdigest()
    if before != after:
        raise ValueError('input changed while plotting')
    (out / 'provenance.json').write_text(json.dumps({
        'command': ['/opt/homebrew/bin/python3.11', 'scripts/plot_c11.py'],
        'input': str(source.relative_to(ROOT)), 'sha256_before': before, 'sha256_after': after,
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'software': {'python': platform.python_version(), 'matplotlib': matplotlib.__version__},
        'outputs': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        'scope': 'descriptive finite counts; no interpolation, confidence interval or risk value at zero coverage'
    }, indent=2) + '\n')
    print('Exported scientific PDF/PNG figures; provenance saved. Standalone figure PDF, not compiled manuscript.')


if __name__ == '__main__':
    main()
