import streamlit as st
import pandas as pd
import os
import io
import base64
from PIL import Image

st.set_page_config(
    page_title="Special Items – United Pharmacy",
    page_icon="⭐",
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
    .info-card {{
        background-color: #1a1a2e;
        border-left: 5px solid {ORANGE};
        padding: 18px 22px; border-radius: 12px;
        margin: 10px 0; color: white;
    }}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-style">⭐ Special Items – Branch Directory</div>',
            unsafe_allow_html=True)

# ── Data ─────────────────────────────────────────────────────────────────────

@st.cache_data
def load_branches():
    data = [
        # Jeddah
        {"Branch": "P300", "City": "Jeddah"},
        {"Branch": "P018", "City": "Jeddah"},
        {"Branch": "P149", "City": "Jeddah"},
        {"Branch": "P400", "City": "Jeddah"},
        {"Branch": "P167", "City": "Jeddah", "Note": "Mini Hub"},
        # Riyadh
        {"Branch": "D147", "City": "Riyadh"},
        {"Branch": "D148", "City": "Riyadh"},
        {"Branch": "D308", "City": "Riyadh"},
        {"Branch": "D069", "City": "Riyadh"},
        # Dammam
        {"Branch": "P216", "City": "Al Dammam"},
        # Al Ahsa
        {"Branch": "P250", "City": "Al Ahsa"},
        # Madinah
        {"Branch": "P436", "City": "Madinah"},
        # Makkah
        {"Branch": "P091", "City": "Makkah"},
        # Taif
        {"Branch": "P173", "City": "Taif"},
    ]
    return pd.DataFrame(data).fillna("")

@st.cache_data
def load_items():
    path = os.path.join(os.path.dirname(__file__), '..', 'Special_March_2026.xlsx')
    return pd.read_excel(path)

branches_df = load_branches()
items_df    = load_items()
all_cities  = sorted(branches_df['City'].unique())

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

# ── Sidebar stats ─────────────────────────────────────────────────────────────
st.sidebar.markdown("---")
c1, c2 = st.sidebar.columns(2)
c1.metric("🏥 Branches", len(branches_df))
c2.metric("🏙️ Cities",   branches_df['City'].nunique())
st.sidebar.metric("⭐ Special Items", len(items_df))
st.sidebar.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_city, tab_item = st.tabs(["🏙️ Search by City", "🔍 Search by Item"])


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1 — SEARCH BY CITY
# ══════════════════════════════════════════════════════════════════════════════
with tab_city:
    st.markdown("<p style='color:#aaa; font-size:15px;'>Select a city to see Special Item responsible branches.</p>",
                unsafe_allow_html=True)

    selected_city = st.selectbox("🏙️ Select City",
                                  options=["— Choose a city —"] + all_cities,
                                  key="sp_city")

    if selected_city and selected_city != "— Choose a city —":
        city_df = branches_df[branches_df['City'] == selected_city].reset_index(drop=True)

        st.markdown(f"<p style='color:{TEAL}; font-weight:600; margin-top:10px;'>"
                    f"Found <b>{len(city_df)}</b> branch(es) in <b>{selected_city}</b></p>",
                    unsafe_allow_html=True)

        for _, row in city_df.iterrows():
            note_badge = (f"<span style='background:{ORANGE}; color:white; font-size:11px; "
                          f"padding:2px 10px; border-radius:10px; margin-left:10px;'>"
                          f"{row['Note']}</span>") if row.get('Note') else ""

            st.markdown(f"""
            <div class="info-card">
                <div style="display:flex; align-items:center; gap:10px;">
                    <span style="font-size:20px; font-weight:700; color:{ORANGE};">
                        🏥 {row['Branch']}
                    </span>
                    {note_badge}
                    <span style="color:#888; font-size:13px; margin-left:6px;">📍 {row['City']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2 — SEARCH BY ITEM
# ══════════════════════════════════════════════════════════════════════════════
with tab_item:
    st.markdown("<p style='color:#aaa; font-size:15px;'>Type any part of the name or code to find a Special Item.</p>",
                unsafe_allow_html=True)

    ITEM_PLACEHOLDER = "— Type to search Special Item —"
    item_options = [ITEM_PLACEHOLDER] + [
        f"{row['Material']}  ·  {row['Material Description']}"
        for _, row in items_df.iterrows()
    ]

    selected_item = st.selectbox("⭐ Search item", options=item_options,
                                  index=0, key="sp_item_sel")

    if selected_item and selected_item != ITEM_PLACEHOLDER:
        parts    = selected_item.split("  ·  ")
        sel_code = parts[0].strip()
        sel_name = parts[1].strip() if len(parts) > 1 else ""

        st.markdown(f"""
        <div style="background:#1a1a2e; border-left:5px solid {ORANGE};
                    padding:20px 24px; border-radius:12px; margin-top:16px;">
            <div style="color:{ORANGE}; font-size:13px; font-weight:600; margin-bottom:6px;">
                ⭐ Special Item
            </div>
            <div style="color:white; font-size:20px; font-weight:700; margin-bottom:8px;">
                {sel_name}
            </div>
            <div style="color:#888; font-size:13px;">
                Material Code: <span style="color:{TEAL}; font-weight:600;">{sel_code}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown(f"<p style='color:#666; font-size:13px; margin-top:8px;'>All {len(items_df)} special items available.</p>",
                    unsafe_allow_html=True)
        with st.expander(f"⭐ Show all Special Items ({len(items_df)})"):
            for _, item in items_df.iterrows():
                st.markdown(f"""
                <div style="padding:6px 0; border-bottom:1px solid #1e1e2e;">
                    <span style="color:white;">{item['Material Description']}</span>
                    <span style="color:#555; font-size:12px; margin-left:8px;">{item['Material']}</span>
                </div>
                """, unsafe_allow_html=True)