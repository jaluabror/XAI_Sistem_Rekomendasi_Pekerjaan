# src/model_evaluation.py
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, classification_report
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings('ignore')

ROOT_PATH = Path(__file__).parent.parent.absolute()
PROCESSED_PATH = ROOT_PATH / "data" / "processed"
MODELS_PATH = ROOT_PATH / "models"

print("🔄 Memuat model dan data untuk Evaluasi...\n")

ebm = joblib.load(MODELS_PATH / "ebm_model_3fitur.pkl")
vectorizer = joblib.load(MODELS_PATH / "tfidf_vectorizer.pkl")

df_mahasiswa = pd.read_csv(PROCESSED_PATH / "final_mahasiswa_skills.csv")
df_jobs = pd.read_csv(PROCESSED_PATH / "final_job_skills.csv")

sample_mhs = df_mahasiswa.sample(n=700, random_state=42)
sample_jobs = df_jobs.sample(n=1400, random_state=42)

mhs_tfidf = vectorizer.transform(sample_mhs['mahasiswa_skills'])
jobs_tfidf = vectorizer.transform(sample_jobs['job_skills'])

print("🔄 Membuat dataset evaluasi...\n")

X_eval = []
y_true = []

for i, mhs_row in sample_mhs.iterrows():
    mhs_vec = mhs_tfidf[sample_mhs.index.get_loc(i)]
    sims = cosine_similarity(mhs_vec, jobs_tfidf).flatten()
    
    for j, sim in enumerate(sims):
        job = sample_jobs.iloc[j]
        job_length = len(str(job['job_skills']).split())
        location = str(job['location']).lower()
        location_match = 1 if any(x in location for x in ['jakarta', 'jawa timur', 'surabaya', 'bandung']) else 0
        
        label = 1 if sim > 0.10 else 0
        
        X_eval.append([float(sim), job_length, location_match])
        y_true.append(label)

X_eval = np.array(X_eval)
y_true = np.array(y_true)

print(f"✅ Dataset evaluasi siap: {len(y_true)} pasangan\n")

y_pred = ebm.predict(X_eval)
y_prob = ebm.predict_proba(X_eval)[:, 1]

print("📊 HASIL EVALUASI MODEL EBM")
print("=" * 70)
print(f"Accuracy          : {accuracy_score(y_true, y_pred):.4f} ({accuracy_score(y_true, y_pred)*100:.2f}%)")
print(f"Precision         : {precision_score(y_true, y_pred):.4f}")
print(f"Recall            : {recall_score(y_true, y_pred):.4f}")
print(f"F1-Score          : {f1_score(y_true, y_pred):.4f}")
print(f"ROC-AUC           : {roc_auc_score(y_true, y_prob):.4f}")
print("\nConfusion Matrix:")
print(confusion_matrix(y_true, y_pred))
print("\nClassification Report:")
print(classification_report(y_true, y_pred, target_names=['Tidak Cocok (0)', 'Cocok (1)']))

# GLOBAL FEATURE IMPORTANCE (cara yang BENAR)
print("\n🌟 GLOBAL FEATURE IMPORTANCE (EBM)")
print("-" * 50)
feature_names = ['Similarity', 'Job Length', 'Location Match']
importance = ebm.term_importances()   # ← ini yang benar

for name, imp in zip(feature_names, importance):
    print(f"• {name:15} : {imp:.4f} ({imp*100:.2f}%)")

print("\n✅ Evaluasi Model selesai!")