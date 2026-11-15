import sys
import os
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from recommendation_system import normalize_clo, IT_SKILL_TERMS

df = pd.read_csv("data/processed/final_mahasiswa_skills.csv")

mk = "Matematika Untuk Sistem Informasi"

rows = df[df["Mata Kuliah"] == mk]

print("="*60)
print(mk)
print("="*60)

detected = set()

for idx, row in rows.iterrows():

    raw = str(row["mahasiswa_skills"])
    normal = normalize_clo(raw)

    print(f"\n--- Index {idx} ---")
    print("RAW    :", raw)
    print("NORMAL :", normal)

    for term in IT_SKILL_TERMS:
        if term in normal:
            detected.add(term)

print("\n" + "="*60)
print("Detected IT Terms")
print("="*60)

for term in sorted(detected):
    print(term)