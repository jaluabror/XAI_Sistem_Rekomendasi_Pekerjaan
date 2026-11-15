import streamlit as st
import json
import os
import plotly.graph_objects as go
from collections import Counter
from backend.src.mk_config import *

st.set_page_config(
    page_title="XAI",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS: Gaya Enterprise Minimalis (Linear/Vercel/Notion) ──────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', -apple-system, sans-serif;
        background-color: #F5F7FA !important;
        color: #1E293B;
    }

    /* Sidebar - Slate Gelap Premium */
    [data-testid="stSidebar"] {
        background: #0F172A !important;
        border-right: 1px solid #E2E8F0;
    }
    [data-testid="stSidebar"] * { color: #F8FAFC !important; }
    [data-testid="stSidebar"] .stRadio label { color: #F8FAFC !important; }

    /* Metric Cards - Bersih ala Stripe/Notion */
    [data-testid="metric-container"], [data-testid="stMetricContainer"] {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 16px !important;
        padding: 20px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.01), 0 2px 4px -1px rgba(0, 0, 0, 0.01) !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 12px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 700 !important;
        color: #0F172A !important;
    }

    /* Judul & Hierarki */
    h1 { color: #0F172A !important; font-weight: 700 !important; letter-spacing: -0.02em; }
    h2 { color: #0F172A !important; font-weight: 600 !important; }
    h3 { color: #1D9E75 !important; font-weight: 600 !important; }

    /* Job Cards Modern dengan Batas Tipis & Soft Shadow */
    .job-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.01);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .job-card:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.02);
    }
    
    .prob-high { color: #1D9E75; font-weight: 700; font-size: 18px; }
    .prob-med  { color: #BA7517; font-weight: 700; font-size: 18px; }
    .prob-low  { color: #E24B4A; font-weight: 700; font-size: 18px; }

    /* Badge & Skill Pills Kustom */
    .pill-match { background:#EFF6FF; color:#378ADD; padding:4px 10px; border-radius:6px; font-size:12px; font-weight:500; margin:2px; display:inline-block; border:1px solid #BFDBFE; }
    .pill-gap   { background:#FEF2F2; color:#E24B4A; padding:4px 10px; border-radius:6px; font-size:12px; font-weight:500; margin:2px; display:inline-block; border:1px solid #FCA5A5; }
    .pill-cover { background:#ECFDF5; color:#1D9E75; padding:4px 10px; border-radius:6px; font-size:12px; font-weight:500; margin:2px; display:inline-block; border:1px solid #A7F3D0; }

    /* Sembunyikan Menu Default */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stHeader"] {background: transparent;}
</style>
""", unsafe_allow_html=True)

# ── Load Data (Isi & Section Tetap) ───────────────────────────────────────────
@st.cache_data
def load_json_data():
    json_path = os.path.join(os.path.dirname(__file__), "outputs", "semua_hasil_rekomendasi.json")
    fallback_paths = [
        "outputs/semua_hasil_rekomendasi.json",
        "../outputs/semua_hasil_rekomendasi.json",
        "semua_hasil_rekomendasi.json",
    ]
    for path in [json_path] + fallback_paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    return {}

if "data" not in st.session_state:
    st.session_state.data = load_json_data()

data = st.session_state.data

# ── Sidebar Navigation (Isi & Section Tetap) ──────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/graduation-cap.png", width=60)
    st.markdown("## XAI")
    st.markdown("**Sistem Rekomendasi Karir**")
    st.markdown("Program Studi Sistem Informasi")
    st.divider()

    st.markdown("### Model Info")
    st.markdown("- **Model**: EBM (InterpretML)")
    st.markdown("- **AUC-ROC**: 0.9404")
    st.markdown("- **CV AUC**: 0.9465 ± 0.0019")
    st.markdown("- **Accuracy**: 88.58%")
    st.markdown("- **Jobs**: 3,352 lowongan")
    st.markdown(f"- **MK**: {len(data)} mata kuliah")
    st.divider()

    st.markdown("### 🔗 Navigasi")
    st.markdown("Gunakan menu **Pages** di atas sidebar untuk navigasi antar halaman.")
    st.divider()
    st.caption("©2026 Job RecSys OBE XAI")

# ── Home Page (Isi & Section Tetap) ───────────────────────────────────────────
st.title(" XAI for Career Recommendation ")
st.markdown("**Explainable Boosting Machine (EBM) · Program Studi Sistem Informasi**")
st.divider()

# Quick stats
all_gaps = []
it_mk_with_coverage = 0
for mk, hasil in data.items():
    if not hasil or "top_jobs" not in hasil:
        continue
    scores = [j.get("coverage_score", 0) for j in hasil["top_jobs"]]
    avg = sum(scores) / len(scores) if scores else 0
    if avg > 0:
        it_mk_with_coverage += 1
    for j in hasil["top_jobs"]:
        all_gaps.extend(j.get("skill_gap", []))

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Mata Kuliah", len(data))
col2.metric("MK dengan Coverage > 0%", it_mk_with_coverage)
col3.metric("Total Lowongan", "3,352")
col4.metric("AUC-ROC Model", "0.9404")

st.divider()

# Top skill gaps global
st.subheader(" Top Skill Gap Global")
st.caption("Skill yang paling sering dibutuhkan industri tapi belum tercover kurikulum")

gap_counter = Counter(all_gaps).most_common(10)

# Mengubah warna grafik ke warna baru (Emerald/Blue/Muted)
if gap_counter:
    fig = go.Figure(go.Bar(
        x=[f[1] for f in gap_counter],
        y=[f[0] for f in gap_counter],
        orientation="h",
        marker=dict(
            color='rgba(55, 138, 221, 0.85)', # Warna Secondary Biru kustom Anda
            line=dict(color="#378ADD", width=1)
        ),
        text=[f"<b>{f[1]} MK</b>" for f in gap_counter],
        textposition="inside",
        insidetextanchor="middle",
        width=0.65,
    ))
    fig.update_layout(
        height=380,
        margin=dict(l=0, r=20, t=10, b=10),
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(autorange="reversed", tickfont=dict(size=12, color="#0F172A")),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.info("Gunakan menu **Pages** di sidebar kiri untuk navigasi ke halaman Rekomendasi Karir, Gap Analysis, dan Explainability XAI.")