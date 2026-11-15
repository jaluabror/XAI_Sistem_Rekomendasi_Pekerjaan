import os
from recommendation_system import (normalize_clo, vocab_match_score, DOMAIN_KEYWORDS, domain_match_score, count_domain_keywords)
os.environ["LOKY_MAX_CPU_COUNT"] = "1"
import pandas as pd
import numpy as np
import re
from pathlib import Path
from interpret.glassbox import ExplainableBoostingRegressor   # ← HANYA Regressor, Classifier sudah tidak dipakai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score      # ← metrik regresi, BUKAN classification_report/roc_auc_score
import joblib
import warnings
warnings.filterwarnings('ignore')

ROOT_PATH      = Path(__file__).parent.parent.absolute()
PROCESSED_PATH = ROOT_PATH / "data" / "processed"
MODELS_PATH    = ROOT_PATH / "models"
MODELS_PATH.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("Training EBM")
print("=" * 60)

# ── 1. Load Data ───────────────────────────────────────────────────────────────
df_mahasiswa = pd.read_csv(PROCESSED_PATH / "final_mahasiswa_skills.csv")
df_jobs      = pd.read_csv(PROCESSED_PATH / "final_job_skills.csv")

df_mahasiswa['mahasiswa_skills'] = df_mahasiswa['mahasiswa_skills'].fillna('').astype(str)
df_jobs['job_skills']            = df_jobs['job_skills'].fillna('').astype(str)

df_mahasiswa = df_mahasiswa[df_mahasiswa['mahasiswa_skills'].str.strip() != ''].reset_index(drop=True)
df_jobs      = df_jobs[df_jobs['job_skills'].str.strip() != ''].reset_index(drop=True)

print(f"\nDataset mahasiswa : {df_mahasiswa.shape}")
print(f"Dataset jobs      : {df_jobs.shape}")

# ── 2. Build TF-IDF Vectorizer ────────────────────────────────────────────────

print("\nMembangun TF-IDF Vectorizer...")
all_texts  = (
    df_mahasiswa['mahasiswa_skills'].tolist() +
    df_jobs['job_skills'].tolist()
)
vectorizer = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2),
    min_df=2,
    sublinear_tf=True
    # stop_words TIDAK diisi — biarkan semua kata masuk
)
vectorizer.fit(all_texts)
joblib.dump(vectorizer, MODELS_PATH / "tfidf_vectorizer.pkl")
print("Vectorizer baru dibangun dan disimpan.")

# ── 3. Sampling ────────────────────────────────────────────────────────────────
sample_mhs  = df_mahasiswa.sample(n=200, random_state=42).reset_index(drop=True)
sample_jobs = df_jobs.sample(n=300,  random_state=42).reset_index(drop=True)

mhs_tfidf  = vectorizer.transform(sample_mhs['mahasiswa_skills'])
jobs_tfidf = vectorizer.transform(sample_jobs['job_skills'])

# ── 4. Helper Functions ────────────────────────────────────────────────────────
DOMAIN_KEYWORDS = {
    'web':        ['html', 'css', 'javascript', 'react', 'angular', 'vue',
                'php', 'laravel', 'django', 'nodejs', 'bootstrap', 'typescript'],
    'data':      ['sql', 'python', 'tableau', 'power bi', 'machine learning',
                'data mining', 'data science', 'data analysis', 'pandas',
                'numpy', 'tensorflow', 'pytorch', 'spark', 'hadoop'],
    'network':   ['networking', 'cisco', 'mikrotik', 'routing', 'switching',
                'firewall', 'linux', 'docker', 'kubernetes', 'devops'],
    'enterprise': ['erp', 'sap', 'odoo', 'togaf', 'archimate', 'cobit',
                'bpmn', 'scrum', 'agile', 'jira', 'waterfall', 'sdlc'],
    'security':   ['cybersecurity', 'firewall', 'cryptography', 'penetration'],
    'mobile':     ['android', 'ios', 'flutter', 'kotlin', 'swift',
                'mobile development', 'react native'],
    'cloud':      ['aws', 'gcp', 'azure', 'cloud', 'docker', 'kubernetes'],
    'database':   ['mysql', 'postgresql', 'mongodb', 'oracle', 'redis',
                'database', 'nosql', 'sql'],
}

def count_domain_keywords(text: str) -> int:
    text_lower = str(text).lower()
    return sum(1 for kw in DOMAIN_KEYWORDS if kw in text_lower)

def domain_match_score(mhs_skill:str, job_skills:str) -> float:
    """
    Mengukur overlap domain IT antara CLO dan Job description.
    Range: 0.0 - 1.0
    """
    mhs_text = normalize_clo(str(mhs_skill).lower())
    job_text = str(job_skills).lower()

    mhs_domains = set()
    job_domains = set()
    
    for domain, keywords in DOMAIN_KEYWORDS.items():
        for kw in keywords:
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, mhs_text): mhs_domains.add(domain)
            if re.search(pattern, job_text): job_domains.add(domain)

    if not job_domains:
        return 0.0
    return len(mhs_domains & job_domains) / len(job_domains) * 10.0

# ── 5. Bangun Dataset Training ─────────────────────────────────────────────────
print("\nMembangun dataset training...")
jobs_kw_counts = [min(count_domain_keywords(t), 10) for t in sample_jobs['job_skills']]

data = []
for i in range(len(sample_mhs)):
    mhs_vec    = mhs_tfidf[i]
    mhs_skills = str(sample_mhs.iloc[i]['mahasiswa_skills'])
    sims       = cosine_similarity(mhs_vec, jobs_tfidf).flatten()

    for j, sim in enumerate(sims):
        job = sample_jobs.iloc[j]
        data.append({
            'similarity':   float(sim),
            'job_kw_count': jobs_kw_counts[j],
            'vocab_match_score':   vocab_match_score(mhs_skills),
            'domain_match_score':  domain_match_score(mhs_skills, str(job['job_skills'])),
        })

df_train = pd.DataFrame(data)
print(f"Total pasangan    : {len(df_train):,}")

print(f"\n{'='*60}")
print(f"DIAGNOSIS DISTRIBUSI vocab & domain match")
print(f"{'='*60}")
print(f"\nvocab_match_score:")
print(df_train['vocab_match_score'].describe())
print(f"\ndomain_match_score:")
print(df_train['domain_match_score'].describe())
print(f"\n% domain_match == 0: {(df_train['domain_match_score']==0).mean()*100:.1f}%")
print(f"% vocab_match == 0:  {(df_train['vocab_match_score']==0).mean()*100:.1f}%")
print(f"{'='*60}\n")

# // Composite Score // 
print(f"\n{'='*60}")
print(f"MEMBANGUN COMPOSITE SCORE")
print(f"{'='*60}")

df_train['composite_score'] = (
    df_train['similarity'] * (1 + df_train['job_kw_count'] / 10)
)

print(f"Composite score → min: {df_train['composite_score'].min():.4f}, "
      f"mean: {df_train['composite_score'].mean():.4f}, "
      f"max: {df_train['composite_score'].max():.4f}")
print(f"{'='*60}\n")

# // X dan Y Composite score //
print(f"\n{'='*60}")
print(f"SETUP REGRESI — Dekomposisi Composite Score")
print(f"{'='*60}")

X = df_train[['similarity', 'job_kw_count']].values
y = df_train['composite_score'].values

print(df_train[['similarity', 'job_kw_count', 'composite_score']].describe())
print(df_train[['similarity', 'job_kw_count', 'composite_score']].corr())

print(f"Shape X (fitur)  : {X.shape}")
print(f"Shape y (target) : {y.shape}")
print(f"Target composite_score → min: {y.min():.4f}, mean: {y.mean():.4f}, max: {y.max():.4f}")
print(f"{'='*60}\n")

# ════════ TRAIN/TEST SPLIT ════════
print(f"\n{'='*60}")
print(f"TRAIN/TEST SPLIT")
print(f"{'='*60}")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"Data training : {X_train.shape[0]:,} baris")
print(f"Data testing  : {X_test.shape[0]:,} baris")
print(f"{'='*60}\n")

joblib.dump(X_test, MODELS_PATH / "X_test.pkl")
joblib.dump(y_test, MODELS_PATH / "y_test.pkl")


# ── 7. Training EBM ────────────────────────────────────────────────────────────
print("\nTraining EBM...")
ebm = ExplainableBoostingRegressor(
    feature_names=['similarity', 'job_kw_count'],
    interactions=1,
    max_bins=128,
    min_samples_leaf=20,
    learning_rate=0.01,
    max_rounds=3000,
)
ebm.fit(X_train, y_train)
print("Training selesai!")

# ════════ EVALUASI MODEL REGRESI ════════
print(f"\n{'='*60}")
print(f" EVALUASI MODEL REGRESI")
print(f"{'='*60}")

y_pred_test = ebm.predict(X_test)

mse  = mean_squared_error(y_test, y_pred_test)
rmse = np.sqrt(mse)
r2   = r2_score(y_test, y_pred_test)

print(f"MSE  (Mean Squared Error)     : {mse:.6f}")
print(f"RMSE (Root MSE)               : {rmse:.4f}")
print(f"R²   (R-squared)               : {r2:.4f}")

print(f"\nContoh perbandingan (5 sampel pertama dari test set):")
for i in range(5):
    print(f"  Asli: {y_test[i]:.4f}  |  Tebakan: {y_pred_test[i]:.4f}  |  "
          f"Selisih: {abs(y_test[i]-y_pred_test[i]):.4f}")

print(f"{'='*60}\n")

# ── 10. Simpan Model ───────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f" GLOBAL FEATURE IMPORTANCE — Dekomposisi Kontribusi")
print(f"{'='*60}")

global_exp = ebm.explain_global()
for i, feat_name in enumerate(ebm.feature_names_in_):
    importance = global_exp.data()['scores'][i]
    print(f"  {feat_name:<20}: {importance:.4f}")
print(f"{'='*60}\n")

# ════════ SIMPAN MODEL ════════
joblib.dump(ebm,        MODELS_PATH / "ebm_decompose_similarity_kw.pkl")
joblib.dump(vectorizer, MODELS_PATH / "tfidf_vectorizer.pkl")

print("\n" + "=" * 60)
print(" Model & Vectorizer berhasil disimpan!")
print(f" Path: {MODELS_PATH}")
print("=" * 60)