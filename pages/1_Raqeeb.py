import streamlit as st
import pandas as pd
import os

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
    st.markdown("<p style='color:#aaa; font-size:15px;'>Search for any medication by name, code, or type — partial match supported.</p>",
                unsafe_allow_html=True)

    search_q = st.text_input("🔍 Search medication", placeholder="e.g. Gonal, 101545, Hormones",
                              key="raqeeb_item_search")

    if search_q.strip():
        q = search_q.strip().lower()
        mask = (
            medications_df['Material Description'].str.lower().str.contains(q, na=False) |
            medications_df['Material'].astype(str).str.lower().str.contains(q, na=False) |
            medications_df['Material Type'].str.lower().str.contains(q, na=False)
        )
        results = medications_df[mask].reset_index(drop=True)

        if len(results) == 0:
            st.warning("⚠️ No results found.")
        else:
            st.markdown(f"<p style='color:{TEAL}; font-weight:600;'>"
                        f"Found <b>{len(results)}</b> result(s)</p>",
                        unsafe_allow_html=True)

            # Group by Material Type
            for mat_type, grp in results.groupby('Material Type'):
                st.markdown(f"""
                <div style="background:#1e1e2e; border-left:4px solid {ORANGE};
                            padding:8px 14px; border-radius:6px; margin:12px 0 6px 0;">
                    <span style="color:{ORANGE}; font-weight:700;">📦 {mat_type}</span>
                    <span style="color:#666; font-size:12px; margin-left:8px;">{len(grp)} item(s)</span>
                </div>
                """, unsafe_allow_html=True)

                for _, item in grp.iterrows():
                    st.markdown(f"""
                    <div style="background:#12122a; border:1px solid #2a2a3a;
                                padding:12px 16px; border-radius:8px; margin:4px 0;">
                        <span style="color:white; font-size:15px; font-weight:600;">
                            {item['Material Description']}
                        </span>
                        <span style="color:#555; font-size:12px; margin-left:10px;">
                            Code: {item['Material']}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        # Show all grouped by type
        st.markdown(f"<p style='color:#666; font-size:13px;'>Showing all {len(medications_df)} medications:</p>",
                    unsafe_allow_html=True)
        for mat_type, grp in medications_df.groupby('Material Type'):
            with st.expander(f"📦 {mat_type}  ({len(grp)} items)"):
                for _, item in grp.iterrows():
                    st.markdown(f"""
                    <div style="padding:6px 0; border-bottom:1px solid #1e1e2e;">
                        <span style="color:white;">{item['Material Description']}</span>
                        <span style="color:#555; font-size:12px; margin-left:8px;">
                            {item['Material']}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
