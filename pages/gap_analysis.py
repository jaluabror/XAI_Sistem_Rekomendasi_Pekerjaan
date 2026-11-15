import streamlit as st
import json, os
from collections import Counter
import plotly.graph_objects as go
import pandas as pd
from src.mk_config import *

st.set_page_config(page_title="Gap Analysis", page_icon="", layout="wide")

st.markdown("""
<style>
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0F2942 0%,#1A3D5C 100%)}
[data-testid="stSidebar"] *{color:#E8F4FD!important}
h1{color:#0F2942!important}h2,h3{color:#1A3D5C!important}
.pill-g{background:#FDECEA;color:#B31412;padding:3px 10px;border-radius:20px;font-size:12px;margin:2px;display:inline-block}
.pill-c{background:#E8F0FE;color:#1A55D4;padding:3px 10px;border-radius:20px;font-size:12px;margin:2px;display:inline-block}
#MainMenu{visibility:hidden}footer{visibility:hidden}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    for p in ["outputs/semua_hasil_rekomendasi.json","../outputs/semua_hasil_rekomendasi.json"]:
        if os.path.exists(p):
            with open(p,"r",encoding="utf-8") as f: return json.load(f)
    return {}

NON_IT = {
    'Bahasa Indonesia','Bahasa Inggris II','Pancasila','Etika Profesi',
    'Internalisasi Budaya dan Pembentukan Karakter','Kewirausahaan',
    'Kepemimpinan dan Komunikasi Interpersonal',
    'Kerja Praktek dan Pengabdian Masyarakat','PELATIHAN DAN SERTIFIKASI',
    'Statistika Industri','Matematika Diskrit','Matematika Untuk Sistem Informasi',
    'PROBABILITAS DAN STATISTIK','Capstone Design & Project',
    'METODE PENELITIAN DAN PENYUSUNAN KARYA ILMIAH '
}

data = load_data()

rows, all_gaps, all_covs = [], [], []
for mk, hasil in data.items():
    if not hasil or "top_jobs" not in hasil: continue
    sc  = [j.get("coverage_score",0) for j in hasil["top_jobs"]]
    avg = round(sum(sc)/len(sc),1) if sc else 0
    ag, ac = [], []
    for j in hasil["top_jobs"]:
        ag.extend(j.get("skill_gap",[])); ac.extend(j.get("skill_tercover",[]))
    if mk not in NON_IT:
        all_gaps.extend(ag); all_covs.extend(ac)
    rows.append({
        "mk": mk, "avg": avg, "is_non_it": mk in NON_IT,
        "gap":  [s for s,f in Counter(ag).most_common(3)],
        "cov":  [s for s,f in Counter(ac).most_common(3)],
        "grade":"Tinggi" if avg>=60 else("Sedang" if avg>=30 else("Rendah" if avg>0 else "0%")),
    })
rows.sort(key=lambda x:(x["is_non_it"],-x["avg"]))

st.title(" Gap Analysis Kurikulum vs Industri")
st.caption("Identifikasi kesenjangan skill CLO vs kebutuhan industri")
st.divider()

# ── Summary metrics ───────────────────────────────────────────────────────────
it_nz = [r for r in rows if not r["is_non_it"] and r["avg"]>0]
it_z  = [r for r in rows if not r["is_non_it"] and r["avg"]==0]
non   = [r for r in rows if r["is_non_it"]]

m1,m2,m3,m4 = st.columns(4)
m1.metric("Total MK",len(rows))
m2.metric("MK IT Coverage > 0%",len(it_nz))
m3.metric("MK IT Coverage = 0%",len(it_z))
m4.metric("MK Non-IT",len(non))
st.divider()

tab1, tab2, tab3 = st.tabs([" Global Gap"," Per Mata Kuliah"," Heatmap"])

# ── Tab 1 ─────────────────────────────────────────────────────────────────────
with tab1:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("###  Top Skill Gap Global")
        gap15 = Counter(all_gaps).most_common(15)
        reds  = [f"rgb({max(150,200-i*5)},{max(50,80-i*5)},{max(50,80-i*5)})" for i in range(len(gap15))]
        fig = go.Figure(go.Bar(
            x=[f[1] for f in gap15], y=[f[0] for f in gap15],
            orientation="h", marker_color=reds,
            text=[f"{f[1]} MK" for f in gap15], textposition="outside",
            width=0.65,
        ))
        fig.update_layout(
            height=480, margin=dict(l=0,r=70,t=10,b=10),
            xaxis=dict(showticklabels=False,showgrid=False,zeroline=False),
            yaxis=dict(autorange="reversed",tickfont=dict(size=12)),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("###  Kekuatan Kurikulum")
        cov10 = Counter(all_covs).most_common(10)
        greens = [f"rgb({max(30,50-i*3)},{max(130,165-i*8)},{max(80,100-i*5)})" for i in range(len(cov10))]
        fig2 = go.Figure(go.Bar(
            x=[f[1] for f in cov10], y=[f[0] for f in cov10],
            orientation="h", marker_color=greens,
            text=[f"{f[1]} MK" for f in cov10], textposition="outside",
            width=0.65,
        ))
        fig2.update_layout(
            height=340, margin=dict(l=0,r=70,t=10,b=10),
            xaxis=dict(showticklabels=False,showgrid=False,zeroline=False),
            yaxis=dict(autorange="reversed",tickfont=dict(size=12)),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    left, center, right = st.columns([1,10,1])

    with center:
        st.info(
        "**Vocabulary Gap**\n\n"
        "Coverage rendah bukan berarti kurikulum tidak relevan. CLO menggunakan terminologi akademik Indonesia sementara industri menggunakan terminologi teknis Inggris. Contoh: CLO menyebut 'Pemrograman Web' sementara industri menyebut 'Web Development'. Gap ini bisa diatasi dengan mapping istilah dan penyesuaian materi ajar."
    )
# ── Tab 2 ─────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("###  IT Coverage Score per Mata Kuliah")
    fil = st.radio("Filter:", ["Semua","IT Only","Non-IT Only"], horizontal=True)
    filt = rows if fil=="Semua" else ([r for r in rows if not r["is_non_it"]] if fil=="IT Only" else [r for r in rows if r["is_non_it"]])

    mk_n  = [r["mk"][:38] for r in filt]
    avgs  = [r["avg"] for r in filt]
    clrs  = ["#27AE60" if a>=60 else("#F39C12" if a>=30 else("#E74C3C" if a>0 else "#BDC3C7")) for a in avgs]
    fig3 = go.Figure(go.Bar(
        x=avgs, y=mk_n, orientation="h",
        marker=dict(color=clrs, line=dict(color="white",width=1)),
        text=[f"{a}%" for a in avgs], textposition="outside", width=0.7,
    ))
    fig3.update_layout(
        height=max(420,len(filt)*22),
        margin=dict(l=0,r=60,t=10,b=10),
        xaxis=dict(range=[0,115],showticklabels=False,showgrid=False,zeroline=False),
        yaxis=dict(autorange="reversed",tickfont=dict(size=11)),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.divider()
    df = pd.DataFrame([{
        "Mata Kuliah": r["mk"], "Coverage (%)": r["avg"],
        "Grade": r["grade"], "Tercover": ", ".join(r["cov"]) or "-",
        "Gap Utama": ", ".join(r["gap"]) or "-",
        "Kategori": "Non-IT" if r["is_non_it"] else "IT",
    } for r in filt])
    st.dataframe(df, use_container_width=True, hide_index=True)

# ── Tab 3 Heatmap ─────────────────────────────────────────────────────────────
with tab3:
    st.markdown("###  Heatmap Skill Gap per MK")
    st.caption("Angka = berapa job dari top-10 yang butuh skill tersebut tapi tidak ada di CLO")

    top_skills = [s for s,f in Counter(all_gaps).most_common(15)]
    matrix, mk_labels = [], []

for mk, hasil in data.items():
        kat = get_kategori(mk)
        if kat == "Non-IT" or not hasil or "top_jobs" not in hasil:
            continue
        ag = []
        for j in hasil["top_jobs"]: ag.extend(j.get("skill_gap",[]))
        gc = Counter(ag)
        matrix.append([gc.get(s,0) for s in top_skills])
        mk_labels.append(normalize_mk_name(mk))

if matrix:
        max_val = max(max(row) for row in matrix) if matrix else 10

        
fig4 = go.Figure(go.Heatmap(
        z=matrix,
        x=top_skills,
        y=mk_labels,
        colorscale=[
            [0.0,  "#FFFFFF"],   # 0 = putih (tidak ada gap)
            [0.2,  "#FEF0ED"],   # rendah
            [0.5,  "#F1948A"],   # sedang
            [0.8,  "#E74C3C"],   # tinggi
            [1.0,  "#922B21"],   # sangat tinggi
        ],
        zmin=0,
        zmax=max_val,
        text=matrix,
        texttemplate="%{text}",
        textfont=dict(size=11),
        showscale=True,
        colorbar=dict(
            title=dict(text="Freq Gap", side="right"),
            tickvals=[0, max_val//4, max_val//2, max_val*3//4, max_val],
            ticktext=["0", str(max_val//4), str(max_val//2), str(max_val*3//4), str(max_val)],
            len=0.8,
        ),
        xgap=3,
        ygap=3,
    ))
fig4.update_layout(
        height=max(600, len(mk_labels) * 22),
        margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            side="top",
            tickfont=dict(size=12),
            tickangle=0,
        ),
        yaxis=dict(
            tickfont=dict(size=11),
            autorange="reversed",
        ),
    )
st.plotly_chart(fig4, use_container_width=True)