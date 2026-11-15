import re
import pandas as pd
import numpy as np
import joblib
import ast
import json
import os
import sys
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
from sklearn.metrics.pairwise import cosine_similarity
import warnings

current_file = Path(__file__).resolve()                     
src_directory = current_file.parent                         
backend_directory = src_directory.parent                    
project_root_directory = backend_directory.parent               

for path_target in [str(project_root_directory), str(backend_directory), str(src_directory)]:
    if path_target not in sys.path:
        sys.path.insert(0, path_target)

from backend.src.explainability_matching import analyze_mk_pattern
from mk_config import normalize_mk_name, get_kategori, MK_TO_KATEGORI

ROOT_PATH      = Path(__file__).parent.parent.absolute()
PROCESSED_PATH = ROOT_PATH / "data" / "processed"
MODELS_PATH    = ROOT_PATH / "models"

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

IT_SKILL_TERMS = [
    # Programming
    'python', 'java', 'javascript', 'php', 'kotlin', 'swift', 'golang',
    'react', 'angular', 'vue', 'flutter', 'django', 'laravel', 'spring',
    'nodejs', 'typescript', 'ruby', 'scala', 'rust', 'programming',
    'algorithm', 'flowchart',

    # Database
    'sql', 'mysql', 'postgresql', 'mongodb', 'oracle', 'nosql',
    'database', 'redis', 'elasticsearch',

    # Cloud & DevOps
    'aws', 'gcp', 'azure', 'cloud', 'docker', 'kubernetes', 'jenkins',
    'devops', 'terraform', 'ansible', 'linux', 'git',

    # Data & AI
    'machine learning', 'deep learning', 'tensorflow', 'pytorch',
    'data science', 'data mining', 'data analysis', 'pandas', 'numpy',
    'tableau', 'power bi', 'statistics',

    # Network & Security
    'networking', 'firewall', 'cisco', 'mikrotik', 'routing', 'switching',
    'cybersecurity', 'penetration', 'wireshark', 'cryptography',

    # Web & Mobile
    'html', 'css', 'bootstrap', 'rest api', 'graphql', 'microservices',
    'android', 'ios', 'mobile development', 'web development',

    # Project & Analysis
    'agile', 'scrum', 'jira', 'uml', 'waterfall', 'sdlc',
    'system analysis', 'business analysis', 'project management',
    'bpmn',

    # Enterprise & Architecture
    'togaf', 'archimate', 'cobit', 'erp', 'sap', 'odoo',

    # Tools
    'hadoop', 'testing', 'quality assurance', 'test case',
    'figma', 'wireframe', 'prototyping', 'kafka', 'spark',
]

CLO_TO_INDUSTRY = {
    # ── Programming & Development ─────────────────────────────────────────────
    'pemrograman':                      'programming',
    'algoritma':                        'algorithm',
    'bahasa pemrograman':               'programming',
    'pengkodean':                       'programming',
    'kode program':                     'programming',
    'berorientasi objek':               'java',
    'object oriented':                  'java',
    'pseudocode':                       'algorithm',
 
    # ── Web ───────────────────────────────────────────────────────────────────
    'halaman web':                      'html',
    'web statis':                       'html',
    'web dinamis':                      'javascript',
    'pengembangan web':                 'web development',
    'aplikasi web':                     'web development',
    'antarmuka pengguna':               'html',
    'antarmuka':                        'html',
    'user interface':                   'javascript',
    'pengembangan ui':                  'javascript',
    'tampilan ui':                      'html',
 
    # ── Mobile ────────────────────────────────────────────────────────────────
    'aplikasi bergerak':                'mobile development',
    'aplikasi mobile':                  'mobile development',
    'pengembangan mobile':              'mobile development',
    'pengembangan aplikasi bergerak':   'mobile development',
    'pengembangan aplikasi mobile':     'mobile development',
 
    # ── Database ──────────────────────────────────────────────────────────────
    'basis data':                       'database',
    'basisdata':                        'database',
    'pangkalan data':                   'database',
    'penyimpanan data':                 'database',
    'pemodelan data':                   'database',
    'model data':                       'database',
    'kueri':                            'sql',
    'query':                            'sql',
    'relasional':                       'sql',
    'gudang data':                      'database',
    'tata kelola data':                 'database',
    'manajemen data':                   'database',
    'tata kelola dan manajemen data':   'database',
 
    # ── Network & Security ────────────────────────────────────────────────────
    'jaringan komputer':                'networking',
    'komunikasi data':                  'networking',
    'keamanan sistem informasi':        'cybersecurity',
    'keamanan informasi':               'cybersecurity',
    'keamanan sistem':                  'cybersecurity',
    'kriptografi':                      'cryptography',
    'enkripsi':                         'cryptography',
    'keamanan jaringan':                'cybersecurity',
    'keamanan komputer':                'cybersecurity',
    'sistem keamanan':                  'cybersecurity',
    'ancaman keamanan':                 'cybersecurity',
    'proteksi data':                    'cybersecurity',
 
    # ── Cloud ─────────────────────────────────────────────────────────────────
    'komputasi awan':                   'cloud',
    'layanan awan':                     'cloud',
    'virtualisasi':                     'cloud',
 
    # ── AI & Data ─────────────────────────────────────────────────────────────
    'kecerdasan buatan':                'machine learning',
    'kecerdasan artifisial':            'machine learning',
    'pembelajaran mesin':               'machine learning',
    'penambangan data':                 'data mining',
    'mining data':                      'data mining',
    'analitik data':                    'data analysis',
    'analisis data':                    'data analysis',
    'visualisasi data':                 'tableau',
    'statistika':                       'statistics',
    'statistik':                        'statistics',
    'business intelligence':            'tableau',
    'intelijen bisnis':                 'tableau',
 
    # ── Enterprise & Architecture ─────────────────────────────────────────────
    'arsitektur enterprise':            'togaf',
    'implementasi arsitektur':          'togaf',
    'enterprise resource planning':     'erp',
    'sistem erp':                       'erp',
    'tata kelola teknologi informasi':  'cobit',
    'tata kelola ti':                   'cobit',
    'tata kelola teknologi':            'cobit',
 
    # ── Analysis & Process ────────────────────────────────────────────────────
    'analisis sistem':                  'system analysis',
    'analisis dan perancangan':         'system analysis',
    'perancangan sistem':               'system analysis',
    'rekayasa perangkat lunak':         'software engineering',
    'proyek perangkat lunak':           'sdlc',
    'pemodelan proses bisnis':          'bpmn',
    'manajemen proyek sistem':          'project management',
    'manajemen proyek':                 'project management',
 
    # ── API & Integration ─────────────────────────────────────────────────────
    'layanan web':                      'rest api',
    'web service':                      'rest api',
    'antarmuka pemrograman':            'rest api',
    'integrasi sistem':                 'rest api',
 
    # ── SDLC & Testing ────────────────────────────────────────────────────────
    'pengujian sistem':                 'sdlc',
    'pengujian perangkat lunak':        'sdlc',
    'siklus hidup':                     'sdlc',
    'capstone':                         'sdlc',
 
    # ── DevOps & Tools ────────────────────────────────────────────────────────
    'kontrol versi':                    'git',
    'version control':                  'git',
    'kontainer':                        'docker',
    'devops':                           'devops',
 
    # ── Methodology ───────────────────────────────────────────────────────────
    'metodologi agile':                 'agile',
    'audit sistem':                     'cobit',
    'manajemen risiko':                 'cybersecurity',
    'notasi bpmn':                      'bpmn',

    # ── UI/UX ──────────────────────────────────────────────────
    'ui ux':                    'javascript',
    'desain ui':                'javascript',
    'desain ux':                'javascript',
    'user experience':          'javascript',
    'wireframe':                'javascript',
    'prototipe':                'javascript',
    'figma':                    'figma',
    'adobe xd':                 'figma',

    # ── Sistem Operasi ────────────────────────────────────────────────
    'sistem operasi':           'linux',
    'manajemen memori':         'linux',
    'shell scripting':          'linux',
    'kernel':                   'linux',
    'file system':              'linux',

    # ── Mobile ────────────────────────────────────────────────────────
    'android':                  'android',
    'kotlin':                   'kotlin',
    'flutter':                  'flutter',
    'aplikasi android':         'android',
    'native':                   'android',

    # ── Data Mining / AI ─────────────────────────────────────────────
    'supervised learning':      'machine learning',
    'unsupervised learning':    'machine learning',
    'neural network':           'deep learning',
    'jaringan saraf':           'deep learning',

    # ── Pengujian ────────────────────────────────────────────────────
    'unit test':                'sdlc',
    'black box testing':        'sdlc',
    'white box testing':        'sdlc',
    'test case':                'sdlc',
    'quality assurance':        'sdlc',

    # ── Integrasi & Middleware ───────────────────────────────────────
    'integrasi aplikasi':       'rest api',
    'middleware':               'rest api',
    'service oriented':         'rest api',
    'enterprise integration':   'rest api',
    'message broker':           'kafka',

    # ── Design Thinking & UX ────────────────────────────────────────
    'design thinking':          'uml',
    'user research':            'uml',
    'ideasi':                   'uml',

    # ── Capstone & Project ───────────────────────────────────────────
    'proyek akhir':             'sdlc',
    'pengembangan sistem':      'sdlc',

    # ── E-Government ────────────────────────────────────────────────
    'e-government':             'system analysis',
    'pemerintahan digital':     'system analysis',
    'kota cerdas':              'cloud',
    'smart city':               'cloud',
}

def normalize_clo(text: str) -> str:
    """
    Translasi terminologi CLO akademik Indonesia ke terminologi teknis industri.
    Sort by length descending untuk cegah partial match.

    Contoh:
        'mampu merancang basis data relasional menggunakan sql'
        → 'mampu merancang database sql menggunakan sql'
    """
    text_lower = str(text).lower()
    sorted_map = sorted(
        CLO_TO_INDUSTRY.items(),
        key=lambda x: len(x[0]),
        reverse=True
    )
    for id_term, en_term in sorted_map:
        text_lower = text_lower.replace(id_term, en_term)
    return text_lower

def vocab_match_score(mhs_skill:str) -> float:
    """
    Hitung berapa banyak keyword domain yang muncul di skill mahasiswa.
    """
    mhs_normalized = normalize_clo(str(mhs_skill).lower())
    match_terms = [t for t in IT_SKILL_TERMS if re.search(r'\b' + re.escape(t) + r'\b', mhs_normalized)]
    return min(len(match_terms)/ 15.0 , 1.0)

def domain_match_score(mhs_skill:str, job_skills:str) -> float:
    """
    Mengukur overlap domain IT antara CLO dan Job description.
    Range: 0.0 -10.0
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

def count_domain_keywords(text: str) -> int:
    text_lower = str(text).lower()
    all_keywords = set([kw for kws in DOMAIN_KEYWORDS.values() for kw in kws])
    return min(sum(1 for kw in all_keywords if kw in text_lower), 10)

def parse_skills_coursera(skill_str: str) -> list:
    """Parse kolom Skills dari Coursera (format string list Python)."""
    try:
        skills = ast.literal_eval(skill_str)
        return [s.strip().lower() for s in skills]
    except Exception:
        return [s.strip().lower() for s in str(skill_str).split(',')]

def generate_ebm_explanation(ebm_model, similarity, job_kw_count, composite_score):
    
    """
    Penjelasan dekomposisi EBM, menjelaskan kontribusi similarity dan
    job_kw_count terhadap composite_score (similarity * (1 + kw_count/10)),
    dengan dekomposisi skor ranking yang formulanya transparan.
    """
    try:
        X_input = pd.DataFrame([{
            'similarity':   similarity,
            'job_kw_count': job_kw_count,
        }])

        local_exp = ebm_model.explain_local(X_input)
        names   = local_exp.data(0)['names']
        scores  = local_exp.data(0)['scores']
        contrib = dict(zip(names, scores))

        sim_contrib = contrib.get('similarity',   0)
        kw_contrib  = contrib.get('job_kw_count', 0)

        contribs_abs = {
            'kemiripan skill':    abs(sim_contrib),
            'relevansi IT job':   abs(kw_contrib),
        }
        dominant = max(contribs_abs, key=contribs_abs.get)

        total_abs = abs(sim_contrib) + abs(kw_contrib) + 1e-9
        sim_pct   = round(abs(sim_contrib) / total_abs * 100, 2)
        kw_pct    = round(abs(kw_contrib)  / total_abs * 100, 2)

        dom_map   = {
            'kemiripan skill':        abs(sim_contrib),
            'relevansi IT job':       abs(kw_contrib),
        }
        dominant = max(dom_map, key=dom_map.get)

        sim_arah = "mendukung" if sim_contrib >= 0 else "mengurangi"
        kw_arah  = "mendukung" if kw_contrib  >= 0 else "mengurangi"
    
        lines = [
            f"Dekomposisi Skor Ranking (EBM):",
            f"  • Kemiripan skill  : {similarity*100:.1f}% → bobot {sim_pct:.1f}% ({sim_arah})",
            f"  • Relevansi IT job : {job_kw_count}/10 keyword → bobot {kw_pct:.1f}% ({kw_arah})",
            f"  • Faktor dominan   : {dominant}",
            f"  • Skor gabungan    : {composite_score:.4f}"
        ]
        return {
            'text':           "\n   ".join(lines),
            'sim_pct':        round(sim_pct, 2),
            'kw_pct':         round(kw_pct, 2),
            'faktor_dominan': dominant,
            }
    except Exception as e:
        # Fallback rule-based jika explain_local() gagal
        # print(f"[EBM DEBUG] explain_local() GAGAL: {e}") 
        print(f"[EBM WARNING] explain_local() gagal: {e}")
        return {
            'text':         f"Skor gabungan: {composite_score:.4f} "
                            f"(similarity={similarity:.4f}, kw_count={job_kw_count})",
            'sim_pct':        None,
            'kw_pct':         None,
            'faktor_dominan': 'tidak tersedia',
        }
    
def highlight_skill_match(mhs_skills: str, job_skills: str, min_len: int = 4) -> dict:
    """
    FIX: sebelumnya pakai pendekatan blacklist (STOPWORDS) di atas hasil split
    kata bebas — rawan bocor karena kata umum Bahasa Indonesia jumlahnya sangat
    banyak dan terus bervariasi (mis. 'maupun', 'bekerja', 'jawab', 'laporan').

    Sekarang pakai pendekatan whitelist IT_SKILL_TERMS, konsisten dengan
    skill_coverage_score() — hanya istilah yang memang ada di kamus skill
    teknis yang bisa muncul sebagai skill_match, sehingga hasilnya otomatis
    spesifik (nama bahasa/tools/framework/metodologi), bukan kata umum.
    """
    def exact_match(skill: str, text: str) -> bool:
        pattern = r'\b' + re.escape(skill) + r'\b'
        return bool(re.search(pattern, text))

    mhs_text = normalize_clo(str(mhs_skills))
    job_text = str(job_skills).lower()

    mhs_terms = {t for t in IT_SKILL_TERMS if exact_match(t, mhs_text)}
    job_terms = {t for t in IT_SKILL_TERMS if exact_match(t, job_text)}

    matched   = sorted(mhs_terms & job_terms)
    total     = len(mhs_terms | job_terms)
    match_pct = len(matched) / total * 100 if total > 0 else 0
    return {'matched': matched, 'match_pct': match_pct}

def normalize_clo(text: str) -> str:
    """
    Translasi terminologi CLO akademik Indonesia
    ke terminologi teknis industri.

    Contoh:
        'mampu merancang basis data relasional'
        → 'mampu merancang database sql'
    """
    text_lower = str(text).lower()
    sorted_map = sorted(
        CLO_TO_INDUSTRY.items(),
        key=lambda x: len(x[0]),
        reverse=True
    )
    for id_term, en_term in sorted_map:
        text_lower = text_lower.replace(id_term, en_term)
    return text_lower

def skill_coverage_score(mhs_skills: str, job_skills: str) -> dict:
    original = str(mhs_skills).lower()
    mhs_text = normalize_clo(str(mhs_skills))
    job_text = str(job_skills).lower()

    def exact_match(skill: str, text: str) -> bool:
        """Cek skill sebagai kata utuh, bukan substring."""
        pattern = r'\b' + re.escape(skill) + r'\b'
        return bool(re.search(pattern, text))

    job_skills_needed = [s for s in IT_SKILL_TERMS if exact_match(s, job_text)]

    if not job_skills_needed:
        return {'covered': [], 'not_covered': [], 'score': 0, 'grade': 'N/A'}

    covered     = [s for s in job_skills_needed if s in mhs_text]
    not_covered = [s for s in job_skills_needed if s not in mhs_text]
    score       = len(covered) / len(job_skills_needed) * 100
    grade       = 'Tinggi' if score >= 60 else ('Sedang' if score >= 30 else 'Rendah')

    return {
        'covered':     covered,
        'not_covered': not_covered,
        'score':       round(score, 2),
        'grade':       grade
    }

def analyze_mk_pattern(top_kandidat: list, mhs_skills: str) -> dict:
    from collections import Counter
    from backend.src.course_recommender import classify_role
    all_gaps, all_matches, all_roles, all_scores = [], [], [], []
    for k in top_kandidat:
        cov = skill_coverage_score(mhs_skills, str(k['job']['job_skills']))
        all_scores.append(cov['score'])
        all_gaps.extend(cov['not_covered'])
        all_matches.extend(cov['covered'])
        all_roles.append(classify_role(str(k['job']['title'])))
    return {
        'skill_gap_terbanyak':   Counter(all_gaps).most_common(5),
        'skill_match_terbanyak': Counter(all_matches).most_common(5),
        'role_distribution':     Counter(all_roles).most_common(),
        'avg_coverage':          np.mean(all_scores) if all_scores else 0,
    }
    
# ── Load semua resource ───────────────────────────────────────────────────────
print("=" * 65)
print(" Memuat model EBM + TF-IDF")
print("=" * 65)

ebm        = joblib.load(MODELS_PATH / "ebm_decompose_similarity_kw.pkl")
vectorizer = joblib.load(MODELS_PATH / "tfidf_vectorizer.pkl")

df_mahasiswa = pd.read_csv(PROCESSED_PATH / "final_mahasiswa_skills.csv")
mks = sorted(df_mahasiswa['Mata Kuliah'].unique().tolist())

df_jobs      = pd.read_csv(PROCESSED_PATH / "final_job_skills.csv")

# Bersihkan NaN
df_mahasiswa['mahasiswa_skills'] = df_mahasiswa['mahasiswa_skills'].fillna('').astype(str)
df_jobs['job_skills']            = df_jobs['job_skills'].fillna('').astype(str)

print(f" Model & Vectorizer berhasil dimuat")
print(f" Jobs tersedia   : {len(df_jobs):,}")

# ── Fungsi utama ──────────────────────────────────────────────────────────────
def rekomendasi_kerja(mata_kuliah: str, top_n: int = 10):
    df_jobs['title'] = df_jobs['title'].str.replace(r'^\d+\.\s*', '', regex=True)

    mahasiswa = df_mahasiswa[
        df_mahasiswa['Mata Kuliah'].str.contains(
            mata_kuliah, case=False, na=False, regex=False
        )
    ]

    if mahasiswa.empty:
        print(f"[DEBUG] '{mata_kuliah}' tidak ditemukan di CSV")
        print(f"\n Mata kuliah '{mata_kuliah}' tidak ditemukan.")
        print(" Mata kuliah tersedia:")
        for mk in sorted(df_mahasiswa['Mata Kuliah'].unique()):
            print(f"   - {mk}")
        return

    # ── FIX: gabungkan SEMUA baris CLO untuk MK ini, jangan cuma iloc[0] ──
    skill_mahasiswa = ' '.join(
        mahasiswa['mahasiswa_skills'].dropna().astype(str).tolist()
    )
    nama_mk = mahasiswa.iloc[0]['Mata Kuliah']   # nama MK boleh tetap ambil baris pertama, ini aman

    print(f"\n Mata Kuliah : {nama_mk}")
    print(f" Total CLO   : {len(mahasiswa)} baris digabung")
    print(f" Skills      : {skill_mahasiswa[:120]}...\n")

    # ── Hitung similarity ─────────────────────────────────────────────────────
    mhs_vec  = vectorizer.transform([skill_mahasiswa])
    jobs_vec = vectorizer.transform(df_jobs['job_skills'])
    sims     = cosine_similarity(mhs_vec, jobs_vec).flatten()

    # ── Bangun kandidat ───────────────────────────────────────────────────────
    EXCLUDE_JOB = ['bakery', 'food', 'makanan', 'restoran', 'hotel', 
            'garment', 'tekstil', 'fashion', 'catering']
    kandidat = []
    for idx, sim in enumerate(sims):
        job = df_jobs.iloc[idx]
        kw_count = count_domain_keywords(job['job_skills'])
        if kw_count < 4: 
                continue
        if any(ex in str(job['title']).lower() or ex in str(job['company']).lower()
        for ex in EXCLUDE_JOB):
                    continue

        kandidat.append({
            'idx':          idx,
            'similarity':   float(sim),
            'job_kw_count': count_domain_keywords(job['job_skills']),
            'vocab_match_score': vocab_match_score(skill_mahasiswa),
            'domain_match_score':domain_match_score(skill_mahasiswa, str(job['job_skills'])),
            'job':          job,  
        })
        
    kandidat.sort(key=lambda x: x['similarity'], reverse=True)
    top_kandidat = kandidat[:top_n]

    # ── Prediksi EBM ─────────────────────────────────────────────────────────
    for k in top_kandidat:
        k['composite_score'] = k['similarity'] * (1 + k['job_kw_count'] / 10)

    # ranking tetap berdasarkan composite_score, bukan similarity 
    top_kandidat.sort(key=lambda x: x['composite_score'], reverse=True) 

    # ── Tampilkan hasil ───────────────────────────────────────────────────────
    print(f"{'='*65}")
    print(f" Top {top_n} Rekomendasi Karir — {nama_mk}")
    print(f"{'='*65}\n")

    hasil = []  

    for rank, k in enumerate(top_kandidat, 1):
        job = k['job']

        exp = generate_ebm_explanation(
        ebm, 
        similarity=k['similarity'], 
        job_kw_count=k['job_kw_count'],
        composite_score=k['composite_score'])
        
        match_info = highlight_skill_match(skill_mahasiswa, str(job['job_skills']))
        cov_info   = skill_coverage_score(skill_mahasiswa, str(job['job_skills']))

        hasil.append({
            'rank':              rank,
            'title':             str(job['title']),
            'company':           str(job['company']),
            'location':          str(job.get('location', 'N/A')),
            'similarity':        round(k['similarity'] * 100, 2),
            'job_kw_count':      k['job_kw_count'],
            'vocab_match_score': round(k['vocab_match_score'] * 100, 2),   
            'domain_match_score':round(k['domain_match_score'] * 100, 2), 
            'composite_score':   round(k['composite_score'], 4),           
            'ebm_sim_bobot':     exp['sim_pct'],
            'ebm_kw_bobot':      exp['kw_pct'],
            'faktor_dominan':    exp['faktor_dominan'],
            'skill_match':       match_info['matched'][:6],
            'match_pct':         round(match_info['match_pct'], 2),
            'coverage_score':    round(cov_info['score'], 2),
            'coverage_grade':    cov_info['grade'],
            'skill_tercover':    cov_info['covered'][:5],
            'skill_gap':         cov_info['not_covered'][:5],
            'role_detected':     'N/A',
        })
        
        print(f"{rank}. {job['title']} — {job['company']}")
        print(f"   Lokasi             : {job.get('location', 'N/A')}")
        print(f"   ── Kemiripan & Ranking ───────────────────────────────────")
        print(f"   Similarity         : {k['similarity']*100:.1f}%")
        print(f"   Keyword IT di Job  : {k['job_kw_count']}/10")
        print(f"   Kontribusi (EBM)   : Similarity {exp['sim_pct']:.1f}% | KW Count {exp['kw_pct']:.1f}%")
        print(f"   Faktor Dominan     : {exp['faktor_dominan']}")

        print(f"   ── Explainability Matching ──────────────────────────────")
        print(f"   Skill Match        : {len(match_info['matched'])} kata cocok ({match_info['match_pct']:.1f}% overlap)")
        if match_info['matched']:
            print(f"   Kata yang Match    : {', '.join(match_info['matched'][:6])}")
        print(f"   IT Coverage Score  : {cov_info['score']:.1f}% ({cov_info['grade']})")
        if cov_info['covered']:
            print(f"   Skill Tercover     : {', '.join(cov_info['covered'][:5])}")
        if cov_info['not_covered']:
            print(f"   Skill Belum Cover  : {', '.join(cov_info['not_covered'][:5])}")
        print("-" * 65)

    pattern = analyze_mk_pattern(top_kandidat, skill_mahasiswa)
    print(f"\n{'='*65}")
    print(f" Analisis Pattern — {nama_mk}")
    print(f"{'='*65}")
    print(f"\n Rata-rata IT Coverage Score : {pattern['avg_coverage']:.1f}%")
    print(f"\n Distribusi Role Job:")
    for role, count in pattern['role_distribution']:
            print(f"   {role:<20} : {'█' * count} ({count} job)")
    print(f"\n Skill Sering Match (tercover kurikulum):")
    for skill, freq in pattern['skill_match_terbanyak']:
            print(f"   • {skill:<25} muncul di {freq}/{len(top_kandidat)} job")
    print(f"\n Skill Gap Terbanyak (belum tercover):")
    for skill, freq in pattern['skill_gap_terbanyak']:
            print(f"   • {skill:<25} dibutuhkan {freq}/{len(top_kandidat)} job")
            

    return {
        'mata_kuliah': nama_mk,
        'top_jobs':    hasil,
        'pattern': {
        'avg_coverage':          round(pattern['avg_coverage'], 2),
        'role_distribution':     dict(pattern['role_distribution']),
        'skill_gap_top5':        [{'skill': s, 'freq': f} for s, f in pattern['skill_gap_terbanyak']],
        'skill_match_top5':      [{'skill': s, 'freq': f} for s, f in pattern['skill_match_terbanyak']],
        'top_n':                 len(top_kandidat),
        }
    }

# ── Entry point ───────────────────────────────────────────────────────────────
# 1 mata kuliah → 10 rekomendasi kerja + analisis pattern, simpan ke JSON
# if __name__ == "__main__":
#     mata_kuliah = input("\nMasukkan nama mata kuliah: ").strip()
#     if not mata_kuliah:
#         mata_kuliah = "Algoritma dan Pemrograman"
    
#     hasil = rekomendasi_kerja(mata_kuliah, top_n=10) 

#     import os
#     os.makedirs("outputs", exist_ok=True)
    
#     # Simpan ke JSON
#     filename = f"outputs/hasil_{mata_kuliah.replace(' ', '_')}.json"
#     with open(filename, 'w', encoding='utf-8') as f:
#         json.dump(hasil, f, ensure_ascii=False, indent=2)
#     print(f"\n Hasil disimpan ke {filename}")

# semua hasil = {}
if __name__ == "__main__":
    import os
    from collections import Counter
    os.makedirs("outputs", exist_ok=True)

    semua_hasil = {}
    semua_mk = sorted(df_mahasiswa['Mata Kuliah'].unique().tolist())
    
    print(f"\n Memproses {len(semua_mk)} mata kuliah...")
    
    for i, mk in enumerate(semua_mk, 1):
        print(f"\n[{i}/{len(semua_mk)}] Processing: {mk}")
        hasil = rekomendasi_kerja(mk, top_n=10)
        if hasil is None:
            print(f"[SKIP] {mk} — hasil None")
        else:
            semua_hasil[mk] = hasil

        print(f"\n Menghitung agregat skill gap seluruh mata kuliah...")

    mk_it_list = [mk for mk in semua_hasil.keys() 
            if get_kategori(mk) in ("IT Spesifik", "IT Umum")]
    total_mk_it = len(mk_it_list)
    
    all_skill_gaps = []
    for mk in mk_it_list:
        hasil = semua_hasil[mk]
        mk_gaps_set = set()

        for job in hasil['top_jobs']:
            mk_gaps_set.update(job.get('skill_gap', []))
        all_skill_gaps.extend(list(mk_gaps_set))

    gap_counter = Counter(all_skill_gaps)
    top_gap_skill, top_gap_count = gap_counter.most_common(1)[0] if gap_counter else (None, 0)
        
    mk_dengan_top_gap = 0
    for mk in mk_it_list:
            hasil = semua_hasil[mk]
            for job in hasil['top_jobs']:
                if top_gap_skill in job.get('skill_gap', []):
                    mk_dengan_top_gap += 1
                    break

    # ════════ Pooled Mean Coverage & Unique Roles ════════
    print(f"\n Menghitung pooled mean coverage dan unique roles...")
    all_coverage_scores = []
    all_roles = set()
    
        # Only IT
    for mk in mk_it_list:  
        hasil = semua_hasil[mk]
        for job in hasil['top_jobs']:
            all_coverage_scores.append(job.get('coverage_score', 0))
        
        # Uniqe Roles
        roles_in_mk = hasil.get('pattern', {}).get('role_distribution', {})
        all_roles.update(roles_in_mk.keys())
    
    pooled_avg_coverage = (
        sum(all_coverage_scores) / len(all_coverage_scores) 
        if all_coverage_scores else 0
    )
    total_unique_roles = len(all_roles)
    
    print(f" Pooled avg coverage: {pooled_avg_coverage:.2f}% "
        f"(dari {len(all_coverage_scores)} job individual)")
    print(f" Total unique roles : {total_unique_roles} -> {sorted(all_roles)}")

    semua_hasil['_global_summary'] = {
    'total_mk':               len(semua_hasil),
    'total_mk_it':            total_mk_it,
    'top_skill_gap':          top_gap_skill,
    'top_skill_gap_mk_count': mk_dengan_top_gap,
    'top_skill_gap_total_mk': total_mk_it,
    'avg_coverage':           round(pooled_avg_coverage, 2),
    'unique_roles':           total_unique_roles,
}

    print(f" Skill gap teratas (MK IT): {top_gap_skill} "
            f"(muncul di {mk_dengan_top_gap}/{total_mk_it} MK IT)")
    filename = "outputs/semua_hasil_rekomendasi.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(semua_hasil, f, ensure_ascii=False, indent=2)
    
    print(f"\n Semua hasil disimpan ke {filename}")
    total_mk_asli = len([k for k in semua_hasil.keys() if not k.startswith('_')])
    print(f" Total mata kuliah diproses: {total_mk_asli}")