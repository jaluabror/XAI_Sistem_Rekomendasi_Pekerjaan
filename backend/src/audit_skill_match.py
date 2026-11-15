import json
from collections import Counter

data = json.loads(open(r'C:\xampp\htdocs\Proyek\OBE-Recommendation\outputs\semua_hasil_rekomendasi.json').read())

# Kumpulkan semua kata match
all_matched = []
per_mk = {}

for mk, hasil in data.items():
    if not hasil or 'top_jobs' not in hasil:
        continue
    mk_words = []
    for job in hasil['top_jobs']:
        words = job.get('skill_match', [])
        all_matched.extend(words)
        mk_words.extend(words)
    per_mk[mk] = Counter(mk_words)

word_counter = Counter(all_matched)

# Kategorikan manual
TEKNIS = {
    'html', 'css', 'java', 'python', 'javascript', 'sql', 'php', 'kotlin',
    'swift', 'golang', 'react', 'angular', 'vue', 'flutter', 'django',
    'laravel', 'spring', 'nodejs', 'typescript', 'ruby', 'scala', 'rust',
    'mysql', 'postgresql', 'mongodb', 'oracle', 'nosql', 'database', 'redis',
    'aws', 'gcp', 'azure', 'cloud', 'docker', 'kubernetes', 'jenkins',
    'devops', 'linux', 'git', 'machine learning', 'deep learning',
    'tensorflow', 'pytorch', 'data science', 'pandas', 'numpy', 'tableau',
    'networking', 'firewall', 'cisco', 'mikrotik', 'routing', 'switching',
    'cybersecurity', 'wireshark', 'bootstrap', 'rest api', 'graphql',
    'microservices', 'android', 'ios', 'mobile development', 'web development',
    'agile', 'scrum', 'jira', 'uml', 'system analysis', 'business analysis',
    'project management', 'waterfall', 'sdlc', 'togaf', 'archimate',
    # Domain teknis bermakna
    'enterprise', 'architecture', 'arsitektur', 'pemrograman', 'software',
    'jaringan', 'mining', 'mobile', 'backend', 'network', 'diagram',
    'infrastructure', 'layer', 'flowchart', 'cobit', 'json', 'rest',
    'website', 'html', 'java', 'pemrograman', 'togaf', 'archimate',
}

print('SEMUA KATA MATCH — AUDIT LENGKAP:')
print('='*70)
print(f'Total unique kata: {len(word_counter)}')
print()

umum = []
teknis_list = []
borderline = []

for word, freq in word_counter.most_common(200):
    if word in TEKNIS:
        teknis_list.append((word, freq))
    else:
        # Cek apakah kata ini bermakna atau tidak
        umum.append((word, freq))

print('⚠️  KATA UMUM/NON-TEKNIS (perlu masuk STOPWORDS):')
print('-'*70)
for word, freq in umum:
    print(f'  {word:<35} : {freq}x')

print()
print('✅ KATA TEKNIS (pertahankan):')
print('-'*70)
for word, freq in teknis_list:
    print(f'  {word:<35} : {freq}x')