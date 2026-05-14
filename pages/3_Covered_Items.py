import streamlit as st
import pandas as pd
import os
import io
import base64
from PIL import Image

st.set_page_config(
    page_title="Covered Items – United Pharmacy",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

BLUE   = "#0066CC"
TEAL   = "#00A693"
ORANGE = "#F7941D"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, .main {{ font-family: 'Inter', sans-serif; background-color: #0e1117; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 6px; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: #1e1e2e; border-radius: 8px 8px 0 0;
        padding: 11px 22px; font-weight: 600; color: #ccc;
    }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {BLUE}, {TEAL}) !important;
        color: white !important;
    }}
    .header-style {{
        color: {BLUE}; font-weight: 700; font-size: 28px;
        text-align: center; margin-bottom: 22px;
    }}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-style">📋 Covered Items</div>',
            unsafe_allow_html=True)

# ── Logo ─────────────────────────────────────────────────────────────────────
@st.cache_data
def load_logo_base64(path):
    img = Image.open(path).convert("RGBA")
    data = img.getdata()
    new_data = []
    for r, g, b, a in data:
        if r > 210 and g > 210 and b > 210:
            new_data.append((r, g, b, 0))
        else:
            new_data.append((r, g, b, a))
    img.putdata(new_data)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

_logo_candidates = ['logo.png', 'logo.jpg', 'logo.png.jpg', 'logo.jpeg']
_base = os.path.join(os.path.dirname(__file__), '..')
LOGO_PATH = next(
    (os.path.join(_base, f) for f in _logo_candidates
     if os.path.exists(os.path.join(_base, f))),
    None
)
if LOGO_PATH:
    logo_b64 = load_logo_base64(LOGO_PATH)
    st.sidebar.markdown(f"""
    <div style="text-align:center; padding:14px 0 6px 0;">
        <img src="data:image/png;base64,{logo_b64}"
             style="width:160px; height:auto; background:transparent;">
    </div>
    """, unsafe_allow_html=True)

# ── Data ─────────────────────────────────────────────────────────────────────
@st.cache_data
def load_meena():
    path = os.path.join(os.path.dirname(__file__), '..', 'الاصناف المغطاه على مينا ابريل 2026.xlsx')
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={'MATREIAL': 'Material', 'MATERIAL DESC': 'Description'})
    df['Material']    = df['Material'].astype(str).str.strip()
    df['Description'] = df['Description'].astype(str).str.strip()
    return df[['Material', 'Description']]

meena_df = load_meena()

# ── Sidebar stats ─────────────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.metric("📋 Meena Items", len(meena_df))
st.sidebar.metric("🚧 Tawynia Items", "Coming soon")
st.sidebar.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_meena, tab_tawynia = st.tabs(["🏥 Meena", "🏥 Tawynia"])


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1 — MEENA
# ══════════════════════════════════════════════════════════════════════════════
with tab_meena:
    st.markdown(f"<p style='color:#aaa; font-size:15px;'>Search across <b>{len(meena_df)}</b> covered items for Meena.</p>",
                unsafe_allow_html=True)

    PLACEHOLDER = "— Type to search item —"
    options = [PLACEHOLDER] + [
        f"{row['Material']}  ·  {row['Description']}"
        for _, row in meena_df.iterrows()
    ]

    selected = st.selectbox("🔍 Search Meena item", options=options,
                             index=0, key="meena_sel")

    if selected and selected != PLACEHOLDER:
        parts    = selected.split("  ·  ")
        sel_code = parts[0].strip()
        sel_name = parts[1].strip() if len(parts) > 1 else ""

        st.markdown(f"""
        <div style="background:#1a1a2e; border-left:5px solid {TEAL};
                    padding:20px 24px; border-radius:12px; margin-top:16px;">
            <div style="color:{TEAL}; font-size:13px; font-weight:600; margin-bottom:6px;">
                ✅ Covered – Meena
            </div>
            <div style="color:white; font-size:20px; font-weight:700; margin-bottom:8px;">
                {sel_name}
            </div>
            <div style="color:#888; font-size:13px;">
                Material Code: <span style="color:{ORANGE}; font-weight:600;">{sel_code}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Show total count only — no full list (3220 items is too long)
        st.markdown(f"""
        <div style="background:#1a1a2e; border:1px solid #2a2a3a;
                    padding:20px; border-radius:12px; text-align:center; margin-top:20px;">
            <div style="color:{TEAL}; font-size:36px; font-weight:700;">{len(meena_df):,}</div>
            <div style="color:#aaa; font-size:15px; margin-top:6px;">Total Covered Items – Meena</div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2 — TAWYNIA (placeholder)
# ══════════════════════════════════════════════════════════════════════════════
with tab_tawynia:
    st.markdown(f"""
    <div style="background:#1a1a2e; border:1px solid #2a2a3a;
                padding:40px; border-radius:12px; text-align:center; margin-top:20px;">
        <div style="font-size:40px;">🚧</div>
        <div style="color:#aaa; font-size:18px; margin-top:12px; font-weight:600;">
            Tawynia data coming soon
        </div>
    </div>
    """, unsafe_allow_html=True)
