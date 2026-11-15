    'use client';

    import { useState, useEffect } from 'react';
    import { BookOpenText, LayoutDashboard, ChartBarDecreasing, Cpu } from 'lucide-react';
    import Link from 'next/link';

    interface Course {
    display_name: string;
    actual_name: string;
    }

    export default function ExplainabilityPage() {
    const [courses, setCourses] = useState<Course[]>([]);
    const [selectedCourse, setSelectedCourse] = useState<string>('');
    const [jobs, setJobs] = useState<any[]>([]);
    const [selectedRank, setSelectedRank] = useState<number>(1);
    const [jobDetail, setJobDetail] = useState<any>(null);
    const [loading, setLoading] = useState<boolean>(true);

    // 1. Fetch daftar mata kuliah awal (Menyaring metadata kotor)
    useEffect(() => {
        fetch('http://127.0.0.1:8000/api/courses')
        .then((res) => res.json())
        .then((data) => {
            // FILTER: Pastikan nama berkas metadata kotor tidak lolos masuk ke dropdown
            const filteredCourses = data.filter((c: Course) => !c.actual_name.strip?.().startsWith("_") && !c.actual_name.startsWith("_"));
            setCourses(filteredCourses);
            if (filteredCourses.length > 0) {
            setSelectedCourse(filteredCourses[0].actual_name);
            }
            setLoading(false);
        })
        .catch((err) => console.error("Gagal memuat list mata kuliah:", err));
    }, []);

    // 2. Fetch list job yang tersedia ketika mata kuliah diganti oleh user
    useEffect(() => {
        if (!selectedCourse) return;
        fetch(`http://127.0.0.1:8000/api/recommendations/${encodeURIComponent(selectedCourse)}`)
        .then((res) => res.json())
        .then((data) => {
            if (data.top_jobs && data.top_jobs.length > 0) {
            setJobs(data.top_jobs);
            setSelectedRank(data.top_jobs[0].rank);
            } else {
            setJobs([]);
            setJobDetail(null);
            }
        })
        .catch((err) => console.error("Gagal memuat rekomendasi job:", err));
    }, [selectedCourse]);

    // 3. Fetch detail XAI ketika user mengganti target job alternatif pilihan
    useEffect(() => {
        if (!selectedCourse || !selectedRank || jobs.length === 0) return;
        fetch(`http://127.0.0.1:8000/api/explainability/${encodeURIComponent(selectedCourse)}/${selectedRank}`)
        .then((res) => res.json())
        .then((data) => setJobDetail(data))
        .catch((err) => console.error("Gagal memuat detail explainability:", err));
    }, [selectedCourse, selectedRank, jobs]);

    // Kalkulasi normalisasi persentase bobot lokal EBM (SINKRONISASI 2 PARAMETER REGRESI)
    const { sp, kp } = (() => {
        if (!jobDetail) return { sp: 0, kp: 0 };
        const total_b = Math.abs(jobDetail.ebm_sim_bobot ?? 0) + Math.abs(jobDetail.ebm_kw_bobot ?? 0) || 1;
        return {
        sp: Math.round(Math.abs(jobDetail.ebm_sim_bobot ?? 0) / total_b * 100),
        kp: Math.round(Math.abs(jobDetail.ebm_kw_bobot ?? 0) / total_b * 100)
        };
    })();

    if (loading) {
        return <div className="flex h-screen items-center justify-center font-medium bg-[#F5F7FA]">Memuat XAI Analytics Engine...</div>;
    }

    return (
        <div className="flex min-h-screen bg-[#F5F7FA]">

        {/* ── WORKSPACE AREA ── */}
        <div className="flex-1 min-h-screen flex flex-col">
            <main className="p-8 w-full max-w-[1400px] mx-auto flex-1">
            
            {/* HEADER PAGE */}
            <div className="mb-6">
                <h1 className="text-2xl font-bold tracking-tight text-slate-900">Explainability XAI per Job</h1>
                <p className="text-xs font-medium text-slate-400 mt-0.5">Analisis EBM Local Explanation dan Match Validasi Kurikulum Berbasis AI</p>
            </div>

            {/* DUAL DROPDOWN ROW SELECTION */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div>
                <label className="block text-xs font-bold text-slate-800 uppercase tracking-wider mb-2">Mata Kuliah</label>
                <select 
                    value={selectedCourse} 
                    onChange={(e) => setSelectedCourse(e.target.value)}
                    className="w-full h-11 px- bg-white border border-slate-200 rounded-xl text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-emerald-500 shadow-sm text-slate-700 cursor-pointer capitalize"
                >
                    {courses.map((c, i) => (
                    <option key={i} value={c.actual_name}>
                        {c.display_name.toLowerCase()}
                    </option>
                    ))}
                </select>
                </div>
                <div>
                <label className="block text-xs font-bold text-slate-800 uppercase tracking-wider mb-2">Target Job Alternatif</label>
                <select 
                    value={selectedRank} 
                    onChange={(e) => setSelectedRank(Number(e.target.value))}
                    className="w-full h-11 px-4 bg-white border border-slate-200 rounded-xl text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-emerald-500 shadow-sm text-slate-700 cursor-pointer"
                    disabled={jobs.length === 0}>
                    {jobs.map((j, i) => (
                    <option key={i} value={j.rank}>Rank {j.rank} Job {j.title.slice(0, 40)}</option>
                    ))}
                </select>
                </div>
            </div>

            {/* MAIN CARD DETAIL BLOCK DISPLAY */}
            {jobDetail ? (
                <div className="space-y-6">
                {/* Premium Header Jumbotron Job Info */}
                <div className="p-6 bg-slate-900 rounded-2xl text-white shadow-md flex justify-between items-center">
                    <div>
                    <span className="text-[10px] uppercase font-bold tracking-widest text-emerald-100d-400">TARGET JOB ANALYSIS</span>
                    <h3 className="text-xl font-bold text-white mt-1">{jobDetail.title}</h3>
                    <p className="text-xs text-slate-400 mt-1">{jobDetail.company} &nbsp;·&nbsp; {jobDetail.location}</p>
                    </div>
                </div>

                {/* 3 Columns Breakdown Analytics Layout */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    
                    {/* Panel 1: Local Weight Bars (SINKRON HANYA 2 VARIABEL) */}
                    <div className="p-6 bg-white border border-slate-100 rounded-2xl shadow-sm space-y-4 flex flex-col justify-between">
                    <div>
                        <h4 className="text-sm font-bold text-slate-800"> EBM Local Explanation</h4>
                        <p className="text-[11px] text-slate-400 mt-0.5">Dekomposisi kontribusi fitur terhadap skor ranking</p>
                        
                        <div className="space-y-4 pt-5">
                        <div>
                            <div className="flex justify-between text-xs font-semibold text-slate-600 mb-1">
                            <span>Kemiripan Kualifikasi Skill</span>
                            <b>{sp}%</b>
                            </div>
                            <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                            <div className="h-full bg-[#378ADD] transition-all duration-500" style={{ width: `${sp}%` }}></div>
                            </div>
                        </div>
                        <div>
                            <div className="flex justify-between text-xs font-semibold text-slate-600 mb-1">
                            <span>Relevansi Kata Kunci IT</span>
                            <b>{kp}%</b>
                            </div>
                            <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                            <div className="h-full bg-[#1D9E75] transition-all duration-500" style={{ width: `${kp}%` }}></div>
                            </div>
                        </div>
                        </div>
                    </div>
                    <div className="bg-slate-50 p-3 rounded-xl text-center text-xs font-medium text-slate-600 border border-slate-100 mt-4">
                        Faktor Dominan: <b className="text-slate-900 capitalize">{jobDetail.faktor_dominan ? jobDetail.faktor_dominan.replace(/_/g, ' ') : '—'}</b>
                    </div>
                    </div>

                            {/* Panel 2: Global Feature Importance (FIXED dari hasil training EBM) */}
            <div className="p-6 bg-white border border-slate-100 rounded-2xl shadow-sm space-y-4">
                <div>
                    <h4 className="text-sm font-bold text-slate-800">Global Feature Importance</h4>
                    <p className="text-[11px] text-slate-400 mt-0.5">Proporsi kontribusi global fitur model dari hasil training EBM</p>
                </div>
                
                <div className="space-y-4 pt-2">
                    <div>
                    <div className="flex justify-between text-xs font-semibold text-slate-500 mb-1">
                        <span>Bobot Relatif Skill</span>
                        <b className="text-slate-700">92.5%</b>
                    </div>
                    <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
                        <div className="h-full bg-slate-400 transition-all duration-500" style={{ width: `92.5%` }}></div>
                    </div>
                    </div>

                    <div>
                    <div className="flex justify-between text-xs font-semibold text-slate-500 mb-1">
                        <span>Bobot Relatif Keywords</span>
                        <b className="text-slate-700">7.5%</b>
                    </div>
                    <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
                        <div className="h-full bg-slate-400 transition-all duration-500" style={{ width: `7.5%` }}></div>
                    </div>
                    </div>
                </div>
                <div className="bg-slate-50 p-3 rounded-xl text-center text-xs font-medium text-slate-600 border border-slate-100 mt-4">
                    Nilai tetap dari hasil training EBM 
                </div>
            </div>

                    {/* Panel 3: Content Match Text Intersection Badges */}
                    <div className="p-6 bg-white border border-slate-100 rounded-2xl shadow-sm space-y-4">
                    <div>
                        <h4 className="text-sm font-bold text-slate-800"> Content Matching Analysis</h4>
                        <p className="text-[11px] text-slate-400 mt-0.5">Kesesuaian skill CLO kurikulum dengan kebutuhan job description</p>
                    </div>
                    
                    <div className="space-y-4 pt-1">
                        <div>
                        <div className="flex justify-between text-xs font-semibold text-slate-600 mb-1">
                            <span>Mata Kuliah Coverage Score</span>
                            <span className="text-[#1D9E75] font-bold">
                            {jobDetail.coverage_score != null ? Number(jobDetail.coverage_score).toFixed(1) : "0"}%
                            </span>
                        </div>
                        <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                            <div className="h-full bg-[#1D9E75]" style={{ width: `${Math.min(jobDetail.coverage_score ?? 0, 100)}%` }}></div>
                        </div>
                        </div>

                        {jobDetail.skill_match && jobDetail.skill_match.length > 0 && (
                        <div className="text-[11px] pt-1">
                            <p className="font-bold text-slate-400 mb-1">MATCH INTEGRATION (TOP 5):</p>
                            <div className="flex flex-wrap gap-1">
                            {jobDetail.skill_match.slice(0, 5).map((s: string, i: number) => (
                                <span key={i} className="px-2 py-0.5 bg-blue-50 text-blue-600 border border-blue-100 rounded font-medium text-[10px] capitalize">{s}</span>
                            ))}
                            </div>
                        </div>
                        )}

                        {jobDetail.skill_gap && jobDetail.skill_gap.length > 0 && (
                        <div className="text-[11px]">
                            <p className="font-bold text-slate-400 mb-1">OUTSTANDING SKILL GAP (TOP 5):</p>
                            <div className="flex flex-wrap gap-1">
                            {jobDetail.skill_gap.slice(0, 5).map((s: string, i: number) => (
                                <span key={i} className="px-2 py-0.5 bg-red-50 text-red-500 border border-red-100 rounded font-medium text-[10px] capitalize">{s}</span>
                            ))}
                            </div>
                        </div>
                        )}
                    </div>
                    </div>

                </div>
                </div>
            ) : (
                <div className="p-8 bg-white border border-slate-100 rounded-2xl text-center text-slate-400 text-sm shadow-sm">
                Tidak ada data atribusi atau relasi regresi untuk pekerjaan ini.
                </div>
            )}
            </main>
        </div>

        </div>
    );
    }