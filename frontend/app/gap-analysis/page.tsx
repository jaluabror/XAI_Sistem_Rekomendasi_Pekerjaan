'use client';

import { useState, useEffect, useMemo } from 'react';
import { BookOpenText, LayoutDashboard, Cpu, ChartBarDecreasing } from 'lucide-react';
import Link from 'next/link';

export default function GapAnalysisPage() {
    const [data, setData] = useState<any>(null);
    const [heatmapData, setHeatmapData] = useState<any>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [activeTab, setActiveTab] = useState<string>('macro'); // 'macro', 'course', 'heatmap'
    const [tableFilter, setTableFilter] = useState<string>('Semua');

    // ── 1. KALKULASI STATISTIK MAKRO DINAMIS (SINKRON 48 MATA KULIAH) ──
    const mkStats = useMemo(() => {
        if (!data || !data.table_rows) return { coverageNonZero: 0, coverageZero: 0, nonIT: 0 };
        
        let coverageNonZero = 0, coverageZero = 0, nonIT = 0;

        // Membaca status kategori langsung dari properti flags backend agar presisi 100%
        data.table_rows.forEach((row: any) => {
            if (row.is_non_it || row.kategori === 'Non-IT') { 
                nonIT++; 
            } else {
                if (row.avg > 0) coverageNonZero++;
                else coverageZero++;
            }
        });

        return { coverageNonZero, coverageZero, nonIT };
    }, [data]);

    useEffect(() => {
        // Ambil data summary makro & tabel
        fetch('http://127.0.0.1:8000/api/gap-analysis/summary')
        .then((res) => res.json())
        .then((resData) => {
            setData(resData);
            // Ambil data heatmap matrix
            return fetch('http://127.0.0.1:8000/api/gap-analysis/heatmap');
        })
        .then((res) => res.json())
        .then((heatData) => {
            setHeatmapData(heatData);
            setLoading(false);
        })
        .catch((err) => console.error("Gagal memuat engine analisis gap:", err));
    }, []);

    if (loading || !data || !heatmapData) {
        return <div className="flex h-screen items-center justify-center font-medium bg-[#F5F7FA]">Memuat Gap Analysis Engine...</div>;
    }

    const filteredRows = data.table_rows.filter((r: any) => {
        if (tableFilter === 'IT Spesifik') return r.kategori === 'IT Spesifik';
        if (tableFilter === 'IT Umum') return r.kategori === 'IT Umum';
        if (tableFilter === 'Non-IT') return r.kategori === 'Non-IT';
        return true;
    });

    return (
        <div className="flex min-h-screen bg-[#F5F7FA]">
        
        {/* ── WORKSPACE AREA ── */}
        <div className="flex-1 min-h-screen flex flex-col">
            <main className="p-8 w-full max-w-[1400px] mx-auto flex-1">
            
                <div className="mb-6">
                    <h1 className="text-2xl font-bold tracking-tight text-slate-900">Gap Analysis Kurikulum vs Industri</h1>
                    <p className="text-xs font-medium text-slate-400 mt-0.5">Identifikasi kesenjangan skill CLO (Capaian Pembelajaran) vs kebutuhan industri nyata</p>
                </div>

                {/* STATS CARDS GRID */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                    {/* CARD 1: TOTAL MATA KULIAH */}
                    <div className="p-5 bg-white border border-slate-100 rounded-2xl shadow-sm space-y-1">
                        <span className="text-[11px] font-semibold text-slate-400 tittlecase tracking-wider block">Total Mata Kuliah</span>
                        <h3 className="text-2xl font-black text-slate-900">{data?.table_rows ? data.table_rows.length : 48}</h3>
                    </div>

                    {/* CARD 2: MK IT COVERAGE > 0% */}
                    <div className="p-5 bg-white border border-slate-100 rounded-2xl shadow-sm space-y-1">
                        <span className="text-[11px] font-semibold text-slate-400 tittlecase tracking-wider block">MK IT Coverage &gt; 0%</span>
                        <h3 className="text-2xl font-black text-emerald-600">{mkStats.coverageNonZero}</h3>
                    </div>

                    {/* CARD 3: MK IT COVERAGE = 0% */}
                    <div className="p-5 bg-white border border-slate-100 rounded-2xl shadow-sm space-y-1">
                        <span className="text-[11px] font-semibold text-slate-400 tittlecase tracking-wider block">MK IT Coverage = 0%</span>
                        <h3 className="text-2xl font-black text-amber-500">{mkStats.coverageZero}</h3>
                    </div>

                    {/* CARD 4: MK NON-IT */}
                    <div className="p-5 bg-white border border-slate-100 rounded-2xl shadow-sm space-y-1">
                        <span className="text-[11px] font-semibold text-slate-400 tittlecase tracking-wider block">MK Non-IT</span>
                        <h3 className="text-2xl font-black text-slate-700">{mkStats.nonIT}</h3>
                    </div>
                </div>

                {/* INTERACTIVE NAVIGATION TABS */}
                <div className="flex border-b border-slate-200 mb-6 gap-6 text-sm">
                    <button onClick={() => setActiveTab('macro')} className={`pb-3 font-semibold transition-all ${activeTab === 'macro' ? 'text-[#1D9E75] border-b-2 border-[#1D9E75]' : 'text-slate-400 hover:text-slate-600'}`}> Distribusi Makro</button>
                    <button onClick={() => setActiveTab('course')} className={`pb-3 font-semibold transition-all ${activeTab === 'course' ? 'text-[#1D9E75] border-b-2 border-[#1D9E75]' : 'text-slate-400 hover:text-slate-600'}`}> Per Mata Kuliah</button>
                    <button onClick={() => setActiveTab('heatmap')} className={`pb-3 font-semibold transition-all ${activeTab === 'heatmap' ? 'text-[#1D9E75] border-b-2 border-[#1D9E75]' : 'text-slate-400 hover:text-slate-600'}`}> Heatmap Spectrum</button>
                </div>

                {/* ── TAB 1: DISTRIBUSI MAKRO ── */}
                {activeTab === 'macro' && (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <div className="p-6 bg-white border border-slate-100 rounded-2xl shadow-sm">
                            <h4 className="text-sm font-bold text-slate-800 mb-4 flex items-center gap-2"><span className="w-1.5 h-3 bg-red-500 rounded-sm"></span> Top 15 Skill Gap Global (Defisit)</h4>
                            <div className="space-y-3">
                                {data.top_gaps.map((item: any, idx: number) => {
                                    const barWidth = Math.max(15, (item.count / data.top_gaps[0].count) * 100);
                                    return (
                                        <div key={idx} className="text-xs">
                                            <div className="flex justify-between text-slate-600 mb-1"><span className="font-medium capitalize">{item.skill}</span><span className="font-semibold text-red-500">{item.count} MK</span></div>
                                            <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden"><div className="h-full bg-red-400 rounded-full" style={{ width: `${barWidth}%` }}></div></div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                        <div className="p-6 bg-white border border-slate-100 rounded-2xl shadow-sm h-fit">
                            <h4 className="text-sm font-bold text-slate-800 mb-4 flex items-center gap-2"><span className="w-1.5 h-3 bg-emerald-500 rounded-sm"></span> Top 10 Kekuatan Kurikulum</h4>
                            <div className="space-y-3">
                                {data.top_covs.map((item: any, idx: number) => {
                                    const barWidth = Math.max(15, (item.count / data.top_covs[0].count) * 100);
                                    return (
                                        <div key={idx} className="text-xs">
                                            <div className="flex justify-between text-slate-600 mb-1"><span className="font-medium capitalize">{item.skill}</span><span className="font-semibold text-emerald-600">{item.count} MK</span></div>
                                            <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden"><div className="h-full bg-emerald-400 rounded-full" style={{ width: `${barWidth}%` }}></div></div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    </div>
                )}

                {/* ── TAB 2: PER MATA KULIAH ── */}
                {activeTab === 'course' && (
                    <div className="p-6 bg-white border border-slate-100 rounded-2xl shadow-sm">
                        <div className="flex items-center gap-4 mb-6 text-xs font-semibold text-slate-500">
                            <span>Kategori:</span>
                            {['Semua', 'IT Spesifik', 'IT Umum', 'Non-IT'].map((opt) => (
                                <label key={opt} className="flex items-center gap-1.5 cursor-pointer text-slate-700">
                                    <input 
                                        type="radio" 
                                        name="filter" 
                                        value={opt} 
                                        checked={tableFilter === opt}
                                        onChange={(e) => setTableFilter(e.target.value)}
                                        className="accent-[#1D9E75]"
                                    />
                                    {opt}
                                </label>
                            ))}
                        </div>
                        <div className="overflow-x-auto">
                            <table className="w-full border-collapse text-left text-xs">
                                <thead>
                                    <tr className="border-b border-slate-100 text-slate-400 font-semibold bg-slate-50/50">
                                        <th className="py-3 px-4 w-[40%]">Mata Kuliah Kurikulum</th>
                                        <th className="py-3 px-4 w-[25%]">Rata-rata Coverage Score</th>
                                        <th className="py-3 px-4 w-[15%]">Grade</th>
                                        <th className="py-3 px-4 w-[20%]">Materi Tercover (Top 3)</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-50 text-slate-700 font-medium">
                                    {filteredRows.map((row: any, idx: number) => {
                                        const barColor = row.avg >= 60 ? 'bg-[#1D9E75]' : (row.avg >= 30 ? 'bg-amber-500' : (row.avg > 0 ? 'bg-red-400' : 'bg-slate-300'));
                                        return (
                                            <tr key={idx} className="hover:bg-slate-50/50 transition-all">
                                                <td className="py-3.5 px-4">
                                                    <div className="flex items-center gap-2.5">
                                                        <span className="text-sm shrink-0">{row.icon || "📘"}</span>
                                                        <div>
                                                            <p className="font-bold text-slate-800 text-[12.5px] tracking-tight">{row.mk}</p>
                                                            <p className="text-[10px] text-slate-400 font-normal uppercase tracking-wide mt-0.5">{row.realm} · {row.kategori}</p>
                                                        </div>
                                                    </div>
                                                </td>
                                                <td className="py-3.5 px-4">
                                                    <div className="flex items-center gap-3">
                                                        <span className="w-10 inline-block font-bold text-slate-700">{row.avg?.toFixed(2)}%</span>
                                                        <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden max-w-[130px]">
                                                            <div className={`h-full ${barColor}`} style={{ width: `${Math.min(row.avg, 100)}%` }}></div>
                                                        </div>
                                                    </div>
                                                </td>
                                                <td className="py-3.5 px-4">
                                                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${row.grade === 'Tinggi' ? 'bg-emerald-50 text-emerald-600' : (row.grade === 'Sedang' ? 'bg-amber-50 text-amber-600' : 'bg-rose-50 text-rose-500')}`}>
                                                        {row.grade}
                                                    </span>
                                                </td>
                                                <td className="py-3.5 px-4 text-slate-400 text-[11px]">
                                                    {row.cov && row.cov.length > 0 ? (
                                                        <div className="flex flex-wrap gap-1">
                                                            {row.cov.map((c: string, i: number) => (
                                                                <span key={i} className="px-1.5 py-0.5 bg-blue-50 text-blue-600 border border-blue-100 rounded text-[10px] font-medium capitalize">{c}</span>
                                                            ))}
                                                        </div>
                                                    ) : '—'}
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}

                {/* ── TAB 3: VISUALISASI HEATMAP MATRIX ── */}
                {activeTab === 'heatmap' && (
                    <div className="p-6 bg-white border border-slate-100 rounded-2xl shadow-sm space-y-4">
                        <div>
                            <h4 className="text-sm font-bold text-slate-800"> Heatmap Kesenjangan Kompetensi (Top 15 Skills)</h4>
                            <p className="text-[11px] text-slate-400 mt-0.5">Warna merah pekat mengindikasikan tingginya frekuensi kemunculan gap skill industri pada silabus mata kuliah IT</p>
                        </div>

                        <div className="overflow-auto max-h-[650px] border border-slate-100 rounded-xl mt-4">
                            <div className="w-max min-w-full">
                            
                                {/* HEADER SUMBU X (Nama-Nama Kompetensi Industri) */}
                                <div className="flex bg-slate-50 border-b border-slate-100 py-3 px-4 sticky top-0 z-20 text-center font-bold text-slate-500 text-[10px] tracking-wider uppercase items-center">
                                    <div className="w-[280px] text-left text-slate-400 font-semibold shrink-0">Mata Kuliah IT</div>
                                    <div className="flex-1 flex justify-between">
                                        {heatmapData.x_axis_skills.map((skill: string, i: number) => (
                                            <div key={i} className="w-[75px] shrink-0 truncate px-1 text-[9.5px] text-slate-600 font-bold capitalize" title={skill}>
                                                {skill}
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* RENDERING MATRIX SUMBU Y (Baris per MK) */}
                                <div className="divide-y divide-slate-100">
                                    {heatmapData.y_axis_courses.map((course: string, yIdx: number) => (
                                        <div key={yIdx} className="flex items-center hover:bg-slate-50/50 transition-all px-4 py-1.5 text-[11px] text-slate-700 font-medium">
                                            
                                            <div className="w-[280px] font-bold text-slate-800 truncate pr-4 shrink-0 text-left" title={course}>
                                                {course}
                                            </div>
                                            
                                            <div className="flex-1 flex justify-between">
                                                {heatmapData.z_matrix?.[yIdx]?.map((val: number, xIdx: number) => {
                                                    let bgHeatValue = 'bg-slate-50/40 text-slate-300'; 

                                                    if (val > 0) {
                                                        if (val >= 7) bgHeatValue = 'bg-red-600 text-white font-black shadow-sm';
                                                        else if (val >= 5) bgHeatValue = 'bg-red-400 text-white font-black';
                                                        else if (val >= 3) bgHeatValue = 'bg-red-200 text-red-800 font-bold';
                                                        else if (val >= 2) bgHeatValue = 'bg-red-100 text-red-700 font-semibold';
                                                        else bgHeatValue = 'bg-red-50 text-red-600 font-medium';
                                                    }

                                                    return (
                                                        <div 
                                                            key={xIdx} 
                                                            className={`w-[75px] shrink-0 text-center py-1.5 mx-0.5 rounded-md transition-all text-[10px] flex items-center justify-center h-7 ${bgHeatValue}`}
                                                            title={`MK: ${course} | Skill: ${heatmapData.x_axis_skills[xIdx]} | Frekuensi: ${val} kali`}
                                                        >
                                                            {val}
                                                        </div>
                                                    );
                                                })}
                                            </div>

                                        </div>
                                    ))}
                                </div>

                            </div>
                        </div>

                        {/* FOOTER INFORMASI AKADEMIK */}
                        <div className="pt-4 flex justify-end text-[10px] text-slate-400 font-medium tracking-wide">
                            <span>Standarisasi Kurikulum IS2020 ACM/AIS • Sistem Informasi</span>
                        </div>
                    </div>
                )}

            </main>
        </div>
        
        </div>
    );
}