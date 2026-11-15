# src/course_recommender.py
# Role-Aware Course Recommendation Engine
# Digunakan oleh recommendation_system.py
# ──────────────────────────────────────────────────────────────────────────────

import ast
import pandas as pd

# ══════════════════════════════════════════════════════════════════════════════
# 1. ROLE TAXONOMY
#    Mapping: job title keyword → kategori role → core skills → exclude skills
# ══════════════════════════════════════════════════════════════════════════════

ROLE_TAXONOMY = {

    'mobile_developer': {
        'keywords': [
            'mobile', 'android', 'ios', 'flutter', 'react native',
            'kotlin', 'swift', 'ionic', 'bergerak'
        ],
        'core_skills': [
            'mobile development', 'android', 'ios', 'flutter',
            'javascript', 'react', 'api', 'database', 'git',
            'computer programming'
        ],
        'exclude_skills': [
            'deep learning', 'machine learning algorithms',
            'leadership and management', 'supply chain',
            'data science', 'big data'
        ]
    },
     'support': {
        'keywords': [
            'support', 'helpdesk', 'technical support', 'noc',
            'it staff', 'staf it',  'staff it', 
            'infrastructure', 'network engineer',
            'hardware', 'noc staff',  'hardware & software',  'staff it (',
        ],
        'core_skills': [
            'computer networking', 'network architecture', 'linux',
            'cloud computing', 'computer security incident management',
            'network model', 'networking hardware', 'python programming'
        ],
        'exclude_skills': [
            'deep learning', 'machine learning algorithms',
            'mobile development', 'html and css', 'supply chain',
        ]
    },
    'data_engineer': {
        'keywords': [
            'data engineer', 'data architect', 'database architect',
            'etl', 'warehouse', 'big data', 'data platform', 'dba'
        ],
        'core_skills': [
            'sql', 'databases', 'cloud computing', 'python programming',
            'big data', 'data management', 'extract', 'database administration',
            'cloud platforms', 'google cloud platform'
        ],
        'exclude_skills': [
            'mobile development', 'html and css', 'leadership and management',
            'supply chain', 'deep learning'
        ]
    },

    'data_scientist': {
        'keywords': [
            'data scientist', 'machine learning', 'ai engineer',
            'ml engineer', 'deep learning', 'nlp', 'computer vision',
            'artificial intelligence', 'kecerdasan'
        ],
        'core_skills': [
            'python programming', 'machine learning', 'deep learning',
            'machine learning algorithms', 'data analysis', 'sql',
            'cloud computing', 'applied machine learning', 'tensorflow',
            'human learning', 'statistical programming'
        ],
        'exclude_skills': [
            'mobile development', 'html and css',
            'leadership and management', 'supply chain'
        ]
    },

    'analyst': {
        'keywords': [
            'analyst', 'business analyst', 'system analyst',
            'it analyst', 'solution analyst', 'odoo analyst',
            'system analis', 'junior system'
        ],
        'core_skills': [
            'sql', 'data analysis', 'databases', 'python programming',
            'software engineering', 'computer programming',
            'agile software development', 'data management',
            'business analysis', 'data visualization'
        ],
        'exclude_skills': [
            'deep learning', 'mobile development', 'tensorflow',
            'leadership and management', 'supply chain', 'big data'
        ]
    },

    'manager': {
        'keywords': [
            'manager', 'lead', 'head', 'director', 'chief',
            'vp', 'coordinator', 'supervisor', 'officer', 'project', 'sr. officer',
        ],
        'core_skills': [
            'project management', 'agile software development',
            'cloud computing', 'software engineering',
            'scrum (software development)', 'planning',
            'leadership and management', 'python programming'
        ],
        'exclude_skills': [
            'deep learning', 'mobile development', 'html and css',
            'tensorflow', 'supply chain', 'big data'
        ]
    },

    'consultant': {
        'keywords': [
            'consultant', 'architecture', 'enterprise', 'solution architect',
            'advisor', 'specialist', 'it consultant'
        ],
        'core_skills': [
            'cloud computing', 'software engineering', 'python programming',
            'agile software development', 'databases', 'sql',
            'computer programming', 'cloud platforms'
        ],
        'exclude_skills': [
            'deep learning', 'mobile development', 'html and css',
            'tensorflow', 'supply chain'
        ]
    },

    'security': {
        'keywords': [
            'security', 'cyber', 'penetration', 'soc',
            'network security', 'information security', 'cybersecurity'
        ],
        'core_skills': [
            'network security', 'linux', 'python programming',
            'cryptography', 'cloud computing', 'sql',
            'computer security incident management', 'risk management',
            'network architecture', 'audit'
        ],
        'exclude_skills': [
            'mobile development', 'html and css', 'deep learning',
            'supply chain', 'leadership and management'
        ]
    },
       'developer': {
        'keywords': [
            'developer', 'programmer', 'engineer', 'software',
            'frontend', 'backend', 'fullstack', 'full stack',
            'web developer', 'coding', 'low code', 'it programmer'
        ],
        'core_skills': [
            'python programming', 'javascript', 'sql', 'databases',
            'computer programming', 'html and css', 'api',
            'software engineering', 'cloud computing', 'git'
        ],
        'exclude_skills': [
            'deep learning', 'machine learning algorithms',
            'leadership and management', 'supply chain',
            'data science', 'big data'
        ]
    },
    'prompter': {
        'keywords': [
            'prompt', 'ai prompter', 'generative', 'content creator',
            'low code', 'no code'
        ],
        'core_skills': [
            'machine learning', 'python programming', 'cloud computing',
            'applied machine learning', 'computer programming',
            'data analysis', 'human learning'
        ],
        'exclude_skills': [
            'supply chain', 'leadership and management',
            'mobile development', 'html and css'
        ]
    }, 
        'designer': {
        'keywords': [
            'ui', 'ux', 'designer', 'ui/ux', 'product designer',
            'graphic', 'visual designer'
        ],
        'core_skills': [
            'python programming', 'computer programming',
            'software engineering', 'databases', 'sql',
            'agile software development', 'data analysis'
        ],
        'exclude_skills': [
            'deep learning', 'mobile development',
            'machine learning algorithms', 'supply chain',
            'big data', 'tensorflow'
        ]
    },
    
}


# ══════════════════════════════════════════════════════════════════════════════
# 2. SKILL → COURSE MAPPING
#    Mapping: skill yang dibutuhkan → list kursus Coursera yang relevan
# ══════════════════════════════════════════════════════════════════════════════

SKILL_COURSE_MAP = {
    # ── Programming ───────────────────────────────────────────────────────────
    'python programming':       ['Meta Back-End Developer',
                                 'IBM Full Stack Software Developer',
                                 'IBM Data Science'],
    'javascript':               ['Meta Front-End Developer',
                                 'Meta Back-End Developer'],
    'html and css':             ['Meta Front-End Developer',
                                 'Meta Back-End Developer'],
    'computer programming':     ['Meta Back-End Developer',
                                 'IBM Full Stack Software Developer'],
    'software engineering':     ['IBM DevOps and Software Engineering',
                                 'IBM Full Stack Software Developer'],
    'computer networking':      ['Google IT Support', 'IBM IT Support'],
    'network architecture':     ['Google IT Support'],
    'networking hardware':      ['Google IT Support'],
    'linux':                    ['Google Cybersecurity', 'Google IT Support'],

    # ── Database ──────────────────────────────────────────────────────────────
    'sql':                      ['Meta Database Engineer',
                                 'IBM Data Engineering',
                                 'Meta Back-End Developer'],
    'databases':                ['Meta Database Engineer',
                                 'IBM Data Warehouse Engineer',
                                 'IBM Data Engineering'],
    'database administration':  ['IBM Data Engineering',
                                 'IBM Data Warehouse Engineer'],
    'data management':          ['IBM Data Engineering',
                                 'IBM Data Warehouse Engineer'],

    # ── Cloud ─────────────────────────────────────────────────────────────────
    'cloud computing':          ['AWS Fundamentals',
                                 'Google Cloud Digital Leader Training',
                                 'Microsoft Azure Fundamentals AZ-900 Exam Prep',
                                 'IBM Full Stack Software Developer'],
    'cloud platforms':          ['Preparing for Google Cloud Certification: Cloud Data Engineer',
                                 'AWS Cloud Technology Consultant'],
    'google cloud platform':    ['Preparing for Google Cloud Certification: Cloud Data Engineer',
                                 'Google Cloud Digital Leader Training'],
    'amazon web services':      ['AWS Fundamentals',
                                 'AWS Cloud Technology Consultant'],
    'microsoft azure':          ['Microsoft Azure Fundamentals AZ-900 Exam Prep'],
    'cloud applications':       ['IBM Full Stack Software Developer',
                                 'Cloud Application Development Foundations'],

    # ── Data & ML ─────────────────────────────────────────────────────────────
    'machine learning':         ['IBM Machine Learning',
                                 'IBM AI Engineering',
                                 'IBM Data Science'],
    'deep learning':            ['Deep Learning',
                                 'IBM AI Engineering'],
    'machine learning algorithms': ['IBM Machine Learning',
                                    'Deep Learning'],
    'applied machine learning': ['IBM AI Engineering',
                                 'Preparing for Google Cloud Certification: Machine Learning Engineer'],
    'data analysis':            ['Google Data Analytics',
                                 'IBM Data Science'],
    'data visualization':       ['Google Data Analytics'],
    'big data':                 ['Data Engineering, Big Data, and Machine Learning on GCP',
                                 'Preparing for Google Cloud Certification: Cloud Data Engineer'],
    'statistical programming':  ['IBM Data Science',
                                 'Meta Database Engineer'],
    'extract':                  ['IBM Data Engineering'],

    # ── DevOps & Agile ────────────────────────────────────────────────────────
    'agile software development': ['IBM IT Scrum Master',
                                   'IBM IT Project Manager',
                                   'IBM DevOps and Software Engineering'],
    'scrum (software development)': ['IBM IT Scrum Master'],
    'devops':                   ['IBM DevOps and Software Engineering'],
    'project management':       ['IBM IT Project Manager'],

    # ── Mobile ────────────────────────────────────────────────────────────────
    'mobile development':       ['Meta Android Developer',
                                 'Meta iOS Developer'],
    'android':                  ['Meta Android Developer'],
    'ios':                      ['Meta iOS Developer'],
    'react (web framework)':    ['Meta Android Developer',
                                 'Meta Front-End Developer'],
    'mobile development tools': ['Meta Android Developer'],

    # ── Network & Security ────────────────────────────────────────────────────
    'network security':         ['Google Cybersecurity',
                                 'Microsoft Cybersecurity Analyst'],
    'computer networking':      ['Google IT Support',
                                 'IBM IT Support'],
    'network architecture':     ['Google IT Support'],
    'networking hardware':      ['Google IT Support'],
    'linux':                    ['Google Cybersecurity',
                                 'Google IT Support'],
    'cryptography':             ['Google Cybersecurity'],
    'risk management':          ['Google Cybersecurity'],
    'audit':                    ['Google Cybersecurity'],
    'computer security incident management': ['Google Cybersecurity'],

    # ── Support ───────────────────────────────────────────────────────────────
    'network model':            ['Google IT Support'],
    'human learning':           ['IBM AI Engineering',
                                 'IBM Machine Learning'],
    'ibm cloud':                ['Cloud Application Development Foundations',
                                 'IBM Full Stack Software Developer'],
}


# ══════════════════════════════════════════════════════════════════════════════
# 3. HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def parse_skills_coursera(skill_str: str) -> list:
    """Parse kolom Skills dari Coursera."""
    try:
        skills = ast.literal_eval(skill_str)
        return [s.strip().lower() for s in skills]
    except Exception:
        return [s.strip().lower() for s in str(skill_str).split(',')]


def classify_role(job_title: str) -> str:
    """Deteksi kategori role dari job title."""
    title_lower = job_title.lower()
    for role, config in ROLE_TAXONOMY.items():
        if any(kw in title_lower for kw in config['keywords']):
            return role
    return 'developer'  # default fallback


def extract_skill_gap(mhs_skills: str, role: str) -> list:
    """
    Hitung skill gap: skill yang dibutuhkan role
    tapi belum ada di skills mahasiswa.
    """
    mhs_words   = set(mhs_skills.lower().split())
    core_skills = ROLE_TAXONOMY[role]['core_skills']

    gaps = []
    for skill in core_skills:
        skill_words = set(skill.lower().split())
        # Skill dianggap gap kalau tidak ada satupun kata skill di skills mhs
        if not skill_words.intersection(mhs_words):
            gaps.append(skill)

    return gaps


def get_course_skills(course_title: str, df_coursera: pd.DataFrame) -> list:
    """Ambil list skills dari kursus berdasarkan judulnya."""
    row = df_coursera[df_coursera['Title'] == course_title]
    if row.empty:
        return []
    return parse_skills_coursera(row.iloc[0]['Skills'])


# ══════════════════════════════════════════════════════════════════════════════
# 4. MAIN FUNCTION: Role-Aware Course Recommendation
# ══════════════════════════════════════════════════════════════════════════════

def rekomendasikan_kursus_v2(skill_mahasiswa: str,
                              job_title: str,
                              df_coursera: pd.DataFrame,
                              top_n: int = 2) -> dict:
    """
    Role-aware course recommendation.

    Returns dict:
    {
        'role':       str,           # kategori role yang terdeteksi
        'skill_gaps': list[str],     # skill yang kurang
        'kursus':     list[dict],    # rekomendasi kursus + alasan
        'pesan':      str            # pesan jika tidak ada gap
    }
    """
    # ── 1. Classify role ──────────────────────────────────────────────────────
    role        = classify_role(job_title)
    role_config = ROLE_TAXONOMY[role]

    # ── 2. Hitung skill gap ───────────────────────────────────────────────────
    skill_gaps = extract_skill_gap(skill_mahasiswa, role)

    if not skill_gaps:
       return {
            'role':       role,
            'skill_gaps': [],
            'kursus':     [],
            'pesan':      'Skill mahasiswa sudah sesuai dengan role ini'
        }
    

    # ── 3. Cari kursus dari SKILL_COURSE_MAP ──────────────────────────────────
    exclude_skills = set(role_config['exclude_skills'])

    # kursus_scores: title → {covered_gaps, score}
    kursus_scores = {}

    for gap_skill in skill_gaps:
        # Cari di SKILL_COURSE_MAP — exact match atau partial match
        matched_courses = []
        for skill_key, courses in SKILL_COURSE_MAP.items():
            if skill_key == gap_skill or skill_key in gap_skill or gap_skill in skill_key:
                matched_courses.extend(courses)

        for course_title in matched_courses:
            # Ambil skills kursus dari dataframe
            course_skills = get_course_skills(course_title, df_coursera)
            if not course_skills:
                continue

            course_skills_str = ' '.join(course_skills)

            # Skip kalau kursus mengandung skill yang di-exclude untuk role ini
            if any(ex in course_skills_str for ex in exclude_skills):
                continue

            if course_title not in kursus_scores:
                kursus_scores[course_title] = {
                    'covered_gaps': [],
                    'score':        0,
                    'skills':       course_skills[:4]
                }

            kursus_scores[course_title]['covered_gaps'].append(gap_skill)
            kursus_scores[course_title]['score'] += 1

    # ── 4. Sort by score (jumlah gap yang di-cover) ───────────────────────────
    sorted_kursus = sorted(
        kursus_scores.items(),
        key=lambda x: x[1]['score'],
        reverse=True
    )[:top_n]

    # ── 5. Format output ──────────────────────────────────────────────────────
    hasil_kursus = []
    for title, info in sorted_kursus:
        covered = info['covered_gaps']
        hasil_kursus.append({
            'title':       title,
            'skills':      ', '.join(info['skills']),
            'covers_gaps': covered,
            'alasan':      f"Menutup skill gap: {', '.join(covered)}"
        })

    return {
        'role':       role,
        'skill_gaps': skill_gaps,
        'kursus':     hasil_kursus,
        'pesan':      'Kursus spesifik untuk role ini belum tersedia di dataset Coursera' if not hasil_kursus else ''
    }