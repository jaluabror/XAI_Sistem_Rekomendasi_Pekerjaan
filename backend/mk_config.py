# ══════════════════════════════════════════════════════════════════════════════
# mk_config.py — Konfigurasi Kategorisasi MK + Title Case Normalization
# Taruh di folder src/ atau di root proyek bersama app.py
# ══════════════════════════════════════════════════════════════════════════════

# ── Title Case Mapping — semua nama MK dinormalisasi ─────────────────────────
MK_TITLE_CASE = {
    # IT Spesifik
    "ADOPSI TEKNOLOGI INFORMASI":                   "Adopsi Teknologi Informasi",
    "Algoritma dan Pemrograman":                    "Algoritma dan Pemrograman",
    "RPS PBO":                                      "Pemrograman Berorientasi Objek",
    "Arsitektur dan Pengembangan Backend":          "Arsitektur dan Pengembangan Backend",
    "Pengembangan Aplikasi Website":                "Pengembangan Aplikasi Website",
    "Pengembangan Aplikasi Bergerak":               "Pengembangan Aplikasi Bergerak",
    "PENGEMBANGAN UI LANJUT":                       "Pengembangan UI Lanjut",
    "JARINGAN KOMPUTER":                            "Jaringan Komputer",
    "Sistem Operasi":                               "Sistem Operasi",
    "Keamanan Sistem Informasi":                    "Keamanan Sistem Informasi",
    "Komputasi Awan":                               "Komputasi Awan",
    "Penambangan Data":                             "Penambangan Data",
    "Kecerdasan Artifisial dan Penerapannya":       "Kecerdasan Artifisial dan Penerapannya",
    "Data Warehouse dan Business Intelligence":     "Data Warehouse dan Business Intelligence",
    "SISTEM BASIS DATA (1)":                        "Sistem Basis Data",

    # IT Umum
    "Analisis dan Perancangan Sistem Informasi":    "Analisis dan Perancangan Sistem Informasi",
    "Arsitektur Enterprise":                        "Arsitektur Enterprise",
    "IMPLEMENTASI ARSITEKTUR ENTERPRISE":           "Implementasi Arsitektur Enterprise",
    "INTEGRASI APLIKASI ENTERPRISE":                "Integrasi Aplikasi Enterprise",
    "Sistem Enterprise":                            "Sistem Enterprise",
    "Manajemen Data Enterprise":                    "Manajemen Data Enterprise",
    "Sistem Manajemen Hubungan Pelaggan":           "Sistem Manajemen Hubungan Pelanggan",
    "MANAJEMEN PROYEK SISTEM INFORMASI":            "Manajemen Proyek Sistem Informasi",
    "Tata Kelola dan Manajemen Teknologi Informasi":"Tata Kelola dan Manajemen Teknologi Informasi",
    "Pemodelan Proses Bisnis":                      "Pemodelan Proses Bisnis",
    "Pengantaran Sistem Informasi":                 "Pengantaran Sistem Informasi",
    "PENGUJIAN DAN IMPLEMENTASI SISTEM":            "Pengujian dan Implementasi Sistem",
    "Proyek Perangkat Lunak":                       "Proyek Perangkat Lunak",
    "Perancangan Interaksi":                        "Perancangan Interaksi",
    "PEMERINTAHAN ELEKTRONIK DAN KOTA CERDAS":     "Pemerintahan Elektronik dan Kota Cerdas",
    "DESIGN THINKING":                              "Design Thinking",
    "Capstone Design & Project":                    "Capstone Design & Project",
    "PELATIHAN DAN SERTIFIKASI":                    "Pelatihan dan Sertifikasi",
    "Kerja Praktek dan Pengabdian Masyarakat":      "Kerja Praktek dan Pengabdian Masyarakat",
    "Matematika Diskrit":                           "Matematika Diskrit",
    "PROBABILITAS DAN STATISTIK":                   "Probabilitas dan Statistik",
    # Non-IT
    "BAHASA INDONESIA":                             "Bahasa Indonesia",
    "Bahasa Inggris II":                            "Bahasa Inggris",
    "Pancasila":                                    "Pancasila",
    "Etika Profesi":                                "Etika Profesi",
    "Internalisasi Budaya dan Pembentukan Karakter":"Internalisasi Budaya dan Pembentukan Karakter",
    "Kewirausahaan":                                "Kewirausahaan",
    "Kepemimpinan dan Komunikasi Interpersonal":    "Kepemimpinan dan Komunikasi Interpersonal",
    "MANAJEMEN RANTAI PASOK":                       "Manajemen Rantai Pasok",
    "MANAJEMEN SUMBER DAYA MANUSIA":                "Manajemen Sumber Daya Manusia",
    "Matematika Untuk Sistem Informasi":            "Matematika untuk Sistem Informasi",
    "Statistika Industri":                          "Statistika Industri",
    "METODE PENELITIAN DAN PENYUSUNAN KARYA ILMIAH ": "Metode Penelitian dan Penyusunan Karya Ilmiah",
}

def normalize_mk_name(mk: str) -> str:
    """Normalisasi nama MK ke Title Case yang konsisten."""
    return MK_TITLE_CASE.get(mk.strip(), mk.strip().title())


# ── Kategorisasi MK ───────────────────────────────────────────────────────────
MK_KATEGORI = {
    # 🔴 IT Spesifik — teknis, coding, infrastruktur murni
    "IT Spesifik": {
        "ADOPSI TEKNOLOGI INFORMASI",
        "Algoritma dan Pemrograman",
        "RPS PBO", 
        "Arsitektur dan Pengembangan Backend",
        "Pengembangan Aplikasi Website",
        "Pengembangan Aplikasi Bergerak",
        "PENGEMBANGAN UI LANJUT",
        "JARINGAN KOMPUTER",
        "Sistem Operasi",
        "Keamanan Sistem Informasi",
        "Komputasi Awan",
        "Penambangan Data",
        "Kecerdasan Artifisial dan Penerapannya",
        "Data Warehouse dan Business Intelligence",
    },

    # 🟡 IT Umum — domain SI, manajemen IT, enterprise, metodologi
    "IT Umum": {
        "Analisis dan Perancangan Sistem Informasi",
        "Arsitektur Enterprise",
        "IMPLEMENTASI ARSITEKTUR ENTERPRISE",
        "INTEGRASI APLIKASI ENTERPRISE",
        "Sistem Enterprise",
        "Manajemen Data Enterprise",
        "Sistem Manajemen Hubungan Pelaggan",
        "MANAJEMEN PROYEK SISTEM INFORMASI",
        "Tata Kelola dan Manajemen Teknologi Informasi",
        "Pemodelan Proses Bisnis",
        "Pengantaran Sistem Informasi",
        "PENGUJIAN DAN IMPLEMENTASI SISTEM",
        "Proyek Perangkat Lunak",
        "Perancangan Interaksi",
        "ADOPSI TEKNOLOGI INFORMASI",
        "PEMERINTAHAN ELEKTRONIK DAN KOTA CERDAS",
        "DESIGN THINKING",
        "Capstone Design & Project",
        "PELATIHAN DAN SERTIFIKASI",
        "Kerja Praktek dan Pengabdian Masyarakat",
        "Matematika Diskrit",
        "PROBABILITAS DAN STATISTIK",
        "SISTEM BASIS DATA (1)",
    },

    # ⚫ Non-IT — general education
    "Non-IT": {
        "BAHASA INDONESIA",
        "Bahasa Inggris II",
        "Pancasila",
        "Etika Profesi",
        "Internalisasi Budaya dan Pembentukan Karakter",
        "Kewirausahaan",
        "Kepemimpinan dan Komunikasi Interpersonal",
        "MANAJEMEN RANTAI PASOK",
        "MANAJEMEN SUMBER DAYA MANUSIA",
        "Matematika Untuk Sistem Informasi",
        "Statistika Industri",
        "METODE PENELITIAN DAN PENYUSUNAN KARYA ILMIAH",
    },
}

# Reverse lookup: MK → kategori
MK_TO_KATEGORI = {}
for kat, mk_set in MK_KATEGORI.items():
    for mk in mk_set:
        MK_TO_KATEGORI[mk] = kat

def get_kategori(mk: str) -> str:
    """Return kategori MK: 'IT Spesifik', 'IT Umum', atau 'Non-IT'."""
    return MK_TO_KATEGORI.get(mk.strip(), "IT Umum")

def get_kategori_color(kategori: str) -> str:
    """Return warna hex per kategori untuk UI."""
    return {
        "IT Spesifik": "#E74C3C",
        "IT Umum":     "#F39C12",
        "Non-IT":      "#95A5A6",
    }.get(kategori, "#95A5A6")

def get_kategori_icon(kategori: str) -> str:
    return {
        "IT Spesifik": "🔴",
        "IT Umum":     "🟡",
        "Non-IT":      "⚫",
    }.get(kategori, "⚫")


# ── Default Top-N ─────────────────────────────────────────────────────────────
DEFAULT_TOP_N = 10

# Tambahkan ini di bagian paling bawah backend/mk_config.py

def get_kategori_realm(mk: str) -> str:
    """Return IS2020 realm label untuk keperluan laporan."""
    REALM_MAP = {
        "JARINGAN KOMPUTER": "Technology Realm",
        "Sistem Operasi": "Technology Realm",
        "Keamanan Sistem Informasi": "Technology Realm",
        "Komputasi Awan": "Technology Realm",
        "SISTEM BASIS DATA (1)": "Data Realm",
        "Penambangan Data": "Data Realm",
        "Kecerdasan Artifisial dan Penerapannya": "Data Realm",
        "Data Warehouse dan Business Intelligence": "Data Realm",
        "PROBABILITAS DAN STATISTIK": "Data Realm",
        "Manajemen Data Enterprise": "Data Realm",
        "Algoritma dan Pemrograman": "Development Realm",
        "RPS PBO": "Development Realm",
        "Arsitektur dan Pengembangan Backend": "Development Realm",
        "Pengembangan Aplikasi Website": "Development Realm",
        "Pengembangan Aplikasi Bergerak": "Development Realm",
        "PENGEMBANGAN UI LANJUT": "Development Realm",
        "Analisis dan Perancangan Sistem Informasi": "Development Realm",
        "PENGUJIAN DAN IMPLEMENTASI SISTEM": "Development Realm",
        "Perancangan Interaksi": "Development Realm",
        "Proyek Perangkat Lunak": "Development Realm",
        "Capstone Design & Project": "Development Realm",
        "Arsitektur Enterprise": "Integration Realm",
        "IMPLEMENTASI ARSITEKTUR ENTERPRISE": "Integration Realm",
        "INTEGRASI APLIKASI ENTERPRISE": "Integration Realm",
        "Sistem Enterprise": "Integration Realm",
        "Pemodelan Proses Bisnis": "Integration Realm",
        "PEMERINTAHAN ELEKTRONIK DAN KOTA CERDAS": "Integration Realm",
        "MANAJEMEN PROYEK SISTEM INFORMASI": "Organizational Realm",
        "Tata Kelola dan Manajemen Teknologi Informasi": "Organizational Realm",
        "Sistem Manajemen Hubungan Pelaggan": "Organizational Realm",
        "DESIGN THINKING": "Organizational Realm",
        "Pengantaran Sistem Informasi": "IS Foundations",
        "ADOPSI TEKNOLOGI INFORMASI": "IS Foundations",
        "Etika Profesi": "IS Foundations",
        "PELATIHAN DAN SERTIFIKASI": "IS Foundations",
        "Kerja Praktek dan Pengabdian Masyarakat": "IS Foundations",
    }
    return REALM_MAP.get(mk.strip(), "General Education")