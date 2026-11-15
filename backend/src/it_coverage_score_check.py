import json
from collections import Counter

with open(r'C:\xampp\htdocs\Proyek\OBE-Recommendation\outputs\semua_hasil_rekomendasi.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    
with open(r'C:\xampp\htdocs\Proyek\OBE-Recommendation\outputs\it_coverage_check.json', 'w', encoding='utf-8') as out:
    json.dump(data, out, indent=4, ensure_ascii=False)
    
results = []
for mk, hasil in data.items():
    if not hasil or 'top_jobs' not in hasil:
        continue
    scores = [j.get('coverage_score', 0) for j in hasil['top_jobs']]
    avg = sum(scores) / len(scores) if scores else 0
    all_covered = []
    all_gap = []
    roles = []
    for j in hasil['top_jobs']:
        all_covered.extend(j.get('skill_tercover', []))
        all_gap.extend(j.get('skill_gap', []))
        roles.append(j.get('role_detected', 'N/A'))
    
    results.append({
        'mk': mk,
        'avg': round(avg, 1),
        'covered': Counter(all_covered).most_common(5),
        'gap': Counter(all_gap).most_common(5),
        'roles': Counter(roles).most_common(3),
        'pattern': hasil.get('pattern', {})
    })

results.sort(key=lambda x: x['avg'], reverse=True)

# Kategorikan MK
it_core = []      # MK IT inti dengan coverage > 0
it_low = []       # MK IT tapi coverage 0
non_it = []       # MK non-IT

NON_IT_MK = {
    'Bahasa Indonesia', 'Bahasa Inggris II', 'Pancasila',
    'Etika Profesi', 'Internalisasi Budaya dan Pembentukan Karakter',
    'Kewirausahaan', 'Kepemimpinan dan Komunikasi Interpersonal',
    'Kerja Praktek dan Pengabdian Masyarakat', 'PELATIHAN DAN SERTIFIKASI',
    'Statistika Industri', 'Matematika Diskrit',
    'Matematika Untuk Sistem Informasi', 'PROBABILITAS DAN STATISTIK',
    'Capstone Design & Project', 'METODE PENELITIAN DAN PENYUSUNAN KARYA ILMIAH '
}

for r in results:
    if r['mk'] in NON_IT_MK:
        non_it.append(r)
    elif r['avg'] > 0:
        it_core.append(r)
    else:
        it_low.append(r)

print(f'Total MK: {len(results)}')
print(f'MK IT dengan coverage > 0% : {len(it_core)}')
print(f'MK IT dengan coverage = 0% : {len(it_low)}')
print(f'MK Non-IT                  : {len(non_it)}')
print()

print('='*80)
print('✅ MK IT — COVERAGE VALID (ada skill yang tercover)')
print('='*80)
for r in it_core:
    grade = '🟢' if r['avg'] >= 60 else ('🟡' if r['avg'] >= 30 else '🔴')
    covered_str = ', '.join([f"{s}({f}x)" for s, f in r['covered'][:3]])
    gap_str = ', '.join([s for s,f in r['gap'][:3]])

    print(f"{grade} {r['mk'][:50]:<50} : {r['avg']:>5.1f}%")
    print(f"   ✅ Tercover: {covered_str}")
    print(f"   ⚠️  Gap    : {gap_str}")

    print()
    print('='*80)
    print('⚫ MK IT — COVERAGE 0% (perlu investigasi)')
    print('='*80)
    for r in it_low:
            gap_str = ', '.join([s for s,f in r['gap'][:4]])
            print(f"⚫ {r['mk'][:50]:<50} : 0.0%")
            print(f"   ⚠️  Gap: {gap_str}")

    print()
    print('='*80)
    print('📚 MK NON-IT — Coverage 0% (valid/expected)')
    print('='*80)
    for r in non_it:
        gap_str = ', '.join([s for s,f in r['gap'][:3]]) if r['gap'] else '-'
        print(f"📚 {r['mk'][:50]:<50} : {r['avg']:>5.1f}%")
        if gap_str != '-':
            print(f"   ℹ️  Skill IT dibutuhkan job tapi tidak di CLO: {gap_str}")
