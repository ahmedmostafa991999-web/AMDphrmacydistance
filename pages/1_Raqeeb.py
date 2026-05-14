import streamlit as st
import pandas as pd
import os
import io
import base64
from PIL import Image

st.set_page_config(
    page_title="Raqeeb – United Pharmacy",
    page_icon="💊",
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
        border-left: 5px solid {TEAL};
        padding: 18px 22px; border-radius: 12px;
        margin: 10px 0; color: white;
    }}
    .badge {{
        display: inline-block; padding: 4px 12px;
        border-radius: 20px; font-size: 13px;
        font-weight: 600; margin: 3px 4px;
    }}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-style">💊 Raqeeb – Medication & Branch Directory</div>',
            unsafe_allow_html=True)

# ── Data ─────────────────────────────────────────────────────────────────────

@st.cache_data
def load_branches():
    data = [
        {"Pharmacy": "United 018", "City": "Jeddah",        "Doctor": "مطلق الحارثي",           "Phone": "0545373932"},
        {"Pharmacy": "United 421", "City": "Jeddah",        "Doctor": "خالد المالكي",            "Phone": "0562119192"},
        {"Pharmacy": "United 104", "City": "Jeddah",        "Doctor": "راشد عمر باريان",         "Phone": "0565550061"},
        {"Pharmacy": "United 400", "City": "Jeddah",        "Doctor": "",                        "Phone": ""},
        {"Pharmacy": "United 475", "City": "Jeddah",        "Doctor": "",                        "Phone": ""},
        {"Pharmacy": "United 155", "City": "Jeddah",        "Doctor": "",                        "Phone": ""},
        {"Pharmacy": "United 305", "City": "Jeddah",        "Doctor": "",                        "Phone": ""},
        {"Pharmacy": "United 217", "City": "Al Dammam",     "Doctor": "احمد سعيد العباد",        "Phone": "0547447796"},
        {"Pharmacy": "United 336", "City": "Abha",          "Doctor": "لمى علي محمد مشبب",      "Phone": "0580990587"},
        {"Pharmacy": "United 337", "City": "Abha",          "Doctor": "",                        "Phone": ""},
        {"Pharmacy": "United 337", "City": "Khamis Mushait","Doctor": "امجد الملحم",             "Phone": "0508376393"},
        {"Pharmacy": "United 348", "City": "Taif",          "Doctor": "حمزه محمد غندوره",       "Phone": "0538374438"},
        {"Pharmacy": "United 354", "City": "Hail",          "Doctor": "عبد الكريم هليل الشمري", "Phone": "0546081312"},
        {"Pharmacy": "United 107", "City": "Hail",          "Doctor": "",                        "Phone": ""},
        {"Pharmacy": "United 358", "City": "Riyadh",        "Doctor": "فاطمه غزاي العتيبي",     "Phone": "0541820997"},
        {"Pharmacy": "United 120", "City": "Madinah",       "Doctor": "",                        "Phone": ""},
    ]
    return pd.DataFrame(data)

@st.cache_data
def load_medications():
    path = os.path.join(os.path.dirname(__file__), '..', 'RAQEEB MEDICATION LIST.xlsx')
    return pd.read_excel(path)

branches_df   = load_branches()
medications_df = load_medications()

all_cities = sorted(branches_df['City'].unique())

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
c2.metric("🏙️ Cities", branches_df['City'].nunique())
st.sidebar.metric("💊 Medications", len(medications_df))
st.sidebar.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_city, tab_item = st.tabs(["🏙️ Search by City", "🔍 Search by Item"])


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1 — SEARCH BY CITY
# ══════════════════════════════════════════════════════════════════════════════
with tab_city:
    st.markdown(f"<p style='color:#aaa; font-size:15px;'>Select a city to see Raqeeb-responsible branches and doctor info.</p>",
                unsafe_allow_html=True)

    selected_city = st.selectbox("🏙️ Select City", options=["— Choose a city —"] + all_cities,
                                  key="raqeeb_city")

    if selected_city and selected_city != "— Choose a city —":
        city_df = branches_df[branches_df['City'] == selected_city].reset_index(drop=True)
        st.markdown(f"<p style='color:{TEAL}; font-weight:600; margin-top:10px;'>"
                    f"Found <b>{len(city_df)}</b> branch(es) in <b>{selected_city}</b></p>",
                    unsafe_allow_html=True)

        for _, row in city_df.iterrows():
            doctor  = row['Doctor'] if row['Doctor'] else "—"
            phone   = row['Phone']  if row['Phone']  else "—"
            phone_link = f"<a href='tel:{phone}' style='color:{TEAL};'>{phone}</a>" if row['Phone'] else "—"

            st.markdown(f"""
            <div class="info-card">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
                    <div>
                        <span style="font-size:18px; font-weight:700; color:{ORANGE};">
                            🏥 {row['Pharmacy']}
                        </span>
                        <span style="color:#888; font-size:13px; margin-left:10px;">📍 {row['City']}</span>
                    </div>
                </div>
                <div style="margin-top:12px; display:flex; gap:30px; flex-wrap:wrap;">
                    <div>
                        <span style="color:#aaa; font-size:12px;">👨‍⚕️ Doctor</span><br>
                        <span style="font-size:15px; font-weight:600; color:white;">
                            {'<span style="color:#555;">Not assigned</span>' if doctor == '—' else doctor}
                        </span>
                    </div>
                    <div>
                        <span style="color:#aaa; font-size:12px;">📞 Phone</span><br>
                        <span style="font-size:15px; font-weight:600;">{phone_link}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2 — SEARCH BY ITEM
# ══════════════════════════════════════════════════════════════════════════════
with tab_item:
    st.markdown("<p style='color:#aaa; font-size:15px;'>Type any part of the name or code — results filter as you select.</p>",
                unsafe_allow_html=True)

    # Build options list for selectbox
    ITEM_PLACEHOLDER = "— Type to search medication —"
    med_options = [ITEM_PLACEHOLDER] + [
        f"{row['Material']}  ·  {row['Material Description']}  ·  {row['Material Type']}"
        for _, row in medications_df.iterrows()
    ]

    selected_med = st.selectbox("🔍 Search medication", options=med_options,
                                 index=0, key="raqeeb_item_sel")

    if selected_med and selected_med != ITEM_PLACEHOLDER:
        # Parse selected
        parts      = selected_med.split("  ·  ")
        sel_code   = parts[0].strip()
        sel_name   = parts[1].strip() if len(parts) > 1 else ""
        sel_type   = parts[2].strip() if len(parts) > 2 else ""

        st.markdown(f"""
        <div style="background:#1a1a2e; border-left:5px solid {TEAL};
                    padding:20px 24px; border-radius:12px; margin-top:16px;">
            <div style="color:{TEAL}; font-size:13px; font-weight:600; margin-bottom:6px;">
                📦 {sel_type}
            </div>
            <div style="color:white; font-size:20px; font-weight:700; margin-bottom:8px;">
                {sel_name}
            </div>
            <div style="color:#888; font-size:13px;">
                Material Code: <span style="color:{ORANGE}; font-weight:600;">{sel_code}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Show other items in same type
        same_type = medications_df[medications_df['Material Type'] == sel_type]
        same_type = same_type[same_type['Material'].astype(str) != sel_code]
        if len(same_type) > 0:
            st.markdown(f"<p style='color:#555; font-size:13px; margin-top:16px;'>"
                        f"Other items in <b>{sel_type}</b> ({len(same_type)}):</p>",
                        unsafe_allow_html=True)
            for _, item in same_type.iterrows():
                st.markdown(f"""
                <div style="background:#12122a; border:1px solid #1e1e2e;
                            padding:10px 14px; border-radius:8px; margin:3px 0;
                            color:#aaa; font-size:14px;">
                    {item['Material Description']}
                    <span style="color:#444; font-size:12px; margin-left:8px;">{item['Material']}</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        # Show all grouped by type
        st.markdown(f"<p style='color:#666; font-size:13px; margin-top:8px;'>All {len(medications_df)} medications:</p>",
                    unsafe_allow_html=True)
        for mat_type, grp in medications_df.groupby('Material Type'):
            with st.expander(f"📦 {mat_type}  ({len(grp)} items)"):
                for _, item in grp.iterrows():
                    st.markdown(f"""
                    <div style="padding:6px 0; border-bottom:1px solid #1e1e2e;">
                        <span style="color:white;">{item['Material Description']}</span>
                        <span style="color:#555; font-size:12px; margin-left:8px;">{item['Material']}</span>
                    </div>
                    """, unsafe_allow_html=True)