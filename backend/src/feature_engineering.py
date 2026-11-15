import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib

ROOT_PATH = Path(__file__).parent.parent.absolute()
PROCESSED_PATH = ROOT_PATH / "data" / "processed"

print("Feature Engineering dengan TF-IDF (Similarity Lebih Pintar)\n")
    
df_rps = pd.read_csv(PROCESSED_PATH / "rps_cleaned.csv")
df_jobs = pd.read_csv(PROCESSED_PATH / "jobs_cleaned.csv")

# Gabungkan teks bersih
df_rps['mahasiswa_skills'] = (df_rps['clean_hasil'].fillna('') + " " + df_rps['clean_materi'].fillna('')).str.strip()
df_jobs['job_skills'] = (df_jobs['clean_short_desc'].fillna('') + " " + df_jobs['clean_job_desc'].fillna('')).str.strip()

# TF-IDF Vectorizer
vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')

# Fit pada semua skill (mahasiswa + jobs)
all_skills = pd.concat([df_rps['mahasiswa_skills'], df_jobs['job_skills']])
tfidf_matrix = vectorizer.fit_transform(all_skills)

print(f"TF-IDF selesai. Vocabulary size: {len(vectorizer.vocabulary_)} kata\n")

# Simpan vectorizer untuk digunakan nanti

joblib.dump(vectorizer, ROOT_PATH / "models" / "tfidf_vectorizer.pkl")

# Simpan data final
df_rps[['Mata Kuliah', 'mahasiswa_skills']].to_csv(PROCESSED_PATH / "final_mahasiswa_skills.csv", index=False)
df_jobs[['title', 'company', 'location', 'job_skills']].to_csv(PROCESSED_PATH / "final_job_skills.csv", index=False)

print("Feature Engineering selesai!")
print("File siap: final_mahasiswa_skills.csv dan final_job_skills.csv")