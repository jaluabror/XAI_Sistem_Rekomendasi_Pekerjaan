import streamlit as st
import json, os
import plotly.graph_objects as go
from backend.src.mk_config import *

st.set_page_config(page_title="Explainability XAI", page_icon="", layout="wide")

st.markdown("""
<style>
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0F2942 0%,#1A3D5C 100%)}
[data-testid="stSidebar"] *{color:#E8F4FD!important}
h1{color:#0F2942!important}h2,h3{color:#1A3D5C!important}
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

st.title(" Explainability XAI per Job")
st.caption("Analisis mendalam EBM Local Explanation + Skill Coverage per job")
st.divider()

c1, c2 = st.columns(2)
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
    
    hasil    = data.get(sel_mk,{})
    top_jobs = hasil.get("top_jobs",[])
with c2:
    job_opts = {f"#{j['rank']} · {j['title'][:40]}": j for j in top_jobs}
    sel_job  = st.selectbox(" Pilih Job", list(job_opts.keys()))

st.divider()
job = job_opts.get(sel_job)
if not job: st.info("Pilih job."); st.stop()

prob      = job.get("probabilitas",0)
p_color   = "#1D7A3A" if prob>=85 else("#B06000" if prob>=75 else "#B02000")
cov       = job.get("coverage_score",0)
cov_grade = job.get("coverage_grade","N/A")
cov_color = "#1D7A3A" if cov>=60 else("#B06000" if cov>=30 else "#E74C3C")

# Header job
st.markdown(f"""
<div style="background:linear-gradient(135deg,#0F2942,#1A3D5C);border-radius:14px;padding:20px;margin-bottom:20px;color:white">
    <div style="display:flex;justify-content:space-between;align-items:center">
        <div>
            <div style="font-size:12px;opacity:.7;margin-bottom:4px">RANK #{job.get('rank','')}</div>
            <h3 style="margin:0;color:white;font-size:18px">{job.get('title','')}</h3>
            <p style="margin:6px 0 0;opacity:.8;font-size:13px"> {job.get('company','')} &nbsp;·&nbsp;  {job.get('location','')}</p>
        </div>
        <div style="text-align:center;background:rgba(255,255,255,.15);border-radius:12px;padding:14px 22px">
            <div style="font-size:30px;font-weight:700;color:#6EE7B7">{prob}%</div>
            <div style="font-size:11px;opacity:.8">Probabilitas Cocok</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

col_wf, col_gi, col_xm = st.columns([2,1.5,2])

# ── EBM Local ────────────────────────────────────────────────────────────────
with col_wf:
    st.markdown("###  EBM Local Explanation")
    st.caption("Bobot kontribusi per fitur (dinormalisasi dari log-odds EBM)")

    sp, kp, lp = norm_bobot(
        job.get("ebm_sim_bobot",0),
        job.get("ebm_kw_bobot",0),
        job.get("ebm_loc_bobot",0)
    )

    # Radial / lollipop style horizontal bar
    feats  = ["Kemiripan Skill","Relevansi IT Job","Tier Lokasi"]
    vals   = [sp, kp, lp]
    clrs   = ["#1D6FA4","#27AE60","#F39C12"]
    icons  = ["","",""]

    fig_lp = go.Figure()
    for i, (f, v, c) in enumerate(zip(feats, vals, clrs)):
        fig_lp.add_shape(type="rect",
            x0=0, x1=100, y0=i-0.3, y1=i+0.3,
            fillcolor="#F0F0F0", line_width=0, layer="below")
        fig_lp.add_shape(type="rect",
            x0=0, x1=v, y0=i-0.3, y1=i+0.3,
            fillcolor=c, line_width=0, opacity=0.9)
        fig_lp.add_annotation(
            x=v/2, y=i,
            text=f"<b>{v}%</b>",
            font=dict(size=13, color="white"),
            showarrow=False)

    fig_lp.update_layout(
        height=180,
    margin=dict(l=0, r=10, t=10, b=10),
    xaxis=dict(range=[0,100], showticklabels=False,
            showgrid=False, zeroline=False),
    yaxis=dict(
        tickvals=[0,1,2],
        ticktext=[" Kemiripan Skill"," Relevansi IT Job"," Tier Lokasi"],
        tickfont=dict(size=12), autorange="reversed"),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
)
    st.plotly_chart(fig_lp, use_container_width=True)

    # Detail tabel
    st.markdown(f"""
    <div style="background:#F8FAFB;border-radius:10px;padding:12px;font-size:12px">
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;text-align:center">
            <div style="background:white;border-radius:8px;padding:8px">
                <div style="color:#666">Similarity</div>
                <div style="font-weight:700;color:#1D6FA4;font-size:16px">{job.get('similarity',0):.1f}%</div>
            </div>
            <div style="background:white;border-radius:8px;padding:8px">
                <div style="color:#666">KW Count</div>
                <div style="font-weight:700;color:#27AE60;font-size:16px">{job.get('job_kw_count',0)}/10</div>
            </div>
            <div style="background:white;border-radius:8px;padding:8px">
                <div style="color:#666">Tier Lokasi</div>
                <div style="font-weight:700;color:#F39C12;font-size:16px">{job.get('loc_tier',0)}/2</div>
            </div>
        </div>
        <div style="text-align:center;margin-top:8px;color:#555">
            Faktor dominan: <b>{job.get('faktor_dominan','-')}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Global Importance ─────────────────────────────────────────────────────────
with col_gi:
    st.markdown("###  Global Importance")
    st.caption("Rata-rata importance seluruh dataset")

    fig_gi = go.Figure()
    gi_feats = ["Kemiripan\nSkill","Relevansi\nIT Job","Tier\nLokasi"]
    gi_vals  = [79.5, 19.4, 1.1]
    gi_clrs  = ["#1D6FA4","#27AE60","#F39C12"]
    fig_gi.add_trace(go.Bar(
        x=gi_feats, y=gi_vals,
        marker=dict(color=gi_clrs, line=dict(color="white",width=2)),
        text=[f"<b>{v}%</b>" for v in gi_vals],
        textposition="outside", width=0.5,
    ))
    fig_gi.update_layout(
        height=220, margin=dict(l=0,r=10,t=30,b=10),
        yaxis=dict(range=[0,100],showticklabels=False,showgrid=False,zeroline=False),
        xaxis=dict(tickfont=dict(size=11)),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )
    st.plotly_chart(fig_gi, use_container_width=True)

    st.markdown("""
    <div style="background:#F0F7FF;border-radius:10px;padding:12px;font-size:12px">
        <div style="font-weight:600;margin-bottom:6px;color:#0F2942"> Metrik Model</div>
        <div>AUC-ROC: <b>0.9404</b></div>
        <div>CV AUC: <b>0.9465 ± 0.0019</b></div>
        <div>Accuracy: <b>88.58%</b></div>
        <div>F1 (Cocok): <b>0.80</b></div>
        <div>Training: <b>60,000 pasangan</b></div>
    </div>
    """, unsafe_allow_html=True)

# ── Explainability Matching ───────────────────────────────────────────────────
with col_xm:
    st.markdown("###  Explainability Matching")
    st.caption("Analisis konten CLO vs Job Description")

    # Gauge modern pakai bullet chart
    fig_gauge = go.Figure()
    fig_gauge.add_shape(type="rect", x0=0,x1=100,y0=0,y1=1,
                        fillcolor="#FFF0F0",line_width=0,layer="below")
    fig_gauge.add_shape(type="rect", x0=0,x1=60,y0=0,y1=1,
                        fillcolor="#FFFBE6",line_width=0,layer="below")
    fig_gauge.add_shape(type="rect", x0=0,x1=30,y0=0,y1=1,
                        fillcolor="#E8F8F0",line_width=0,layer="below")
    fig_gauge.add_shape(type="rect", x0=0,x1=max(cov,1),y0=0.1,y1=0.9,
                        fillcolor=cov_color, line_width=0)
    fig_gauge.add_annotation(x=50,y=0.5, text=f"<b>{cov:.1f}%</b> — {cov_grade}",
                            font=dict(size=16,color="white" if cov>20 else "#333"),
                            showarrow=False)
    # Milestone markers
    for xv,lbl in [(30,"Rendah"),(60,"Sedang"),(100,"Tinggi")]:
        fig_gauge.add_shape(type="line",x0=xv,x1=xv,y0=0,y1=1,
                            line=dict(color="white",width=1,dash="dot"))
    fig_gauge.update_layout(
        height=100, margin=dict(l=0,r=0,t=5,b=5),
        xaxis=dict(range=[0,100],showticklabels=False,showgrid=False,zeroline=False),
        yaxis=dict(showticklabels=False,showgrid=False,zeroline=False,range=[0,1]),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    st.markdown("IT Coverage Score")
    st.plotly_chart(fig_gauge, use_container_width=True)

    matched = job.get("skill_match",[])
    covered = job.get("skill_tercover",[])
    gap     = job.get("skill_gap",[])
    match_pct = job.get("match_pct",0)

    if matched:
        st.markdown(f"**Kata Match CLO ∩ Job** *(overlap {match_pct:.1f}%)*")
        pills = " ".join([f'<span class="pill-m">{s}</span>' for s in matched])
        st.markdown(pills, unsafe_allow_html=True)

    if covered:
        st.markdown("**Skill IT Tercover **")
        pills = " ".join([f'<span class="pill-c">{s}</span>' for s in covered])
        st.markdown(pills, unsafe_allow_html=True)

    if gap:
        st.markdown("Skill Gap")
        pills = " ".join([f'<span class="pill-g">{s}</span>' for s in gap])
        st.markdown(pills, unsafe_allow_html=True)

    if not matched and not covered and not gap:
        st.caption("Tidak ada data skill match untuk job ini.")

# ── All jobs summary ──────────────────────────────────────────────────────────
st.divider()
mk_display = MK_TITLE_CASE.get(sel_mk, sel_mk.title())
st.markdown(f"###  Semua Job {mk_display}")

cols = st.columns(len(top_jobs))
for i, j in enumerate(top_jobs):
    pb = j.get("probabilitas",0)
    cv = j.get("coverage_score",0)
    pc = "#1D7A3A" if pb>=85 else("#B06000" if pb>=75 else "#E74C3C")
    is_sel = j.get('rank') == job.get('rank')
    border = f"2px solid {pc}" if is_sel else "1px solid #E2EDF7"
    with cols[i]:
        st.markdown(f"""
        <div style="background:white;border:{border};border-radius:12px;padding:12px;text-align:center;box-shadow:0 2px 6px rgba(0,0,0,.06)">
            <div style="font-size:11px;color:#999;font-weight:600">RANK #{j.get('rank','')}</div>
            <div style="font-size:11px;font-weight:600;color:#0F2942;margin:4px 0;line-height:1.3">{j.get('title','')[:28]}...</div>
            <div style="font-size:22px;font-weight:700;color:{pc}">{pb}%</div>
            <div style="font-size:11px;color:#999">Prob</div>
            <div style="background:#F5F5F5;border-radius:6px;height:6px;margin-top:6px;overflow:hidden">
                <div style="width:{int(cv)}%;height:100%;background:{'#27AE60' if cv>=60 else('#F39C12' if cv>=30 else '#E74C3C')}"></div>
            </div>
            <div style="font-size:10px;color:#999;margin-top:2px">Cov {cv:.0f}%</div>
        </div>""", unsafe_allow_html=True)