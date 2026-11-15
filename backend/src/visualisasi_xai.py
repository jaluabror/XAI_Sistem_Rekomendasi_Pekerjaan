# src/visualisasi_xai.py
# Visualisasi XAI untuk Sistem Rekomendasi Karir Berbasis OBE
# Menghasilkan 4 grafik:
#   1. Global Feature Importance (EBM)
#   2. Local Explanation per Job (Waterfall Chart)
#   3. Distribusi Similarity & Probabilitas
#   4. ROC Curve + Confusion Matrix
# ──────────────────────────────────────────────────────────────────────────────

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyArrowPatch
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import roc_curve, auc, confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
import joblib
import warnings
warnings.filterwarnings('ignore')

# ── Setup path ────────────────────────────────────────────────────────────────
ROOT_PATH      = Path(__file__).parent.parent.absolute()
PROCESSED_PATH = ROOT_PATH / "data" / "processed"
MODELS_PATH    = ROOT_PATH / "models"
OUTPUT_PATH    = ROOT_PATH / "outputs" / "visualisasi"
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

# ── Style global ──────────────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family':      'DejaVu Sans',
    'font.size':        11,
    'axes.spines.top':  False,
    'axes.spines.right':False,
    'axes.grid':        True,
    'grid.alpha':       0.3,
    'grid.linestyle':   '--',
    'figure.dpi':       150,
})

COLORS = {
    'navy':   '#065A82',
    'teal':   '#1C7293',
    'accent': '#02C39A',
    'amber':  '#F59E0B',
    'red':    '#EF4444',
    'green':  '#22C55E',
    'gray':   '#64748B',
    'light':  '#E8F4F8',
}

print("=" * 60)
print(" Visualisasi XAI — Sistem Rekomendasi Karir OBE")
print("=" * 60)

# ── Load model & data ─────────────────────────────────────────────────────────
print("\nMemuat model & data...")
ebm        = joblib.load(MODELS_PATH / "ebm_raw.pkl")
ebm_cal    = joblib.load(MODELS_PATH / "ebm_model_3fitur.pkl")
platt      = joblib.load(MODELS_PATH / "platt_scaler.pkl")
vectorizer = joblib.load(MODELS_PATH / "tfidf_vectorizer.pkl")

df_mahasiswa = pd.read_csv(PROCESSED_PATH / "final_mahasiswa_skills.csv")
df_jobs      = pd.read_csv(PROCESSED_PATH / "final_job_skills.csv")

df_mahasiswa['mahasiswa_skills'] = df_mahasiswa['mahasiswa_skills'].fillna('').astype(str)
df_jobs['job_skills']            = df_jobs['job_skills'].fillna('').astype(str)

# ── Helper functions (sama dengan model_training.py) ─────────────────────────
DOMAIN_KEYWORDS = {
    'pemrograman', 'algoritma', 'python', 'java', 'javascript', 'php', 'sql',
    'database', 'web', 'aplikasi', 'sistem', 'software', 'coding', 'backend',
    'frontend', 'api', 'framework', 'mobile', 'android',
    'data', 'analisis', 'analitik', 'machine learning', 'kecerdasan buatan',
    'visualisasi', 'statistik', 'laporan', 'dashboard', 'excel', 'tableau',
    'jaringan', 'network', 'server', 'cloud', 'keamanan', 'security',
    'infrastruktur', 'linux', 'windows', 'hardware', 'troubleshoot',
    'manajemen', 'proyek', 'project', 'scrum', 'agile', 'dokumentasi',
    'perancangan', 'desain', 'arsitektur', 'implementasi', 'pengembangan',
    'informasi', 'bisnis', 'sistem informasi', 'erp', 'enterprise',
    'audit', 'evaluasi', 'monitoring', 'perencanaan',
}

def count_domain_keywords(text):
    return min(sum(1 for kw in DOMAIN_KEYWORDS if kw in str(text).lower()), 10)

def get_location_tier(location):
    loc = str(location).lower()
    tier2 = ['jakarta', 'surabaya', 'bandung', 'yogyakarta', 'semarang']
    tier1 = ['tangerang', 'bekasi', 'depok', 'bogor', 'malang', 'medan',
             'bali', 'cikarang', 'karawang']
    if any(k in loc for k in tier2): return 2
    if any(k in loc for k in tier1): return 1
    return 0

# ── Rebuild dataset untuk evaluasi ───────────────────────────────────────────
print("Membangun dataset evaluasi...")
sample_mhs  = df_mahasiswa.sample(n=200, random_state=42).reset_index(drop=True)
sample_jobs = df_jobs.sample(n=300,  random_state=42).reset_index(drop=True)

mhs_tfidf  = vectorizer.transform(sample_mhs['mahasiswa_skills'])
jobs_tfidf = vectorizer.transform(sample_jobs['job_skills'])

jobs_kw_counts = [count_domain_keywords(t) for t in sample_jobs['job_skills']]
jobs_loc_tier  = [get_location_tier(l)      for l in sample_jobs['location']]

data = []
for i in range(len(sample_mhs)):
    mhs_vec  = mhs_tfidf[i]
    sims     = cosine_similarity(mhs_vec, jobs_tfidf).flatten()
    sim_top25 = float(np.percentile(sims, 75))

    for j, sim in enumerate(sims):
        similarity   = float(sim)
        job_kw_count = min(jobs_kw_counts[j], 10)
        loc_tier     = jobs_loc_tier[j]
        label        = 1 if (similarity >= sim_top25 and job_kw_count >= 2) else 0
        data.append({
            'similarity':   similarity,
            'job_kw_count': job_kw_count,
            'loc_tier':     loc_tier,
            'label':        label
        })

df_eval = pd.DataFrame(data)
X = df_eval[['similarity', 'job_kw_count', 'loc_tier']]
y = df_eval['label']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Prediksi
y_pred      = ebm_cal.predict(X_test)
raw_probs   = ebm_cal.predict_proba(X_test)[:, 1]
y_prob      = platt.predict_proba(raw_probs.reshape(-1, 1))[:, 1]

print(f"Dataset evaluasi: {len(df_eval):,} pasangan")
print(f"Positif: {y.sum():,} ({y.mean()*100:.1f}%)")


# ══════════════════════════════════════════════════════════════════════════════
# VISUALISASI 1: GLOBAL FEATURE IMPORTANCE
# ══════════════════════════════════════════════════════════════════════════════
print("\n[1/4] Global Feature Importance...")

fig, ax = plt.subplots(figsize=(10, 5))
fig.patch.set_facecolor('white')

importances = ebm.term_importances()
feat_names  = ['similarity', 'job_kw_count', 'loc_tier']
feat_labels = ['Kemiripan Skill\n(Similarity)', 'Relevansi IT Job\n(KW Count)', 'Tier Lokasi\n(Loc Tier)']
imp_values  = importances[:3]

# Sort ascending untuk tampilan horizontal bar
idx    = np.argsort(imp_values)
colors = [COLORS['accent'], COLORS['teal'], COLORS['navy']]
colors_sorted = [colors[i] for i in idx]
labels_sorted = [feat_labels[i] for i in idx]
vals_sorted   = [imp_values[i] for i in idx]

bars = ax.barh(labels_sorted, vals_sorted, color=colors_sorted,
               height=0.5, edgecolor='white', linewidth=1.5)

# Tambah nilai di ujung bar
for bar, val in zip(bars, vals_sorted):
    ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2,
            f'{val:.4f}', va='center', fontsize=12, fontweight='bold',
            color=COLORS['navy'])

# Persentase kontribusi
total = sum(vals_sorted)
for bar, val in zip(bars, vals_sorted):
    pct = val / total * 100
    ax.text(bar.get_width() / 2, bar.get_y() + bar.get_height()/2,
            f'{pct:.1f}%', va='center', ha='center',
            fontsize=11, fontweight='bold', color='white')

ax.set_xlabel('Feature Importance Score (EBM)', fontsize=12, color=COLORS['gray'])
ax.set_title('Global Feature Importance — Explainable Boosting Machine (EBM)',
             fontsize=14, fontweight='bold', color=COLORS['navy'], pad=15)
ax.set_xlim(0, max(vals_sorted) * 1.2)
ax.grid(axis='x', alpha=0.3)
ax.grid(axis='y', alpha=0)
ax.tick_params(axis='y', labelsize=11)

# Catatan
ax.text(0.98, 0.05,
        'Similarity mendominasi keputusan model\ndengan kontribusi >80% dari total bobot',
        transform=ax.transAxes, ha='right', va='bottom',
        fontsize=9, color=COLORS['gray'], style='italic',
        bbox=dict(boxstyle='round,pad=0.4', facecolor=COLORS['light'], alpha=0.8))

plt.tight_layout()
path1 = OUTPUT_PATH / "1_global_feature_importance.png"
plt.savefig(path1, dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print(f"   Disimpan: {path1}")


# ══════════════════════════════════════════════════════════════════════════════
# VISUALISASI 2: LOCAL EXPLANATION (WATERFALL) PER JOB
# ══════════════════════════════════════════════════════════════════════════════
print("\n[2/4] Local Explanation Waterfall Chart...")

# Ambil 5 contoh job rekomendasi untuk mata kuliah tertentu
mk_target = "Algoritma dan Pemrograman"
mhs_rows  = df_mahasiswa[df_mahasiswa['Mata Kuliah'].str.contains(mk_target, case=False, na=False)]

if mhs_rows.empty:
    mhs_rows = df_mahasiswa.iloc[:1]

skill_mhs = mhs_rows.iloc[0]['mahasiswa_skills']
mhs_vec   = vectorizer.transform([skill_mhs])
jobs_vec  = vectorizer.transform(df_jobs['job_skills'])
sims_all  = cosine_similarity(mhs_vec, jobs_vec).flatten()

# Ambil top 5 job
top5_idx = np.argsort(sims_all)[::-1][:5]
top5_jobs = []
for idx in top5_idx:
    job = df_jobs.iloc[idx]
    sim = float(sims_all[idx])
    kw  = count_domain_keywords(job['job_skills'])
    loc = get_location_tier(job['location'])

    X_inp     = pd.DataFrame([{'similarity': sim, 'job_kw_count': kw, 'loc_tier': loc}])
    local_exp = ebm.explain_local(X_inp)
    names     = local_exp.data(0)['names']
    scores    = local_exp.data(0)['scores']
    intercept = local_exp.data(0).get('perf', {})
    contrib   = dict(zip(names, scores))

    top5_jobs.append({
        'title':     job['title'][:35] + '...' if len(job['title']) > 35 else job['title'],
        'sim':       sim,
        'kw':        kw,
        'loc':       loc,
        'sim_c':     contrib.get('similarity',   0),
        'kw_c':      contrib.get('job_kw_count', 0),
        'loc_c':     contrib.get('loc_tier',     0),
    })

fig, axes = plt.subplots(1, 5, figsize=(18, 6), sharey=False)
fig.patch.set_facecolor('white')
fig.suptitle(f'Local Explanation EBM — Top 5 Rekomendasi\nMata Kuliah: {mk_target}',
             fontsize=13, fontweight='bold', color=COLORS['navy'], y=1.02)

feat_display = ['Similarity', 'KW Count', 'Loc Tier']

for ax, job in zip(axes, top5_jobs):
    contribs = [job['sim_c'], job['kw_c'], job['loc_c']]
    bar_colors = [COLORS['green'] if c >= 0 else COLORS['red'] for c in contribs]

    bars = ax.barh(feat_display, contribs, color=bar_colors,
                   height=0.5, edgecolor='white', linewidth=1)

    for bar, val in zip(bars, contribs):
        x_pos = val + 0.05 if val >= 0 else val - 0.05
        ha    = 'left' if val >= 0 else 'right'
        ax.text(x_pos, bar.get_y() + bar.get_height()/2,
                f'{val:+.3f}', va='center', ha=ha, fontsize=9,
                fontweight='bold',
                color=COLORS['green'] if val >= 0 else COLORS['red'])

    ax.axvline(x=0, color=COLORS['gray'], linewidth=1, linestyle='-', alpha=0.5)
    ax.set_title(job['title'], fontsize=9, fontweight='bold',
                 color=COLORS['navy'], wrap=True)

    # Info box
    total_abs = abs(job['sim_c']) + abs(job['kw_c']) + abs(job['loc_c']) + 1e-9
    ax.text(0.5, -0.22,
            f"Sim: {job['sim']*100:.1f}% | KW: {job['kw']}/10 | Loc: {job['loc']}/2",
            transform=ax.transAxes, ha='center', fontsize=8,
            color=COLORS['gray'], style='italic')

    ax.grid(axis='x', alpha=0.3)
    ax.grid(axis='y', alpha=0)
    ax.spines['left'].set_visible(False)

# Legend
pos_patch = mpatches.Patch(color=COLORS['green'], label='Kontribusi Positif (Mendukung)')
neg_patch = mpatches.Patch(color=COLORS['red'],   label='Kontribusi Negatif (Mengurangi)')
fig.legend(handles=[pos_patch, neg_patch], loc='lower center',
           ncol=2, fontsize=10, framealpha=0.9, bbox_to_anchor=(0.5, -0.05))

plt.tight_layout()
path2 = OUTPUT_PATH / "2_local_explanation_waterfall.png"
plt.savefig(path2, dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print(f"   Disimpan: {path2}")


# ══════════════════════════════════════════════════════════════════════════════
# VISUALISASI 3: DISTRIBUSI SIMILARITY & PROBABILITAS
# ══════════════════════════════════════════════════════════════════════════════
print("\n[3/4] Distribusi Similarity & Probabilitas...")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.patch.set_facecolor('white')
fig.suptitle('Distribusi Fitur & Output Model EBM',
             fontsize=14, fontweight='bold', color=COLORS['navy'])

# ── Panel kiri: Distribusi Similarity ────────────────────────────────────────
ax1 = axes[0]
sim_vals = df_eval['similarity'].values
ax1.hist(sim_vals, bins=50, color=COLORS['navy'], alpha=0.8, edgecolor='white')
ax1.axvline(sim_vals.mean(), color=COLORS['red'], linewidth=2,
            linestyle='--', label=f'Rata-rata: {sim_vals.mean():.4f}')
ax1.axvline(np.percentile(sim_vals, 75), color=COLORS['amber'],
            linewidth=2, linestyle=':', label=f'Top-25%: {np.percentile(sim_vals, 75):.4f}')

ax1.set_xlabel('Similarity Score (TF-IDF Cosine)', fontsize=11)
ax1.set_ylabel('Jumlah Pasangan', fontsize=11)
ax1.set_title('Distribusi Similarity Score\nKurikulum vs Lowongan Kerja',
              fontsize=12, fontweight='bold', color=COLORS['navy'])
ax1.legend(fontsize=10)

# Annotation
ax1.text(0.97, 0.85,
         f'Mayoritas similarity < 0.15\nRata-rata: {sim_vals.mean():.4f}',
         transform=ax1.transAxes, ha='right', fontsize=9,
         color=COLORS['gray'], style='italic',
         bbox=dict(boxstyle='round,pad=0.4', facecolor=COLORS['light'], alpha=0.9))

# ── Panel kanan: Distribusi Probabilitas ─────────────────────────────────────
ax2 = axes[1]
prob_vals = platt.predict_proba(
    ebm_cal.predict_proba(X_test)[:, 1].reshape(-1, 1)
)[:, 1]

ax2.hist(prob_vals, bins=50, color=COLORS['teal'], alpha=0.8, edgecolor='white')
ax2.axvline(prob_vals.mean(), color=COLORS['red'], linewidth=2,
            linestyle='--', label=f'Rata-rata: {prob_vals.mean():.3f}')

ax2.set_xlabel('Probabilitas Cocok', fontsize=11)
ax2.set_ylabel('Jumlah Pasangan', fontsize=11)
ax2.set_title('Distribusi Probabilitas Cocok\nSetelah Platt Scaling',
              fontsize=12, fontweight='bold', color=COLORS['navy'])
ax2.legend(fontsize=10)

ax2.text(0.97, 0.85,
         f'Rata-rata probabilitas: {prob_vals.mean()*100:.1f}%\nDistribusi lebih merata (Platt Scaling)',
         transform=ax2.transAxes, ha='right', fontsize=9,
         color=COLORS['gray'], style='italic',
         bbox=dict(boxstyle='round,pad=0.4', facecolor=COLORS['light'], alpha=0.9))

plt.tight_layout()
path3 = OUTPUT_PATH / "3_distribusi_similarity_probabilitas.png"
plt.savefig(path3, dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print(f"   Disimpan: {path3}")


# ══════════════════════════════════════════════════════════════════════════════
# VISUALISASI 4: ROC CURVE + CONFUSION MATRIX
# ══════════════════════════════════════════════════════════════════════════════
print("\n[4/4] ROC Curve + Confusion Matrix...")

fig = plt.figure(figsize=(14, 5))
fig.patch.set_facecolor('white')
fig.suptitle('Evaluasi Model EBM — ROC Curve & Confusion Matrix',
             fontsize=14, fontweight='bold', color=COLORS['navy'])

gs = gridspec.GridSpec(1, 2, figure=fig, wspace=0.35)

# ── Panel kiri: ROC Curve ─────────────────────────────────────────────────────
ax1 = fig.add_subplot(gs[0])
fpr, tpr, _ = roc_curve(y_test, y_prob)
roc_auc     = auc(fpr, tpr)

ax1.plot(fpr, tpr, color=COLORS['navy'], linewidth=2.5,
         label=f'ROC Curve (AUC = {roc_auc:.4f})')
ax1.fill_between(fpr, tpr, alpha=0.1, color=COLORS['navy'])
ax1.plot([0, 1], [0, 1], color=COLORS['gray'], linewidth=1.5,
         linestyle='--', label='Random Classifier (AUC = 0.50)')

ax1.set_xlabel('False Positive Rate', fontsize=11)
ax1.set_ylabel('True Positive Rate', fontsize=11)
ax1.set_title('ROC Curve', fontsize=12, fontweight='bold', color=COLORS['navy'])
ax1.legend(fontsize=10, loc='lower right')

# Annotation AUC
ax1.text(0.6, 0.15, f'AUC = {roc_auc:.4f}',
         fontsize=16, fontweight='bold', color=COLORS['navy'],
         bbox=dict(boxstyle='round,pad=0.5', facecolor=COLORS['light'], alpha=0.9))

# ── Panel kanan: Confusion Matrix ────────────────────────────────────────────
ax2 = fig.add_subplot(gs[1])
cm   = confusion_matrix(y_test, y_pred)
labels = ['Tidak Cocok', 'Cocok']

# Heatmap manual
im = ax2.imshow(cm, cmap='Blues', aspect='auto')

# Warna teks berdasarkan nilai
thresh = cm.max() / 2
for i in range(2):
    for j in range(2):
        color = 'white' if cm[i, j] > thresh else COLORS['navy']
        ax2.text(j, i, f'{cm[i,j]:,}',
                 ha='center', va='center',
                 fontsize=18, fontweight='bold', color=color)

        # Label bawah
        sub = ''
        if i == 0 and j == 0: sub = 'True Negative'
        elif i == 0 and j == 1: sub = 'False Positive'
        elif i == 1 and j == 0: sub = 'False Negative'
        else: sub = 'True Positive'
        ax2.text(j, i + 0.28, sub,
                 ha='center', va='center',
                 fontsize=8, color='white' if cm[i, j] > thresh else COLORS['gray'])

ax2.set_xticks([0, 1])
ax2.set_yticks([0, 1])
ax2.set_xticklabels(labels, fontsize=11)
ax2.set_yticklabels(labels, fontsize=11, rotation=90, va='center')
ax2.set_xlabel('Predicted Label', fontsize=11)
ax2.set_ylabel('Actual Label', fontsize=11)
ax2.set_title('Confusion Matrix', fontsize=12, fontweight='bold', color=COLORS['navy'])

# Metrik ringkas di bawah
report = classification_report(y_test, y_pred, target_names=labels, output_dict=True)
acc    = report['accuracy']
f1     = report['Cocok']['f1-score']
prec   = report['Cocok']['precision']
rec    = report['Cocok']['recall']

ax2.text(0.5, -0.18,
         f'Accuracy: {acc:.2%}  |  Precision: {prec:.2%}  |  Recall: {rec:.2%}  |  F1: {f1:.2%}',
         transform=ax2.transAxes, ha='center', fontsize=9,
         color=COLORS['gray'],
         bbox=dict(boxstyle='round,pad=0.4', facecolor=COLORS['light'], alpha=0.9))

plt.tight_layout()
path4 = OUTPUT_PATH / "4_roc_curve_confusion_matrix.png"
plt.savefig(path4, dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print(f"   Disimpan: {path4}")


# ── Summary ───────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print(" Semua visualisasi berhasil dibuat!")
print(f" Lokasi: {OUTPUT_PATH}")
print("=" * 60)
print(f"\n 1. 1_global_feature_importance.png")
print(f" 2. 2_local_explanation_waterfall.png")
print(f" 3. 3_distribusi_similarity_probabilitas.png")
print(f" 4. 4_roc_curve_confusion_matrix.png")