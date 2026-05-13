import streamlit as st
import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2
import folium
from streamlit_folium import st_folium
import re
import os
import io
import base64
from PIL import Image

# MUST be first Streamlit command
st.set_page_config(
    page_title="United Pharmacy – Branch Distance",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'tab1_result' not in st.session_state:
    st.session_state.tab1_result = None
if 'tab2_result' not in st.session_state:
    st.session_state.tab2_result = None

# ── Brand colors ──────────────────────────────────────────────────────────────
BLUE   = "#0066CC"
TEAL   = "#00A693"
ORANGE = "#F7941D"
# ─────────────────────────────────────────────────────────────────────────────

# Custom CSS
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, .main {{
        font-family: 'Inter', sans-serif;
        background-color: #0e1117;
    }}

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {{
        background-color: #1e1e2e;
        color: white;
        border: 1px solid #3a3a4a;
        border-radius: 8px;
        font-size: 15px;
    }}

    .stButton > button {{
        background: linear-gradient(135deg, {BLUE}, {TEAL});
        color: white;
        font-weight: 700;
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 15px;
        border: none;
        transition: all 0.25s;
        letter-spacing: 0.3px;
    }}
    .stButton > button:hover {{
        opacity: 0.88;
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(0,102,204,0.35);
    }}

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {{ gap: 6px; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: #1e1e2e;
        border-radius: 8px 8px 0 0;
        padding: 11px 22px;
        font-weight: 600;
        color: #ccc;
    }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {BLUE}, {TEAL}) !important;
        color: white !important;
    }}

    .result-card {{
        background-color: #1a1a2e;
        border-left: 5px solid {TEAL};
        padding: 24px;
        border-radius: 14px;
        margin: 14px 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.35);
    }}

    .distance-badge {{
        background: linear-gradient(135deg, {BLUE}, {TEAL});
        color: white;
        padding: 11px 22px;
        border-radius: 25px;
        font-weight: bold;
        font-size: 19px;
        display: inline-block;
        margin: 6px;
    }}

    .time-badge {{
        background-color: #28a745;
        color: white;
        padding: 11px 22px;
        border-radius: 25px;
        font-weight: bold;
        font-size: 19px;
        display: inline-block;
        margin: 6px;
    }}

    .branch-info {{
        background-color: #252535;
        border: 1px solid {ORANGE};
        padding: 18px;
        border-radius: 12px;
        margin: 8px 0;
        color: white;
    }}

    .header-style {{
        color: {BLUE};
        font-weight: 700;
        font-size: 30px;
        text-align: center;
        margin-bottom: 22px;
        letter-spacing: -0.5px;
    }}

    .sub-header {{
        color: #d0d0d0;
        font-weight: 600;
        font-size: 20px;
        margin: 16px 0 10px 0;
    }}

    .arrow-container {{
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 36px;
        color: {TEAL};
    }}

    /* Color legend pill */
    .legend-pill {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        margin: 2px 4px;
        color: white;
    }}
</style>
""", unsafe_allow_html=True)


# ── Helper functions ──────────────────────────────────────────────────────────

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

def estimate_driving_time(distance_km, city_name=""):
    city_name = city_name.lower()
    big_cities = ['jeddah', 'riyadh', 'makkah', 'mecca', 'madinah', 'medina', 'dammam', 'khobar']
    if distance_km <= 5:
        speed = 25
    elif distance_km <= 20:
        speed = 35 if any(c in city_name for c in big_cities) else 50
    elif distance_km <= 50:
        speed = 70
    elif distance_km <= 100:
        speed = 90
    else:
        speed = 110
    return round(distance_km / speed * 60, 1), round(speed, 1)

def format_time(minutes):
    if minutes < 60:
        return f"{int(minutes)} min"
    h, m = int(minutes // 60), int(minutes % 60)
    return f"{h} hr" if m == 0 else f"{h} hr {m} min"

def extract_city(address):
    cities = [
        'Jeddah','Makkah','Mecca','Madinah','Medina','Riyadh','Dammam','Khobar',
        'Taif','Khamis Mushait','Abha','Hail','Jizan','Tabuk','Najran','Buraydah',
        'Unayzah','Al-Ahsa','Al-Hofuf','Al-Qatif','Al-Qunfudhah','Bisha','Yanbu',
        'Al-Baha','Arar','Sakaka','Turaif','Al-Kharj','Al-Khafji','Jubail',
        'Al-Majmaah','Hafar Al Batin','Al-Rass','Al-Zulfi','Baljurashi','Bariq',
        'Mahayel Asir','Ahad Rofida','Sarat Ebidah','Al-Makhwah','Al-Mandaq',
        'Al-Mubarraz','Al-Muzaylif','Al-Namas','Al-Qouz','Al-Aridhah',
        'Abu Areesh','Samtah','Saihat','Anak','Khulais','Rabigh','Al-Qurayyat',
        'Al-Henakiyah','Al-Jumum','Sabt Al-Alayah','Al-Wajh','Umluj','Baqaa',
        'Shaqra','Tubarjal','Al-Badayea','KAUST','Al-Haqu','Al-Qahma',
        'Farasan Island','Sharora','Al-Hait','Uyun Al-Jawa','Tayma',
        'Tathleeth','Badr','Al-Darb','Al-Aqiq','Al-Majarda','Duba',
        'Al-Nuairyah','Sabya','Mahd Al-Thahab'
    ]
    al = address.lower()
    for city in cities:
        if city.lower() in al:
            return city
    return "Unknown"

def highlight_distance(val):
    """Color rows by distance thresholds."""
    if val < 10:
        return 'background-color: #1b5e20; color: white'
    elif val < 20:
        return 'background-color: #f9a825; color: #111'
    elif val < 30:
        return 'background-color: #e65100; color: white'
    else:
        return 'background-color: #b71c1c; color: white'


# ── Load data ─────────────────────────────────────────────────────────────────

@st.cache_data
def load_data():
    for path in ['branches_data.xlsx', '/mnt/agents/output/branches_data.xlsx']:
        try:
            df = pd.read_excel(path)
            break
        except Exception:
            continue
    else:
        raise FileNotFoundError("branches_data.xlsx not found.")

    df = df[df['SAP Store Code'] != 'SAP Store Code']
    df = df.dropna(subset=['SAP Store Code', 'Latitude', 'Longitude'])
    df['Latitude']  = pd.to_numeric(df['Latitude'],  errors='coerce')
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
    df = df.dropna(subset=['Latitude', 'Longitude'])
    df = df.drop_duplicates(subset=['SAP Store Code'], keep='first').reset_index(drop=True)
    if 'City' not in df.columns:
        df['City'] = df['English Address'].apply(extract_city)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()


# ── Logo helpers ─────────────────────────────────────────────────────────────

@st.cache_data
def load_logo_base64(path):
    """Load logo, remove white background, return base64 PNG string."""
    img = Image.open(path).convert("RGBA")
    data = img.getdata()
    new_data = []
    for r, g, b, a in data:
        # Make white / near-white pixels transparent
        if r > 210 and g > 210 and b > 210:
            new_data.append((r, g, b, 0))
        else:
            new_data.append((r, g, b, a))
    img.putdata(new_data)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


# ── Sidebar ───────────────────────────────────────────────────────────────────

# Support logo.png, logo.jpg, logo.png.jpg, or logo.jpeg
_logo_candidates = ['logo.png', 'logo.jpg', 'logo.png.jpg', 'logo.jpeg']
LOGO_PATH = next(
    (os.path.join(os.path.dirname(__file__), f) for f in _logo_candidates
     if os.path.exists(os.path.join(os.path.dirname(__file__), f))),
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
else:
    logo_b64 = None
    st.sidebar.markdown(f"""
    <div style="text-align:center; padding:18px 0 10px 0;">
        <span style="font-size:28px; font-weight:800;
                     background:linear-gradient(135deg,{BLUE},{TEAL});
                     -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            United Pharmacy
        </span><br>
        <span style="color:#888; font-size:13px;">Branch Distance System</span>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")

c1, c2 = st.sidebar.columns(2)
c1.metric("Branches", len(df))
c2.metric("Cities", df['City'].nunique())

st.sidebar.markdown("---")

# Color legend
st.sidebar.markdown("""
<div style="font-size:13px; color:#bbb; padding:4px 0 8px 0; font-weight:600;">
    Distance Color Guide
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("""
<span class="legend-pill" style="background:#1b5e20;">● &lt; 10 km</span>
<span class="legend-pill" style="background:#f9a825; color:#111;">● 10–20 km</span>
<span class="legend-pill" style="background:#e65100;">● 20–30 km</span>
<span class="legend-pill" style="background:#b71c1c;">● 30+ km</span>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="font-size:11px; color:#555; text-align:center; line-height:1.8;">
    ⚠️ Distances are straight-line (aerial)<br>
    Travel time is estimated by road type<br>
    <span style="color:#444;">v2.0 — United Pharmacy</span>
</div>
""", unsafe_allow_html=True)


# ── Main header ───────────────────────────────────────────────────────────────

if LOGO_PATH and logo_b64:
    st.markdown(f"""
    <div style="display:flex; align-items:center; justify-content:center;
                gap:18px; margin-bottom:22px;">
        <img src="data:image/png;base64,{logo_b64}"
             style="height:64px; width:auto; background:transparent;">
        <span class="header-style" style="margin:0;">
            United Pharmacy – Branch Distance Dashboard
        </span>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(
        '<div class="header-style">United Pharmacy – Branch Distance Dashboard</div>',
        unsafe_allow_html=True
    )

# ── Tabs  (One vs Many is FIRST = default) ────────────────────────────────────
tab_ovm, tab_two, tab_map = st.tabs(["📊 One vs Many", "🔍 Compare Two", "🗺️ Full Map"])


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1 — ONE vs MANY
# ══════════════════════════════════════════════════════════════════════════════
with tab_ovm:
    st.markdown('<div class="sub-header">Sort branches by distance from a source branch</div>',
                unsafe_allow_html=True)

    source_branch  = st.text_input("🔹 Source Branch Code", value="P001", key="source")
    st.markdown("<p style='color:#aaa; margin-bottom:6px;'>Target branch codes (comma or newline separated):</p>",
                unsafe_allow_html=True)
    target_branches = st.text_area("", value="P002, P003, P004, P005, P010",
                                   height=100, key="targets")

    if st.button("📊 Sort by Distance", key="calc_ovm", use_container_width=True):
        source = df[df['SAP Store Code'].str.upper() == source_branch.upper().strip()]
        if len(source) == 0:
            st.error(f"❌ Branch **{source_branch}** not found in the database.")
            st.session_state.tab2_result = None
        else:
            src = source.iloc[0]
            target_list = [t.strip().upper()
                           for t in re.split(r'[,\n]', target_branches) if t.strip()]
            results, errors = [], []
            for t_code in target_list:
                tgt_row = df[df['SAP Store Code'].str.upper() == t_code]
                if len(tgt_row) > 0:
                    tgt = tgt_row.iloc[0]
                    dist = haversine_distance(src['Latitude'], src['Longitude'],
                                             tgt['Latitude'], tgt['Longitude'])
                    t_min, spd = estimate_driving_time(dist, src['City'])
                    results.append({
                        'Rank':          0,
                        'Branch':        t_code,
                        'City':          tgt['City'],
                        'Distance (km)': round(dist, 1),
                        'Time':          format_time(t_min),
                        'Speed (km/h)':  spd,
                        'lat':           tgt['Latitude'],
                        'lon':           tgt['Longitude'],
                    })
                else:
                    errors.append(t_code)

            if results:
                rdf = pd.DataFrame(results).sort_values('Distance (km)')
                rdf['Rank'] = range(1, len(rdf) + 1)
                st.session_state.tab2_result = {
                    'source_code':    src['SAP Store Code'],
                    'source_address': src['English Address'],
                    'source_city':    src['City'],
                    'source_lat':     src['Latitude'],
                    'source_lon':     src['Longitude'],
                    'results':        rdf.to_dict('records'),
                    'errors':         errors,
                }
                st.rerun()
            else:
                st.warning("⚠️ No valid branch codes found.")

    # ── Display result ────────────────────────────────────────────────────────
    if st.session_state.tab2_result:
        r = st.session_state.tab2_result
        st.markdown("---")
        st.markdown(f"""
        <div class="result-card">
            <h3 style="color:{TEAL}; margin-bottom:8px;">
                📊 Branches sorted by distance from {r['source_code']}
            </h3>
            <p style="color:#888; margin:0;">
                📍 {r['source_address']} &nbsp;·&nbsp; {r['source_city']}
            </p>
        </div>""", unsafe_allow_html=True)

        if r['errors']:
            st.warning(f"⚠️ Not found: {', '.join(r['errors'])}")

        results_df  = pd.DataFrame(r['results'])
        display_df  = results_df[['Rank', 'Branch', 'City', 'Distance (km)', 'Time']].copy()
        styled_df   = display_df.style.map(highlight_distance, subset=['Distance (km)'])
        st.dataframe(styled_df, use_container_width=True, hide_index=True, height=420)

        # ── Top 10 map ────────────────────────────────────────────────────────
        top10 = results_df.head(10).reset_index(drop=True)
        st.markdown(
            "<h4 style='color:#e0e0e0; margin-top:24px;'>🗺️ Top 10 Nearest Branches on Map</h4>",
            unsafe_allow_html=True
        )

        map_colors  = ['red','orange','green','blue','purple',
                       'darkred','darkblue','darkgreen','cadetblue','pink']
        m = folium.Map(location=[r['source_lat'], r['source_lon']], zoom_start=6)
        folium.Marker(
            [r['source_lat'], r['source_lon']],
            popup=f"Source: {r['source_code']}",
            tooltip=f"📍 {r['source_code']} (Source)",
            icon=folium.Icon(color='black', icon='star', prefix='fa')
        ).add_to(m)

        for i, row in top10.iterrows():
            color = map_colors[i % len(map_colors)]
            folium.Marker(
                [row['lat'], row['lon']],
                popup=f"{row['Branch']} – {row['Distance (km)']} km",
                tooltip=f"#{i+1} {row['Branch']} ({row['City']})",
                icon=folium.Icon(color=color, icon='circle', prefix='fa')
            ).add_to(m)
            folium.PolyLine(
                [(r['source_lat'], r['source_lon']), (row['lat'], row['lon'])],
                color=color, weight=3, opacity=0.7
            ).add_to(m)

        legend_items = "".join(
            f"<div><span style='color:{map_colors[i]};'>●</span> #{i+1} {row['Branch']}</div>"
            for i, row in top10.iterrows()
        )
        legend_html = f"""
        <div style="position:fixed; bottom:50px; right:50px; z-index:1000;
                    background:rgba(20,20,35,0.95); padding:14px 18px; border-radius:10px;
                    border:1px solid #3a3a4a; color:white; font-size:12px; line-height:1.8;">
            <b style="color:{ORANGE};">🎯 Ranking</b><br>{legend_items}
        </div>"""
        m.get_root().html.add_child(folium.Element(legend_html))
        st_folium(m, width=720, height=480, key="ovm_map")


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2 — COMPARE TWO BRANCHES
# ══════════════════════════════════════════════════════════════════════════════
with tab_two:
    st.markdown('<div class="sub-header">Enter two branch codes to compare</div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        branch1_code = st.text_input("🔹 First Branch", value="P001", key="b1")
    with col2:
        branch2_code = st.text_input("🔹 Second Branch", value="P300", key="b2")

    if st.button("🔍 Calculate Distance", key="calc_two", use_container_width=True):
        b1_rows = df[df['SAP Store Code'].str.upper() == branch1_code.upper().strip()]
        b2_rows = df[df['SAP Store Code'].str.upper() == branch2_code.upper().strip()]

        if len(b1_rows) == 0:
            st.error(f"❌ Branch **{branch1_code}** not found.")
            st.session_state.tab1_result = None
        elif len(b2_rows) == 0:
            st.error(f"❌ Branch **{branch2_code}** not found.")
            st.session_state.tab1_result = None
        else:
            b1, b2 = b1_rows.iloc[0], b2_rows.iloc[0]
            dist = haversine_distance(b1['Latitude'], b1['Longitude'],
                                      b2['Latitude'], b2['Longitude'])
            t_min, spd = estimate_driving_time(dist, b1['City'])
            st.session_state.tab1_result = dict(
                b1_code=b1['SAP Store Code'], b1_address=b1['English Address'],
                b1_city=b1['City'], b1_lat=b1['Latitude'], b1_lon=b1['Longitude'],
                b2_code=b2['SAP Store Code'], b2_address=b2['English Address'],
                b2_city=b2['City'], b2_lat=b2['Latitude'], b2_lon=b2['Longitude'],
                distance=dist, time=t_min, speed=spd
            )
            st.rerun()

    if st.session_state.tab1_result:
        r = st.session_state.tab1_result
        st.markdown("---")
        st.markdown(f"""
        <div class="result-card">
            <h3 style="color:{TEAL}; margin-bottom:18px;">📊 Comparison Result</h3>
            <div style="display:flex; gap:14px; align-items:stretch;">
                <div class="branch-info" style="flex:1;">
                    <h4 style="color:{ORANGE}; margin-bottom:8px;">🔹 From: {r['b1_code']}</h4>
                    <p style="font-size:14px; line-height:1.6; margin:0;">{r['b1_address']}</p>
                    <p style="color:#888; font-size:13px; margin-top:6px;">📍 {r['b1_city']}</p>
                </div>
                <div class="arrow-container">➡️</div>
                <div class="branch-info" style="flex:1;">
                    <h4 style="color:{ORANGE}; margin-bottom:8px;">🔹 To: {r['b2_code']}</h4>
                    <p style="font-size:14px; line-height:1.6; margin:0;">{r['b2_address']}</p>
                    <p style="color:#888; font-size:13px; margin-top:6px;">📍 {r['b2_city']}</p>
                </div>
            </div>
            <div style="text-align:center; margin-top:22px; padding:18px;
                        background:#1e1e2e; border-radius:12px;">
                <span class="distance-badge">📏 {r['distance']:.1f} km</span>
                <span class="time-badge">🚗 {format_time(r['time'])}</span>
                <p style="color:#888; margin-top:12px; font-size:13px;">
                    ⚡ Estimated avg speed: {r['speed']} km/h
                </p>
            </div>
        </div>""", unsafe_allow_html=True)

        m = folium.Map(
            location=[(r['b1_lat']+r['b2_lat'])/2, (r['b1_lon']+r['b2_lon'])/2],
            zoom_start=10
        )
        folium.Marker([r['b1_lat'], r['b1_lon']],
                      popup=r['b1_code'], tooltip=f"From: {r['b1_code']}",
                      icon=folium.Icon(color='blue', icon='play', prefix='fa')).add_to(m)
        folium.Marker([r['b2_lat'], r['b2_lon']],
                      popup=r['b2_code'], tooltip=f"To: {r['b2_code']}",
                      icon=folium.Icon(color='red', icon='stop', prefix='fa')).add_to(m)
        folium.PolyLine(
            [(r['b1_lat'], r['b1_lon']), (r['b2_lat'], r['b2_lon'])],
            color='#00ff88', weight=4, opacity=0.8
        ).add_to(m)
        st_folium(m, width=720, height=420, key="two_map")


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 3 — FULL MAP
# ══════════════════════════════════════════════════════════════════════════════
with tab_map:
    st.markdown('<div class="sub-header">🗺️ Interactive Map of All Branches</div>',
                unsafe_allow_html=True)

    # ── Controls row ──────────────────────────────────────────────────────────
    # Build neighborhood selectbox options once (all branches as searchable options)
    NBR_PLACEHOLDER = "— Type to search by neighborhood / address —"
    nbr_options = [NBR_PLACEHOLDER] + [
        f"{row['SAP Store Code']}  ·  {row['English Address'][:60]}  ·  {row['City']}"
        for _, row in df.iterrows()
    ]

    ctrl1, ctrl2, ctrl3 = st.columns([1, 2, 2])
    with ctrl1:
        search_code = st.text_input(
            "🔍 Highlight by Code",
            value="",
            placeholder="e.g. P001",
            key="map_search"
        )
    with ctrl2:
        nbr_selected = st.selectbox(
            "🏘️ Search by Neighborhood",
            options=nbr_options,
            index=0,
            key="nbr_sel"
        )
    with ctrl3:
        all_cities  = sorted(df['City'].unique())
        city_filter = st.multiselect("🏙️ Filter by City",
                                     options=all_cities, default=[],
                                     key="city_filter")

    # Neighborhood selectbox overrides code search when a branch is selected
    if nbr_selected and nbr_selected != NBR_PLACEHOLDER:
        search_code = nbr_selected.split("  ·  ")[0].strip()

    filtered_df = df if not city_filter else df[df['City'].isin(city_filter)]

    # ── Stats ─────────────────────────────────────────────────────────────────
    m1, m2, m3 = st.columns(3)
    m1.metric("📊 Branches Shown", len(filtered_df))
    m2.metric("🏙️ Cities", filtered_df['City'].nunique())
    avg_lat = filtered_df['Latitude'].mean()
    avg_lon = filtered_df['Longitude'].mean()
    m3.metric("📍 Map Center", f"{avg_lat:.2f}, {avg_lon:.2f}")

    # ── Resolve highlighted branch ────────────────────────────────────────────
    highlight_code = search_code.upper().strip()
    highlight_row  = None
    if highlight_code:
        found = df[df['SAP Store Code'].str.upper() == highlight_code]
        if len(found) > 0:
            highlight_row = found.iloc[0]
        else:
            st.warning(f"⚠️ Branch **{search_code}** not found.")

    # ── Build map ─────────────────────────────────────────────────────────────
    if len(filtered_df) > 0:
        center_lat = highlight_row['Latitude']  if highlight_row is not None else avg_lat
        center_lon = highlight_row['Longitude'] if highlight_row is not None else avg_lon
        zoom       = 13 if highlight_row is not None else 5

        m = folium.Map(location=[center_lat, center_lon],
                       zoom_start=zoom, tiles='CartoDB dark_matter')

        for _, row in filtered_df.iterrows():
            code = str(row['SAP Store Code']).upper()
            is_highlighted = (highlight_code and code == highlight_code)

            if is_highlighted:
                folium.Marker(
                    [row['Latitude'], row['Longitude']],
                    popup=folium.Popup(
                        f"<b style='color:#c00;'>{row['SAP Store Code']}</b><br>"
                        f"{row['English Address']}<br>"
                        f"<span style='color:#666;'>📍 {row['City']}</span>",
                        max_width=250),
                    tooltip=f"🔴 {row['SAP Store Code']} — {row['City']}",
                    icon=folium.Icon(color='red', icon='map-marker', prefix='fa')
                ).add_to(m)
                folium.CircleMarker(
                    [row['Latitude'], row['Longitude']],
                    radius=18, color='red', fill=False, weight=3, opacity=0.6
                ).add_to(m)
            else:
                folium.CircleMarker(
                    [row['Latitude'], row['Longitude']],
                    radius=5,
                    popup=folium.Popup(
                        f"<div style='font-family:Arial;'>"
                        f"<b>{row['SAP Store Code']}</b><br>"
                        f"{row['English Address']}<br>"
                        f"<span style='color:#666;'>📍 {row['City']}</span></div>",
                        max_width=250),
                    tooltip=row['SAP Store Code'],
                    color=BLUE, fill=True, fillColor=BLUE, fillOpacity=0.75
                ).add_to(m)

        if highlight_row is not None:
            st.success(
                f"🔴 **{highlight_row['SAP Store Code']}** highlighted  ·  "
                f"{highlight_row['English Address']}  ·  {highlight_row['City']}"
            )

        st_folium(m, width=820, height=600, key="full_map")

    # ── Branch list table ─────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("<h4 style='color:#e0e0e0;'>📋 Branch List</h4>", unsafe_allow_html=True)
    display_df = filtered_df[['SAP Store Code','English Address','City','Latitude','Longitude']].copy()
    st.dataframe(display_df, use_container_width=True, hide_index=True, height=380)
