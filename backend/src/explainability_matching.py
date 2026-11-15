# ══════════════════════════════════════════════════════════════════════════════
# EXPLAINABILITY MATCHING — Tambahkan ke recommendation_system.py
# ══════════════════════════════════════════════════════════════════════════════

# ── IT Skill Keywords untuk coverage score ────────────────────────────────────
IT_SKILL_TERMS = [
    # Programming
    'python', 'java', 'javascript', 'php', 'kotlin', 'swift', 'golang',
    'react', 'angular', 'vue', 'flutter', 'django', 'laravel', 'spring',
    'nodejs', 'typescript', 'ruby', 'scala', 'rust', 'c++', 'c#',
    # Database
    'sql', 'mysql', 'postgresql', 'mongodb', 'oracle', 'nosql',
    'database', 'redis', 'elasticsearch',
    # Cloud & DevOps
    'aws', 'gcp', 'azure', 'cloud', 'docker', 'kubernetes', 'jenkins',
    'devops', 'ci/cd', 'terraform', 'ansible', 'linux', 'git',
    # Data & AI
    'machine learning', 'deep learning', 'tensorflow', 'pytorch',
    'data science', 'pandas', 'numpy', 'tableau', 'power bi',
    'statistics', 'nlp', 'computer vision',
    # Network & Security
    'networking', 'firewall', 'cisco', 'mikrotik', 'routing', 'switching',
    'cybersecurity', 'penetration', 'ethical hacking', 'wireshark',
    # Web & Mobile
    'html', 'css', 'bootstrap', 'rest api', 'graphql', 'microservices',
    'android', 'ios', 'mobile development', 'web development',
    # Project & Analysis
    'agile', 'scrum', 'jira', 'uml', 'system analysis', 'business analysis',
    'project management', 'waterfall', 'sdlc', 'togaf', 'archimate',
    # Enterprise Architecture
    'togaf', 'archimate', 'zachman', 'uml', 'bpmn',
    'enterprise architecture', 'solution architecture',

    'cobit', 'zachman', 'bpmn', 'sparx',
    'power bi', 'looker', 'metabase',
    'rest api', 'graphql', 'soap',
    'web development', 'mobile development',
    'data mining', 'business analysis', 'system analysis',
    'erp', 'sap', 'odoo', 'salesforce',
    'penetration testing', 'ethical hacking',
    'bash', 'shell', 'powershell',
    'hadoop', 'spark', 'kafka',
    'elasticsearch', 'redis',
    'tailwind', 'jquery', 'webpack',

    'pemrograman', 'algoritma', 'flowchart', 'pseudocode',
    'basis data', 'jaringan komputer', 'keamanan informasi',
    'arsitektur enterprise', 'kecerdasan buatan', 'machine learning',
    'data mining', 'penambangan data', 'komputasi awan',
    'pengembangan web', 'aplikasi bergerak', 'mobile',
    'manajemen proyek', 'analisis sistem', 'perancangan sistem',
    'interaksi manusia komputer', 'rekayasa perangkat lunak',
]


# ══════════════════════════════════════════════════════════════════════════════
# FUNGSI 1: Skill Match Highlight
# Deteksi kata/frasa dari CLO yang eksplisit match dengan job description
# ══════════════════════════════════════════════════════════════════════════════
def highlight_skill_match(mhs_skills: str, job_skills: str,
                        min_len: int = 5) -> dict:
    """
    Deteksi kata yang match antara skills mahasiswa dan job description.

    Returns:
        {
            'matched':   list kata yang match,
            'mhs_only':  list kata unik di skills mahasiswa,
            'job_only':  list kata unik di job desc (gap),
            'match_pct': persentase overlap
        }
    """

    STOPWORDS = {
    # ── Kata fungsi Bahasa Indonesia ──────────────────────────────────────────
    'dan', 'atau', 'yang', 'di', 'ke', 'dari', 'pada', 'untuk', 'dengan',
    'dalam', 'adalah', 'ini', 'itu', 'tidak', 'ada', 'akan', 'telah',
    'serta', 'suatu', 'secara', 'berbagai', 'juga', 'agar', 'bagi', 'oleh',
    'atas', 'bisa', 'jadi', 'maka', 'namun', 'tetapi', 'bahwa', 'karena',
    'jika', 'bila', 'antara', 'setiap', 'setelah', 'sebelum', 'selama',
    'sebagai', 'terhadap', 'tersebut', 'melalui', 'tentang', 'satu',
    'sama', 'lain', 'lainnya', 'mereka', 'anda', 'saya', 'kami', 'kita',

    # ── Kata CLO / akademik ───────────────────────────────────────────────────
    'clo', 'subclo', 'mampu', 'dapat', 'memahami', 'menjelaskan',
    'menggunakan', 'membuat', 'merancang', 'mengimplementasikan',
    'mengevaluasi', 'menganalisis', 'mengembangkan', 'melaksanakan',
    'menyusun', 'mengidentifikasi', 'memiliki', 'mengetahui', 'memenuhi',
    'berdasarkan', 'melakukan', 'menerapkan', 'membangun', 'mengelola',
    'mendesain', 'merencanakan', 'memberikan', 'mengumpulkan', 'membantu',
    'mendukung', 'menunjang', 'menulis', 'melaksanakan', 'menghasilkan',
    'menentukan', 'mengidentifikasi', 'mengenai', 'merencanakan',
    'mahasiswa', 'mahasiswi', 'pembelajaran', 'capaian', 'mata', 'kuliah',
    'materi', 'pendidikan', 'akademik', 'semester', 'sesuai', 'minimal',
    'digunakan', 'terkait', 'berkaitan',

    # ── Kata umum non-skill (Indonesia) ──────────────────────────────────────
    'informasi', 'sistem', 'bisnis', 'manajemen', 'kerja', 'kebutuhan',
    'bidang', 'teknologi', 'proses', 'kelola', 'pengembangan', 'aplikasi',
    'lunak', 'perangkat', 'perusahaan', 'pengelolaan', 'komputer', 'prinsip',
    'organisasi', 'utama', 'tata', 'inovasi', 'perkembangan', 'industri',
    'keputusan', 'integrasi', 'pekerjaan', 'berbasis', 'baik', 'teknik',
    'solusi', 'evaluasi', 'analisis', 'penerapan', 'pelaksanaan', 'pembuatan',
    'pemahaman', 'pengetahuan', 'kemampuan', 'keterampilan', 'menguasai',
    'hasil', 'tujuan', 'fungsi', 'peran', 'tugas', 'model', 'strategi',
    'pendekatan', 'layanan', 'produk', 'nilai', 'kualitas', 'standar',
    'sederhana', 'baru', 'logika', 'hubungan', 'perancangan', 'pengujian',
    'implementasi', 'pengambilan', 'peluang', 'masalah', 'proyek', 'relevan',
    'pelanggan', 'budaya', 'tulisan', 'berbahasa', 'indonesia', 'keamanan',
    'bahasa', 'cara', 'jenis', 'mendukung', 'merancang', 'menganalisis',
    'data', 'customer', 'inovasi', 'perkembangan', 'pengembangan',
    'mengembangkan', 'memberikan', 'menerapkan', 'melaksanakan', 'antara',
    'bisa', 'bukan', 'benar', 'jelas', 'tepat', 'harus', 'selama',
    'beradaptasi', 'berkembang', 'berkelanjutan', 'kerangka', 'domain',
    'smart', 'program', 'portofolio', 'interpersonal', 'profesional',
    'komunikasi', 'keahlian', 'digital', 'komponen', 'manfaat', 'link',
    'ketersediaan', 'lingkungan', 'siklus', 'pengumpulan', 'definisi',
    'lingkup', 'perbaikan', 'dunia', 'video', 'halaman', 'fitur',
    'penanganan', 'sedang', 'contoh', 'pembuatan', 'order', 'target',
    'strategi', 'menarik', 'umum', 'aturan', 'belajar', 'skill',
    'keamanan', 'perancangan', 'satu', 'materi',

    # ── Kata Inggris umum non-skill ───────────────────────────────────────────
    'the', 'and', 'or', 'of', 'in', 'to', 'a', 'an', 'for', 'is', 'it',
    'with', 'that', 'this', 'are', 'was', 'were', 'been', 'have', 'has',
    'will', 'would', 'could', 'should', 'may', 'might',
    'business', 'management', 'based', 'using', 'good', 'strong', 'able',
    'ability', 'excellent', 'knowledge', 'experience', 'required', 'work',
    'working', 'team', 'project', 'supply', 'chain', 'service', 'process',
    'system', 'information', 'technology', 'intelligence', 'design',
    'analysis', 'functional', 'relevant', 'about', 'other', 'also',
    'development', 'quality', 'standard', 'strategy', 'learning', 'machine',
    'operations', 'management', 'conversion', 'context', 'delivery',
    'systems', 'review', 'intermediate', 'function', 'process',
    'information', 'marketing', 'market', 'real', 'digital',
}

    mhs_words = {
        w for w in str(mhs_skills).lower().split()
        if len(w) >= min_len and w not in STOPWORDS
    }
    job_words = {
        w for w in str(job_skills).lower().split()
        if len(w) >= min_len and w not in STOPWORDS
    }

    matched  = sorted(mhs_words & job_words)
    mhs_only = sorted(mhs_words - job_words)
    job_only = sorted(job_words - mhs_words)

    total    = len(mhs_words | job_words)
    match_pct = len(matched) / total * 100 if total > 0 else 0

    return {
        'matched':   matched,
        'mhs_only':  mhs_only[:10],   # top 10
        'job_only':  job_only[:10],   # top 10 gap
        'match_pct': match_pct
    }


# ══════════════════════════════════════════════════════════════════════════════
# FUNGSI 2: Skill Coverage Score
# Berapa % skill IT yang dibutuhkan job sudah tercover oleh kurikulum
# ══════════════════════════════════════════════════════════════════════════════

def skill_coverage_score(mhs_skills: str, job_skills: str) -> dict:
    """
    Hitung coverage score: seberapa banyak skill IT yang dibutuhkan job
    sudah ada di skills mahasiswa.

    Returns:
        {
            'covered':     list skill IT yang sudah tercover,
            'not_covered': list skill IT yang belum tercover (gap),
            'score':       float 0-100 (persentase coverage),
            'grade':       str label (Tinggi/Sedang/Rendah)
        }
    """
    mhs_text = str(mhs_skills).lower()
    job_text = str(job_skills).lower()

    # Cari skill IT yang dibutuhkan job
    job_skills_needed = [s for s in IT_SKILL_TERMS if s in job_text]

    if not job_skills_needed:
        return {
            'covered':     [],
            'not_covered': [],
            'score':       0,
            'grade':       'N/A'
        }

    # Cek mana yang sudah tercover oleh mahasiswa
    covered     = [s for s in job_skills_needed if s in mhs_text]
    not_covered = [s for s in job_skills_needed if s not in mhs_text]

    score = len(covered) / len(job_skills_needed) * 100

    if score >= 60:
        grade = 'Tinggi'
    elif score >= 30:
        grade = 'Sedang'
    else:
        grade = 'Rendah'

    return {
        'covered':     covered,
        'not_covered': not_covered,
        'score':       score,
        'grade':       grade
    }


# ══════════════════════════════════════════════════════════════════════════════
# FUNGSI 3: Per Mata Kuliah Pattern Analysis
# Analisis agregat dari semua top job yang direkomendasikan
# ══════════════════════════════════════════════════════════════════════════════

def analyze_mk_pattern(top_kandidat: list, mhs_skills: str) -> dict:
    """
    Analisis pattern dari semua job yang direkomendasikan untuk satu mata kuliah.

    Returns dict dengan:
    - skill_gap_terbanyak: skill IT yang paling sering jadi gap
    - skill_match_terbanyak: skill yang paling sering match
    - role_distribution: distribusi kategori role job
    - avg_coverage: rata-rata coverage score
    """
    from collections import Counter
    from backend.src.course_recommender import classify_role

    all_gaps    = []
    all_matches = []
    all_roles   = []
    all_scores  = []

    for k in top_kandidat:
        job_skills = str(k['job']['job_skills'])

        # Coverage
        cov = skill_coverage_score(mhs_skills, job_skills)
        all_scores.append(cov['score'])
        all_gaps.extend(cov['not_covered'])
        all_matches.extend(cov['covered'])

        # Role
        role = classify_role(str(k['job']['title']))
        all_roles.append(role)

    # Hitung frekuensi
    gap_counter   = Counter(all_gaps)
    match_counter = Counter(all_matches)
    role_counter  = Counter(all_roles)

    return {
        'skill_gap_terbanyak':   gap_counter.most_common(5),
        'skill_match_terbanyak': match_counter.most_common(5),
        'role_distribution':     role_counter.most_common(),
        'avg_coverage':   np.mean(all_scores) if all_scores else 0,
    }

# ══════════════════════════════════════════════════════════════════════════════
# UPDATE fungsi rekomendasi_kerja() — tambahkan di dalam loop for rank
# ══════════════════════════════════════════════════════════════════════════════

# Di dalam loop for rank, setelah print Penjelasan EBM, tambahkan:

"""
        ── Skill Match Highlight ─────────────────────────────────────────────
        match_info = highlight_skill_match(skill_mahasiswa, str(job['job_skills']))
        cov_info   = skill_coverage_score(skill_mahasiswa, str(job['job_skills']))

        print(f"   Skill Match        : {len(match_info['matched'])} kata cocok "
            f"({match_info['match_pct']:.1f}% overlap)")
        if match_info['matched']:
            matched_display = ', '.join(match_info['matched'][:6])
            print(f"   Kata yang Match    : {matched_display}")

        print(f"   IT Coverage Score  : {cov_info['score']:.1f}% ({cov_info['grade']})")
        if cov_info['covered']:
            print(f"   Skill Tercover     : {', '.join(cov_info['covered'][:5])}")
        if cov_info['not_covered']:
            print(f"   Skill Belum Cover  : {', '.join(cov_info['not_covered'][:5])}")
"""

# ══════════════════════════════════════════════════════════════════════════════
# UPDATE fungsi rekomendasi_kerja() — tambahkan SETELAH loop for rank
# ══════════════════════════════════════════════════════════════════════════════

"""
    # ── Pattern Analysis per Mata Kuliah ──────────────────────────────────────
    print(f"\n{'='*65}")
    print(f" Analisis Pattern — {nama_mk}")
    print(f"{'='*65}")

    pattern = analyze_mk_pattern(top_kandidat, skill_mahasiswa)

    print(f"\n Rata-rata IT Coverage Score : {pattern['avg_coverage']:.1f}%")

    print(f"\n Distribusi Role Job:")
    for role, count in pattern['role_distribution']:
        bar = '' * count
        print(f"   {role:<20} : {bar} ({count} job)")

    print(f"\n Skill yang Sering Match (sudah tercover kurikulum):")
    for skill, freq in pattern['skill_match_terbanyak']:
        print(f"   • {skill:<25} muncul di {freq}/{len(top_kandidat)} job")

    print(f"\n  Skill Gap Terbanyak (belum tercover kurikulum):")
    for skill, freq in pattern['skill_gap_terbanyak']:
        print(f"   • {skill:<25} dibutuhkan {freq}/{len(top_kandidat)} job")
"""