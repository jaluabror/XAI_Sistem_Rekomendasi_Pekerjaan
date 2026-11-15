import streamlit as st
import json, os, sys
import plotly.graph_objects as go
from src.mk_config import *

st.set_page_config(page_title="Rekomendasi Karir", page_icon="", layout="wide")

st.markdown("""
<style>
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0F2942 0%,#1A3D5C 100%)}
[data-testid="stSidebar"] *{color:#E8F4FD!important}
h1{color:#0F2942!important}h2,h3{color:#1A3D5C!important}
.job-card{background:white;border:1px solid #E2EDF7;border-radius:14px;padding:18px;margin-bottom:14px;box-shadow:0 2px 8px rgba(15,41,66,.07)}
.pill-m{background:#E6F4EA;color:#1D6B37;padding:3px 10px;border-radius:20px;font-size:12px;margin:2px;display:inline-block}
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

data = load_data()

def norm_bobot(sim_b, kw_b, loc_b):
    t = abs(sim_b)+abs(kw_b)+abs(loc_b)
    if t == 0: return 79.5, 19.4, 1.1
    return round(abs(sim_b)/t*100,1), round(abs(kw_b)/t*100,1), round(abs(loc_b)/t*100,1)

st.title(" Rekomendasi Karir per Mata Kuliah")
st.caption("Top-N rekomendasi job berbasis EBM + Explainability Matching")
st.divider()

c1, c2 = st.columns([3,1])
with c1:
    mk_mapping = {
        normalize_mk_name(mk): mk
        for mk in data.keys()
    }

    mk_list = sorted(mk_mapping.keys())

    sel_mk_display = st.selectbox(
        "Pilih Mata Kuliah",
        mk_list
    )

    sel_mk = mk_mapping[sel_mk_display]
with c2:
    top_n = st.selectbox("Top-N", [3,5,10], index=1)

st.divider()
hasil    = data.get(sel_mk, {})
top_jobs = hasil.get("top_jobs",[])[:top_n]
pattern  = hasil.get("pattern",{})

if not top_jobs:
    st.info("Pilih mata kuliah untuk melihat rekomendasi."); st.stop()

scores   = [j.get("coverage_score",0) for j in top_jobs]
avg_cov  = round(sum(scores)/len(scores),1) if scores else 0
avg_prob = round(sum(j.get("probabilitas",0) for j in top_jobs)/len(top_jobs),1)
top_role = max(pattern.get("role_distribution",{"N/A":0}),
            key=pattern.get("role_distribution",{"N/A":0}).get, default="N/A")

mk_display = MK_TITLE_CASE.get(sel_mk, sel_mk.title())
st.subheader(f"  {mk_display}")

m1,m2,m3,m4 = st.columns(4)
m1.metric("Job Direkomendasikan", len(top_jobs))
m2.metric("Avg Probabilitas", f"{avg_prob}%")
m3.metric("Avg IT Coverage", f"{avg_cov}%")
m4.metric("Role Dominan", top_role.replace("_"," ").title())
st.divider()

st.subheader(" Top Job Rekomendasi")
for job in top_jobs:
    prob      = job.get("probabilitas",0)
    p_color   = "#1D7A3A" if prob>=85 else ("#B06000" if prob>=75 else "#B02000")
    cov       = job.get("coverage_score",0)
    cov_grade = job.get("coverage_grade","N/A")
    cov_color = "#1D7A3A" if cov>=60 else ("#B06000" if cov>=30 else "#888")
    sim_b     = job.get("ebm_sim_bobot",0)
    kw_b      = job.get("ebm_kw_bobot",0)
    loc_b     = job.get("ebm_loc_bobot",0)
    sp,kp,lp  = norm_bobot(sim_b, kw_b, loc_b)

    with st.container():
        st.markdown(f"""<div class="job-card">
            <div style="display:flex;justify-content:space-between;align-items:flex-start">
                <div>
                    <span style="font-size:12px;color:#999;font-weight:600">RANK #{job.get('rank','')}</span>
                    <h4 style="margin:4px 0;color:#0F2942;font-size:16px">{job.get('title','')}</h4>
                    <span style="color:#666;font-size:13px"> {job.get('company','')} &nbsp;·&nbsp;  {job.get('location','')}</span>
                </div>
                <div style="text-align:center;background:#F8FAFB;border-radius:12px;padding:10px 18px">
                    <div style="font-size:26px;font-weight:700;color:{p_color}">{prob}%</div>
                    <div style="font-size:11px;color:#999">Probabilitas</div>
                </div>
            </div></div>""", unsafe_allow_html=True)

        col_ebm, col_xm = st.columns(2)

        with col_ebm:
            st.markdown("Bobot Fitur EBM")
            # Donut chart per fitur
            fig = go.Figure()
            features = ["Kemiripan Skill","Relevansi IT","Tier Lokasi"]
            values   = [sp, kp, lp]
            colors   = ["#1D6FA4","#27AE60","#F39C12"]
            fig.add_trace(go.Bar(
                x=values, y=features, orientation="h",
                marker=dict(
                    color=["#1D6FA4", "#27AE60", "#F39C12"],
                    line=dict(color="white", width=2)
                    ),
                    text=[f"<b>{v}%</b>" for v in values],
                    textposition="inside",
                    insidetextanchor="middle",
                width=0.55,
            ))
            fig.update_layout(
                height=160, margin=dict(l=0,r=10,t=5,b=5),
                xaxis=dict(range=[0,105],showticklabels=False,showgrid=False,zeroline=False),
                yaxis=dict(autorange="reversed",tickfont=dict(size=12)),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True, key=f"ebm_{job.get('rank')}")

            # Info fitur
            info_cols = st.columns(3)
            info_cols[0].markdown(f"<div style='text-align:center;padding:6px;background:#EBF5FF;border-radius:8px'><div style='font-size:11px;color:#666'>Similarity</div><div style='font-weight:700;color:#1D6FA4'>{job.get('similarity',0):.1f}%</div></div>", unsafe_allow_html=True)
            info_cols[1].markdown(f"<div style='text-align:center;padding:6px;background:#EDFBF0;border-radius:8px'><div style='font-size:11px;color:#666'>KW Count</div><div style='font-weight:700;color:#27AE60'>{job.get('job_kw_count',0)}/10</div></div>", unsafe_allow_html=True)
            info_cols[2].markdown(f"<div style='text-align:center;padding:6px;background:#FEF9ED;border-radius:8px'><div style='font-size:11px;color:#666'>Tier</div><div style='font-weight:700;color:#F39C12'>{job.get('loc_tier',0)}/2</div></div>", unsafe_allow_html=True)

        with col_xm:
            st.markdown(" Explainability Matching")
            matched = job.get("skill_match",[])
            covered = job.get("skill_tercover",[])
            gap     = job.get("skill_gap",[])

            # Coverage progress bar custom
            cov_w = int(cov)
            st.markdown(f"""
            <div style="margin:8px 0">
                <div style="display:flex;justify-content:space-between;margin-bottom:4px">
                    <span style="font-size:12px;color:#666">IT Coverage Score</span>
                    <span style="font-size:13px;font-weight:700;color:{cov_color}">{cov:.1f}% ({cov_grade})</span>
                </div>
                <div style="background:#F0F0F0;border-radius:8px;height:10px;overflow:hidden">
                    <div style="width:{cov_w}%;height:100%;background:{cov_color};border-radius:8px;transition:width .5s"></div>
                </div>
            </div>""", unsafe_allow_html=True)

            if matched:
                st.markdown("<div style='font-size:12px;color:#666;margin-top:8px'>Kata Match CLO ∩ Job:</div>", unsafe_allow_html=True)
                pills = " ".join([f'<span class="pill-m">{s}</span>' for s in matched[:6]])
                st.markdown(pills, unsafe_allow_html=True)

            if covered:
                st.markdown("<div style='font-size:12px;color:#666;margin-top:6px'>Skill Tercover:</div>", unsafe_allow_html=True)
                pills = " ".join([f'<span class="pill-c">{s}</span>' for s in covered])
                st.markdown(pills, unsafe_allow_html=True)

            if gap:
                st.markdown("<div style='font-size:12px;color:#666;margin-top:6px'>Skill Gap:</div>", unsafe_allow_html=True)
                pills = " ".join([f'<span class="pill-g">{s}</span>' for s in gap[:5]])
                st.markdown(pills, unsafe_allow_html=True)

        st.divider()

# Pattern Analysis
st.subheader(" Analisis Pattern Mata Kuliah")
c_role, c_gap = st.columns(2)

with c_role:
    role_dist = pattern.get("role_distribution",{})
    if role_dist:
        labels = [k.replace("_"," ").title() for k in role_dist]
        vals   = list(role_dist.values())
        colors_pie = ["#1D6FA4","#27AE60","#F39C12","#E74C3C","#8E44AD","#16A085","#2C3E50"]
        fig_p = go.Figure(go.Pie (
            labels=labels, values=vals, hole=0.55,
            marker=dict(colors=colors_pie[:len(labels)], line=dict(color="white",width=2)),
            textinfo="label+percent", textfont_size=12, 
        ))


        fig_p.add_annotation(text=f"<b>{len(vals)}</b><br>Role", x=0.5, y=0.5,
                            font_size=14, showarrow=False)
        fig_p.update_layout(height=280, margin=dict(l=0,r=0,t=20,b=0),
                            paper_bgcolor="rgba(0,0,0,0)", showlegend=True,
                            legend=dict(orientation="v", font_size=11))
        st.markdown("Distribusi Role Job")
        st.plotly_chart(fig_p, use_container_width=True)

with c_gap:
    gap_top5  = pattern.get("skill_gap_top5",[])
    match_top = pattern.get("skill_match_top5",[])
    if gap_top5:
        skills = [g["skill"] for g in gap_top5]
        freqs  = [g["freq"]  for g in gap_top5]
        # Gradient merah
        n = len(skills)
        reds = [f"rgba(231,{max(57,57+i*15)},{max(57,57+i*15)},1)" for i in range(n)]
        fig_g = go.Figure(go.Bar(
            x=freqs, y=skills, orientation="h",
            marker=dict(color=["#E74C3C","#EC6B56","#F08080","#F4A8A8","#F8D0D0"][:n],
                        line=dict(color="white",width=1)),
            text=[f"{f}/{top_n}" for f in freqs],
            textposition="outside", width=0.6,
        ))
        fig_g.update_layout(
            height=280, margin=dict(l=0,r=50,t=20,b=10),
            xaxis=dict(range=[0,top_n+1],showticklabels=False,showgrid=False,zeroline=False),
            yaxis=dict(autorange="reversed",tickfont=dict(size=12)),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        st.markdown("Skill Gap Terbanyak")
        st.plotly_chart(fig_g, use_container_width=True)

    if match_top:
        st.markdown(" Kekuatan Kurikulum")
        pills = " ".join([f'<span class="pill-m"><b>{g["skill"]}</b> {g["freq"]}/{top_n}</span>' for g in match_top])
        st.markdown(pills, unsafe_allow_html=True)