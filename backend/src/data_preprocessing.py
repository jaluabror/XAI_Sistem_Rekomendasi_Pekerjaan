import pandas as pd
import re
from pathlib import Path

# Path
ROOT_PATH = Path(__file__).parent.parent.absolute()
RAW_PATH = ROOT_PATH / "data" / "raw"
PROCESSED_PATH = ROOT_PATH / "data" / "processed"
PROCESSED_PATH.mkdir(parents=True, exist_ok=True)

print("Mulai Data Cleaning yang Lebih Baik\n")

# Load raw data
df_rps = pd.read_csv(RAW_PATH / "RPS_Kurikulum.csv")
df_jobs = pd.read_csv(RAW_PATH / "jobstreet_jobs.csv")
df_coursera = pd.read_csv(RAW_PATH / "data_coursera.csv")

# ====================== FUNGSI CLEANING TEKS ======================
def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text).lower()                    # Lowercase
    text = re.sub(r'[^\w\s]', ' ', text)        # Hapus punctuation
    text = re.sub(r'\d+', ' ', text)            # Hapus angka
    text = re.sub(r'\s+', ' ', text).strip()    # Hapus spasi berlebih
    return text

print("Membersihkan teks di RPS Kurikulum")
df_rps['clean_materi'] = df_rps['Materi Pembelajaran'].apply(clean_text)
df_rps['clean_hasil'] = df_rps['Hasil Pembelajaran yang Diharapkan'].apply(clean_text)

print("Membersihkan teks di JobStreet Jobs")
df_jobs['clean_short_desc'] = df_jobs['short_desc'].apply(clean_text)
df_jobs['clean_job_desc'] = df_jobs['job_desc'].apply(clean_text)

# Gabungkan teks bersih untuk skill
df_rps['mahasiswa_skills'] = df_rps['clean_hasil'] + " " + df_rps['clean_materi']
df_jobs['job_skills'] = df_jobs['clean_short_desc'] + " " + df_jobs['clean_job_desc']

# Simpan hasil cleaning
df_rps.to_csv(PROCESSED_PATH / "rps_cleaned.csv", index=False)
df_jobs.to_csv(PROCESSED_PATH / "jobs_cleaned.csv", index=False)

print("\nData Cleaning selesai!")
print(f"   RPS cleaned: {df_rps.shape[0]} baris")
print(f"   Jobs cleaned: {df_jobs.shape[0]} lowongan")
print("\nFile yang sudah disimpan di folder processed/:")
print("rps_cleaned.csv")
print("jobs_cleaned.csv")