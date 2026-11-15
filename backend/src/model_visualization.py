# src/xai_visualization.py
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.metrics import mean_squared_error, r2_score

plt.style.use('seaborn-v0_8')

ROOT_PATH = Path(__file__).parent.parent.absolute()
OUTPUT_PATH = ROOT_PATH / "outputs" / "visualizations"
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

print("Memuat model EBM...")
ebm = joblib.load(ROOT_PATH / "models" / "ebm_decompose_similarity_kw.pkl")

# ══════════════════════════════════════════════════════════════════
# 0. EVALUASI MODEL — Predicted vs Actual & Residual Plot
# ══════════════════════════════════════════════════════════════════
print("\nMemuat data test set untuk evaluasi model...")

try:
    X_test = joblib.load(ROOT_PATH / "models" / "X_test.pkl")
    y_test = joblib.load(ROOT_PATH / "models" / "y_test.pkl")

    y_pred_test = ebm.predict(X_test)

    mse  = mean_squared_error(y_test, y_pred_test)
    rmse = np.sqrt(mse)
    r2   = r2_score(y_test, y_pred_test)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    fig.suptitle('Evaluasi Model EBM Regressor — Dekomposisi Composite Score',
                 fontsize=14, fontweight='bold')

    # ── Plot Predicted vs Actual ──────────────────────────────────
    ax1.scatter(y_test, y_pred_test, alpha=0.3, s=10, color='#2ca02c')
    lims = [min(y_test.min(), y_pred_test.min()),
            max(y_test.max(), y_pred_test.max())]
    ax1.plot(lims, lims, 'r--', linewidth=1.5, label='Prediksi Sempurna (y=x)')
    ax1.set_xlabel('Composite Score Asli')
    ax1.set_ylabel('Composite Score Prediksi EBM')
    ax1.set_title(f'Predicted vs Actual (R² = {r2:.4f})')
    ax1.legend()
    ax1.grid(alpha=0.3)

    # ── Plot Residual ──────────────────────────────────────────────
    residuals = y_test - y_pred_test
    ax2.scatter(y_pred_test, residuals, alpha=0.3, s=10, color='#1f77b4')
    ax2.axhline(y=0, color='r', linestyle='--', linewidth=1.5)
    ax2.set_xlabel('Composite Score Prediksi')
    ax2.set_ylabel('Residual (Asli - Prediksi)')
    ax2.set_title(f'Residual Plot (RMSE = {rmse:.4f})')
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH / "xai_0_evaluasi_regresi.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Evaluasi regresi tersimpan: xai_0_evaluasi_regresi.png "
          f"(MSE={mse:.6f}, RMSE={rmse:.4f}, R²={r2:.4f})")

except FileNotFoundError:
    print("⚠️  X_test.pkl / y_test.pkl tidak ditemukan di folder models/ — skip evaluasi regresi.")
    print("   Tambahkan baris berikut di model_training.py setelah train_test_split():")
    print("   joblib.dump(X_test, MODELS_PATH / 'X_test.pkl')")
    print("   joblib.dump(y_test, MODELS_PATH / 'y_test.pkl')")


# ══════════════════════════════════════════════════════════════════
# 1. GLOBAL FEATURE IMPORTANCE — termasuk interaction term
# ══════════════════════════════════════════════════════════════════
global_exp = ebm.explain_global()
term_names = global_exp.data()['names']       
term_scores = global_exp.data()['scores']

# Urutkan dari kontribusi terbesar
order = np.argsort(term_scores)[::-1]
sorted_names = [term_names[i] for i in order]
sorted_scores = [term_scores[i] for i in order]

# Label lebih ramah baca
label_map = {
    'similarity': 'Kemiripan Skill (Similarity)',
    'job_kw_count': 'Relevansi IT Job (Keyword Count)',
}

filtered = [(n, s) for n, s in zip(term_names, term_scores) if n in label_map]
sorted_filtered = sorted(filtered, key=lambda x: x[1], reverse=True)
display_names = [label_map[n] for n, s in sorted_filtered]
sorted_scores = [s for n, s in sorted_filtered]

display_names = [
    label_map.get(n, n.replace(' x ', ' × ').title())
    for n in sorted_names
]

plt.figure(figsize=(9, 5))
colors = ['#ff7f0e' if 'similarity' in n.lower() and '×' not in dn else 
          ('#2ca02c' if 'job_kw_count' in n.lower() and '×' not in dn else '#9467bd')
          for n, dn in zip(sorted_names, display_names)]

bars = plt.barh(display_names, sorted_scores, color=colors)
plt.title('Global Feature Importance (EBM)', fontsize=14, fontweight='bold')
plt.xlabel('Rata-rata Kontribusi Absolut (Mean Absolute Score)')
plt.gca().invert_yaxis()

for bar, val in zip(bars, sorted_scores):
    plt.text(bar.get_width() + max(sorted_scores)*0.01, 
              bar.get_y() + bar.get_height()/2,
              f'{val:.4f}', va='center', fontsize=10)

plt.tight_layout()
plt.savefig(OUTPUT_PATH / "xai_1_global_importance.png", dpi=300, bbox_inches='tight')
plt.close()
print("Global feature importance tersimpan: xai_1_global_importance.png")


# ══════════════════════════════════════════════════════════════════
# 2. LOCAL FEATURE IMPORTANCE — contoh 1 pasangan MK-job (waterfall)
# ══════════════════════════════════════════════════════════════════
def plot_local_explanation(similarity: float, job_kw_count: float, 
                             label: str, filename: str):
    """
    Buat waterfall chart untuk 1 prediksi spesifik.
    label: deskripsi kasus, misal 'Sistem Operasi -> IT Assistant Manager'
    """
    X_input = pd.DataFrame([{
        'similarity':   similarity,
        'job_kw_count': job_kw_count,
    }])

    local_exp = ebm.explain_local(X_input)
    names   = local_exp.data(0)['names']
    scores  = local_exp.data(0)['scores']
    
    intercept = getattr(ebm, 'intercept_', [0])
    base = float(intercept[0]) if hasattr(intercept, '__len__') else float(intercept)

    label_map_local = {
        'similarity': 'Kemiripan Skill',
        'job_kw_count': 'Relevansi IT Job',
    }
    disp_names = [label_map_local.get(n, n.replace(' x ', ' × ')) for n in names]

    positions = ['Base'] + disp_names + ['Prediksi Akhir']

    fig, ax = plt.subplots(figsize=(9, 5))
    running = base
    ax.bar(0, base, color='#7f7f7f')
    for i, (n, s) in enumerate(zip(disp_names, scores), start=1):
        color = '#2ca02c' if s >= 0 else '#d62728'
        bottom = running if s >= 0 else running + s
        ax.bar(i, abs(s), bottom=bottom, color=color)
        running += s
    ax.bar(len(disp_names) + 1, running, color='#1f77b4')

    ax.set_xticks(range(len(positions)))
    ax.set_xticklabels(positions, rotation=20, ha='right')
    ax.set_title(f'Local Feature Importance (EBM)\n{label}', fontsize=13, fontweight='bold')
    ax.set_ylabel('Skor Kontribusi (Composite Score)')
    ax.axhline(0, color='black', linewidth=0.8)

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH / filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Local explanation tersimpan: {filename}")

plot_local_explanation(
    similarity=0.111,      
    job_kw_count=2,          
    label='Sistem Operasi → IT Assistant Manager',
    filename='xai_2_local_example.png'
)

print("\nSelesai! Cek folder outputs/visualizations/")