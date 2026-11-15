'use client';

import { useState, useEffect } from 'react';
import { BookOpenText, GraduationCap, LayoutDashboard, ChartBarDecreasing, Cpu, BriefcaseBusiness, MapPin } from 'lucide-react';
import Link from 'next/link';
import { ThemeProvider } from "@/components/theme-provider";

interface Course {
  display_name: string;
  actual_name: string;
}

interface Metrics {
  total_courses: number;
  average_coverage: string;
  top_skill_gap: string;           
  top_skill_gap_mk_count: number;    
  unique_roles: number;
}

export default function Dashboard() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<string>('');
  const [metrics, setMetrics] = useState<Metrics>({
    total_courses: 0,
    average_coverage: '0%',
    top_skill_gap: '-',
    top_skill_gap_mk_count: 0,
    unique_roles: 0
  });
  
  const [recommendations, setRecommendations] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // 1. Ambil list semua mata kuliah saat pertama kali load halaman
  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/courses')
      .then((res) => res.json())
      .then((data) => {
        setCourses(data);
        if (data.length > 0) {
          setSelectedCourse(data[0].actual_name);
        }
        setLoading(false);
      })
      .catch((err) => console.error("Gagal memuat daftar mata kuliah:", err));
  }, []);

  // 2. Fetch Metrik Global (Di-load sekali di awal untuk mengisi metrik makro prodi)
  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/metrics/global')
      .then((res) => res.json())
      .then((data) => {
        setMetrics({
          total_courses: data.total_courses,
          average_coverage: data.average_coverage,
          top_skill_gap: data.top_skill_gap,
          top_skill_gap_mk_count: data.top_skill_gap_mk_count,
          unique_roles: data.unique_roles
        });
      })
      .catch((err) => console.error("Gagal memuat metrik global:", err));
  }, []);

  // 3. Fungsi Pemicu untuk Memuat Data Rekomendasi Detail Per Mata Kuliah (EBM REGRESI)
  const handleFetchData = () => {
    if (!selectedCourse) return;
    
    fetch(`http://127.0.0.1:8000/api/recommendations/${encodeURIComponent(selectedCourse)}`)
      .then((res) => res.json())
      .then((data) => {
        setRecommendations(data);
      })
      .catch((err) => console.error("Gagal memuat data rekomendasi MK:", err));
  };

  // Otomatis jalankan fetch data lokal setiap kali dropdown mata kuliah diganti oleh user
  useEffect(() => {
    if (selectedCourse) {
      handleFetchData();
    }
  }, [selectedCourse]);

  if (loading) {
    return <div className="flex h-screen items-center justify-center font-medium bg-[#F5F7FA]">Memuat Next.js Engine...</div>;
  }

  return (
    <div className="flex min-h-screen bg-[#F5F7FA]">

      {/* ── CONTAINER UTAMA (Diberi margin-left agar tidak tertimpa Sidebar fixed) ── */}
      <div className="flex-1 min-h-screen flex flex-col">
        <main className="p-8 w-full max-w-[1400px] mx-auto flex-1">
          
          {/* HEADER DASHBOARD */}
          <div className="flex justify-between items-start mb-6">
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-slate-900">XAI Career</h1>
              <p className="text-xs font-medium text-slate-400 mt-0.5">Sistem Rekomendasi Karir Berbasis OBE</p>
            </div>
          </div>

          {/* UTILITY BAR ROW (Dropdown Interaktif Pilihan Mata Kuliah) */}
          <div className="flex gap-3 mb-6">
            <div className="flex-1 relative">
              <select 
                value={selectedCourse} 
                onChange={(e) => setSelectedCourse(e.target.value)}
                className="w-full h-11 pl-4 pr-10 bg-white border border-slate-200 rounded-xl text-sm font-medium appearance-none focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent shadow-sm text-slate-700 cursor-pointer"
              >
                {courses.map((course, idx) => (
                  <option key={idx} value={course.actual_name}>{course.display_name}</option>
                ))}
              </select>
              <div className="absolute inset-y-0 right-4 flex items-center pointer-events-none text-slate-400 text-xs">▼</div>
            </div>
          </div>

          {/* 4 CARDS METRIK HORIZONTAL */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
            {/* Card 1: Total Kuantitas Kurikulum */}
            <div className="relative p-6 bg-white border border-slate-100 rounded-2xl shadow-sm flex flex-col justify-between min-h-[125px]">
              <span className="absolute top-6 right-6 w-2 h-2 rounded-full bg-blue-500"></span>
              <p className="text-xs font-medium text-slate-400">Total Mata Kuliah</p>
              <h3 className="text-3xl font-bold text-slate-800 tracking-tight mt-1">{metrics.total_courses}</h3>
            </div>
            
            {/* Card 2: Rata-Rata Coverage Global */}
            <div className="relative p-6 bg-white border border-slate-100 rounded-2xl shadow-sm flex flex-col justify-between min-h-[125px]">
              <span className="absolute top-6 right-6 w-2 h-2 rounded-full bg-[#1D9E75]"></span>
              <p className="text-xs font-medium text-slate-400">Rata-rata Coverage</p>
              <h3 className="text-3xl font-bold text-slate-800 tracking-tight mt-1">{metrics.average_coverage}</h3>
            </div>
            
            {/* Card 3: Top Skill Gap Utama Tingkat Prodi (Global) */}
            <div className="relative p-6 bg-white border border-slate-100 rounded-2xl shadow-sm flex flex-col justify-between min-h-[125px]">
              <span className="absolute top-6 right-6 w-2 h-2 rounded-full bg-amber-500"></span>
              <p className="text-xs font-medium text-slate-400">Top Skill Gap</p>
              <h3 className="text-2xl font-extrabold text-slate-800 tracking-tight mt-1 capitalize truncate">
                {metrics.top_skill_gap}
              </h3>
              <p className="text-[11px] text-rose-500 font-medium mt-1">
                Ditemukan di {metrics.top_skill_gap_mk_count} Mata Kuliah IT
              </p>
            </div>
            
            {/* Card 4: Total Rumpun Pekerjaan Terdeteksi */}
            <div className="relative p-6 bg-white border border-slate-100 rounded-2xl shadow-sm flex flex-col justify-between min-h-[125px]">
              <span className="absolute top-6 right-6 w-2 h-2 rounded-full bg-blue-400"></span>
              <p className="text-xs font-medium text-slate-400">Total Role Tersedia</p>
              <h3 className="text-3xl font-bold text-slate-800 tracking-tight mt-1">
                {metrics?.unique_roles ?? 0}
              </h3>
            </div>
          </div>

          {/* ── TATA LETAK SPLIT VIEW (2 KOLOM RESPONSIVE) ── */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            
            {/* KOLOM KIRI (7/12 area): Output 10 Lowongan Kerja Regresi Terbaik */}
            <div className="lg:col-span-7 space-y-4">
              <h3 className="text-lg font-bold text-slate-800 mb-1">Top Rekomendasi Karir</h3>
              
              {recommendations && recommendations.top_jobs && recommendations.top_jobs.length > 0 ? (
                recommendations.top_jobs.map((job: any, index: number) => {
                  // SINKRONISASI AKTUAL VARIABEL MODEL REGRESI EBM (HANYA 2 VARIABEL)
                  const total_b = Math.abs(job.ebm_sim_bobot) + Math.abs(job.ebm_kw_bobot) || 1;
                  const sp = Math.round(Math.abs(job.ebm_sim_bobot) / total_b * 100);
                  const kp = Math.round(Math.abs(job.ebm_kw_bobot) / total_b * 100);

                  return (
                    <div key={index} className="p-6 bg-white border border-slate-100 rounded-2xl shadow-sm space-y-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className="font-bold text-slate-800 text-base">{job.title}</h4>
                          <p className="text-xs text-slate-400 mt-0.5">
                            <BriefcaseBusiness size={14} className="inline-block mr-1" />{job.company} &nbsp; &nbsp;
                            <MapPin size={14} className="inline-block mr-1" />{job.location}
                          </p>
                        </div>
                        {/* Tampilan Kontinu EBM Regresi (Composite Score) */}
                        {/* <span className="px-2.5 py-1 bg-emerald-50 text-[#1D9E75] border border-emerald-100 rounded-lg text-xs font-bold flex items-center gap-1">
                          Score: {job.composite_score?.toFixed(4)}
                        </span> */}
                      </div>
                      
                      {/* Meta-Informasi Kompetensi */}
                      <div className="flex flex-wrap gap-1.5">
                        <span className="px-2.5 py-1 bg-blue-50 text-[#378ADD] border border-blue-100 rounded-lg text-[11px] font-medium">Similarity: {job.similarity?.toFixed(0)}%</span>
                        <span className="px-2.5 py-1 bg-amber-50 text-[#BA7517] border border-amber-100 rounded-lg text-[11px] font-medium">IT Keywords: {job.job_kw_count}/10</span>
                      </div>

                      {/* EBM LOCAL EXPLANATION PROGRESS BARS */}
                      <div className="space-y-2.5 pt-2">
                        <p className="text-xs font-semibold text-slate-500">EBM Explanation</p>
                        <div className="space-y-2">
                          <div>
                            <div className="flex justify-between text-[13px] text-slate-400 mb-1">
                              <span>{job.faktor_dominan}</span>
                              <b>{sp}%</b>
                            </div>
                            <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
                              <div className="h-full bg-[#1D9E75] rounded-full transition-all duration-500" style={{width: `${sp}%`}}></div>
                            </div>
                          </div>
                          <div>
                            <div className="flex justify-between text-[11px] text-slate-400 mb-1">
                              <span>Kata Kunci IT</span>
                              <b>{kp}%</b>
                            </div>
                            <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
                              <div className="h-full bg-[#378ADD] rounded-full transition-all duration-500" style={{width: `${kp}%`}}></div>
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      {/* Badge Teks Dinamis Skill Match & Gap */}
                      <div className="pt-2 space-y-1.5 border-t border-slate-50">
                        {job.skill_match && job.skill_match.length > 0 && (
                          <div className="text-[11px]">
                            <span className="font-bold text-slate-400 mr-1">MATCH:</span> 
                            {job.skill_match.slice(0, 5).map((s: string, i: number) => (
                              <span key={i} className="inline-block px-1.5 py-0.5 bg-blue-50 text-blue-600 rounded mr-1 mb-1">{s}</span>
                            ))}
                          </div>
                        )}
                        {job.skill_gap && job.skill_gap.length > 0 && (
                          <div className="text-[11px]">
                            <span className="font-bold text-slate-400 mr-1">GAP:</span> 
                            {job.skill_gap.slice(0, 5).map((s: string, i: number) => (
                              <span key={i} className="inline-block px-1.5 py-0.5 bg-red-50 text-red-500 rounded mr-1 mb-1">{s}</span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className="p-6 bg-white border border-slate-100 rounded-2xl text-center text-sm text-slate-400">
                  CLO mata kuliah belum memiliki overlap signifikan dengan kualifikasi industri.
                </div>
              )}
            </div>

            {/* KOLOM KANAN (5/12 area): Analisis Pola/Pattern Frekuensi Kompetensi */}
            <div className="lg:col-span-5 space-y-4">
              <h3 className="text-lg font-bold text-slate-800 mb-1">Analisis Pattern Mata Kuliah</h3>
          
              <div className="p-6 bg-white border border-slate-100 rounded-2xl shadow-sm space-y-4">
                <p className="font-bold text-slate-800 text-base capitalize mt-0.5">
              {selectedCourse ? selectedCourse.toLowerCase().replace(/_/g, ' ') : '-'}
            </p>
                {recommendations && recommendations.pattern && recommendations.pattern.role_distribution ? (
                  <>
                    <div className="flex justify-between text-xs text-slate-400 font-medium pb-2 border-b border-slate-100">
                      <span>Distribusi Role dan Skill Gap</span>
                      <b className="text-slate-700">{Object.keys(recommendations.pattern.role_distribution).length} roles</b>
                    </div>
                    
                    {/* Render Bar Chart Distribusi Pekerjaan */}
                    <div className="space-y-3">
                      {Object.entries(recommendations.pattern.role_distribution).map(([role, freq]: any, idx) => {
                        const displayPct = Math.min(freq * 10, 100);
                        const barColors = ["#378ADD", "#1D9E75", "#BA7517", "#64748B"];
                        return (
                          <div key={idx}>
                            <div className="flex justify-between text-[11px] text-slate-500 mb-1">
                              <span className="capitalize">{role.replace('_', ' ')}</span>
                              <span className="font-semibold text-slate-700">{freq} Lowongan</span>
                            </div>
                            <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
                              <div className="h-full rounded-full transition-all duration-500" style={{ width: `${displayPct}%`, backgroundColor: barColors[idx % barColors.length] }}></div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                    
                    {/* Urutan 3 Teratas Akumulasi Match & Gap Berdasarkan Skema List Baru JSON */}
                    <div className="pt-4 border-t border-slate-100 space-y-2">
                      {recommendations.pattern.skill_match_top5 && recommendations.pattern.skill_match_top5.length > 0 && (
                        <div>
                          <p className="text-[10px] font-bold text-emerald-600 mb-1">MATCH TERBANYAK</p>
                          <div className="flex flex-wrap gap-1">
                            {recommendations.pattern.skill_match_top5.slice(0, 3).map((m: any, i: number) => (
                              <span key={i} className="px-2 py-0.5 bg-emerald-50 text-emerald-700 border border-emerald-100 text-[10px] rounded font-medium">
                                {m.skill} ({m.freq})
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      {recommendations.pattern.skill_gap_top5 && recommendations.pattern.skill_gap_top5.length > 0 && (
                        <div className="pt-1">
                          <p className="text-[10px] font-bold text-red-500 mb-1">GAP TERBANYAK</p>
                          <div className="flex flex-wrap gap-1">
                            {recommendations.pattern.skill_gap_top5.slice(0, 3).map((g: any, i: number) => (
                              <span key={i} className="px-2 py-0.5 bg-red-50 text-red-600 border border-red-100 text-[10px] rounded font-medium">
                                {g.skill} ({g.freq})
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </>
                ) : (
                  <div className="text-center text-sm text-slate-400 py-6">Memetakan pola penyerapan...</div>
                )}

                {/* Skor Coverage Khusus Mata Kuliah yang Dipilih */}
                <div className="pt-4 border-t border-slate-100 mt-4">
                  <h2 className="text-3xl font-extrabold text-slate-800 tracking-tight">
                    {recommendations?.pattern?.avg_coverage ?? "0"}% 
                    <span className="text-xs font-normal text-slate-400 ml-1">Mata Kuliah Coverage Score</span>
                  </h2>
                </div>
              </div>
            </div>

          </div>
        </main>
      </div>
      
    </div>
  );
}

