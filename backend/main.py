from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from collections import Counter

# Import helper fungsional dari konfigurasi internal Anda
from mk_config import normalize_mk_name, get_kategori, get_kategori_icon, get_kategori_realm

app = FastAPI(title="OBE Career Recommendation XAI API")

# ── CONFIG CORS (Agar Next.js bisa Fetch data dari FastAPI tanpa terblokir) ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # URL default Next.js
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pemuat data JSON hasil prediksi EBM Regresi per Mata Kuliah
def load_json_data():
    path = "outputs/semua_hasil_rekomendasi.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

data = load_json_data()

# ── ENDPOINT 1: Mengambil Daftar Semua Mata Kuliah ──
@app.get("/api/courses")
def get_all_courses():
    """
    Mengembalikan daftar semua mata kuliah untuk drop-down menu di Frontend Next.js.
    Nama tampilan (display_name) dirapikan menggunakan normalize_mk_name.
    """
    return [
        {
            "display_name": normalize_mk_name(mk), 
            "actual_name": mk
        } 
        for mk in data.keys()
        if not mk.strip().startswith("_")
    ]

# ── ENDPOINT 2: Mengambil Metrik Global Dashboard ──
@app.get("/api/metrics/global")
def get_dashboard_metrics():
    """
    Mengambil statistik makro langsung dari _global_summary
    yang sudah dihitung dan divalidasi di backend batch processing.
    """
    summary = data.get("_global_summary", {})
    
    if not summary:
        raise HTTPException(status_code=404, detail="_global_summary tidak ditemukan di data")
    
    return {
        "total_courses":          summary.get("total_mk", 0),
        "average_coverage":       f"{summary.get('avg_coverage', 0)}%",
        "top_skill_gap":          summary.get("top_skill_gap", "N/A"),
        "top_skill_gap_mk_count": summary.get("top_skill_gap_mk_count", 0),
        "top_skill_gap_total_mk": summary.get("top_skill_gap_total_mk", 0),
        "unique_roles":           summary.get("unique_roles", 0),
    }

# ── ENDPOINT 3: Mengambil Hasil Rekomendasi Detail Per MK ──
@app.get("/api/recommendations/{course_name}")
def get_recommendations(course_name: str):
    """
    Mengambil data penuh (top_jobs regresi dan pattern lokal) dari satu mata kuliah spesifik
    sesuai dengan opsi dropdown yang dipilih oleh user di frontend.
    """
    if course_name not in data: 
        raise HTTPException(status_code=404, detail=f"Mata kuliah '{course_name}' tidak ditemukan")
    return data[course_name]

# ── ENDPOINT 4: Analisis Ringkasan Kesenjangan Kurikulum (Halaman Gap Analysis) ──
@app.get("/api/gap-analysis/summary")
def get_gap_analysis_summary():
    rows = []
    all_gaps = []
    all_covs = []
    
    for mk, hasil in data.items():
        if not hasil or "top_jobs" not in hasil: 
            continue
            
        avg = hasil.get("pattern", {}).get("avg_coverage", 0.0)
        
        # GANTI: ambil skill_gap dari SEMUA job, bukan cuma top5 pattern
        mk_gaps_set = set()
        mk_covs_set = set()
        for job in hasil.get("top_jobs", []):
            mk_gaps_set.update(job.get("skill_gap", []))
            mk_covs_set.update(job.get("skill_tercover", []))
                
        kat_name = get_kategori(mk)        
        realm_name = get_kategori_realm(mk) 
        is_non_it = (kat_name == "Non-IT")
        
        if not is_non_it:
            all_gaps.extend(list(mk_gaps_set))
            all_covs.extend(list(mk_covs_set))
            
        mk_title_case = normalize_mk_name(mk)
            
        rows.append({
            "mk": mk_title_case,
            "avg": avg,
            "is_non_it": is_non_it,
            "kategori": kat_name,
            "realm": realm_name,
            "icon": get_kategori_icon(kat_name),
            "gap": [item.get("skill") for item in hasil.get("pattern", {}).get("skill_gap_top5", [])[:3]],
            "cov": [item.get("skill") for item in hasil.get("pattern", {}).get("skill_match_top5", [])[:3]],
            "grade": "Tinggi" if avg >= 60 else ("Sedang" if avg >= 30 else ("Rendah" if avg > 0 else "0%"))
        })
        
    rows.sort(key=lambda x: (x["is_non_it"], -x["avg"]))
    
    top_gaps = [{"skill": s, "count": f} for s, f in Counter(all_gaps).most_common(15)]
    top_covs = [{"skill": s, "count": f} for s, f in Counter(all_covs).most_common(10)]
    
    return {
        "stats": {
            "total_mk": len(rows),
            "it_spesifik": len([r for r in rows if r["kategori"] == "IT Spesifik"]),
            "it_umum": len([r for r in rows if r["kategori"] == "IT Umum"]),
            "non_it": len([r for r in rows if r["kategori"] == "Non-IT"])
        },
        "top_gaps": top_gaps,
        "top_covs": top_covs,
        "table_rows": rows
    }
# ── ENDPOINT 5: Matriks Kepadatan Kesenjangan Kurikulum (Heatmap Data) ──
@app.get("/api/gap-analysis/heatmap")
def get_gap_analysis_heatmap():
    all_gaps = []
    for mk, hasil in data.items():
        if get_kategori(mk) == "Non-IT" or not hasil or "pattern" not in hasil:
            continue
        for item in hasil.get("pattern", {}).get("skill_gap_top5", []):
            all_gaps.append(item.get("skill"))
            
    top_skills = [s for s, f in Counter(all_gaps).most_common(15)]
    
    matrix_data = []
    course_labels = []
    
    for mk, hasil in data.items():
        if get_kategori(mk) == "Non-IT" or not hasil or "pattern" not in hasil:
            continue
            
        # Membaca pasangan key-value frekuensi dari struktur list objek baru
        mk_counter = {item.get("skill"): item.get("freq", 0) for item in hasil.get("pattern", {}).get("skill_gap_top5", [])}
        row_values = [mk_counter.get(skill, 0) for skill in top_skills]
        
        matrix_data.append(row_values)
        course_labels.append(normalize_mk_name(mk))
        
    return {
        "x_axis_skills": top_skills,
        "y_axis_courses": course_labels,
        "z_matrix": matrix_data
    }

# ── ENDPOINT 6: Penjelasan Lokal Bobot Model EBM Regresi (XAI Detail) ──
@app.get("/api/explainability/{course_name}/{rank}")
def get_job_explainability_detail(course_name: str, rank: int):
    """
    Endpoint interaktif untuk membongkar kontribusi nilai kontinu regresi
    dari parameter ebm_sim_bobot dan ebm_kw_bobot (EBM Glass-Box Model).
    """
    if course_name not in data:
        raise HTTPException(status_code=404, detail="Mata kuliah tidak ditemukan")
        
    top_jobs = data[course_name].get("top_jobs", [])
    selected_job = next((j for j in top_jobs if j.get("rank") == rank), None)
    
    if not selected_job:
        raise HTTPException(status_code=404, detail="Pekerjaan dengan rank tersebut tidak ditemukan")
        
    return {
        **selected_job,
        "ebm_sim_bobot": float(selected_job.get("ebm_sim_bobot", 0.0)),
        "ebm_kw_bobot": float(selected_job.get("ebm_kw_bobot", 0.0))
    }