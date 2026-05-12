import streamlit as st
import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2
import folium
from streamlit_folium import st_folium
import re

# MUST be first Streamlit command
st.set_page_config(
    page_title="Pharmacy Branch Distance Dashboard",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'tab1_result' not in st.session_state:
    st.session_state.tab1_result = None
if 'tab2_result' not in st.session_state:
    st.session_state.tab2_result = None
if 'tab1_map' not in st.session_state:
    st.session_state.tab1_map = None
if 'tab2_map' not in st.session_state:
    st.session_state.tab2_map = None

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');

    .main {
        font-family: 'Cairo', sans-serif;
        background-color: #0e1117;
    }

    /* Dark theme adjustments */
    .stTextInput > div > div > input {
        background-color: #262730;
        color: white;
        border: 1px solid #4a4a4a;
        border-radius: 8px;
        padding: 12px;
        font-size: 16px;
    }

    .stTextArea > div > div > textarea {
        background-color: #262730;
        color: white;
        border: 1px solid #4a4a4a;
        border-radius: 8px;
        padding: 12px;
        font-size: 14px;
    }

    .stButton>button {
        background-color: #0066CC;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 16px;
        border: none;
        transition: all 0.3s;
    }

    .stButton>button:hover {
        background-color: #0052a3;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,102,204,0.4);
    }

    .result-card {
        background-color: #1e1e2e;
        border-right: 5px solid #0066CC;
        padding: 25px;
        border-radius: 15px;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }

    .distance-badge {
        background-color: #0066CC;
        color: white;
        padding: 12px 24px;
        border-radius: 25px;
        font-weight: bold;
        font-size: 20px;
        display: inline-block;
        margin: 8px;
        box-shadow: 0 2px 8px rgba(0,102,204,0.3);
    }

    .time-badge {
        background-color: #28a745;
        color: white;
        padding: 12px 24px;
        border-radius: 25px;
        font-weight: bold;
        font-size: 20px;
        display: inline-block;
        margin: 8px;
        box-shadow: 0 2px 8px rgba(40,167,69,0.3);
    }

    .branch-info {
        background-color: #2d2d3a;
        border: 1px solid #ffc107;
        padding: 20px;
        border-radius: 12px;
        margin: 8px 0;
        color: white;
    }

    .header-style {
        color: #0066CC;
        font-weight: 700;
        font-size: 32px;
        text-align: center;
        margin-bottom: 25px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }

    .sub-header {
        color: #e0e0e0;
        font-weight: 600;
        font-size: 22px;
        margin: 18px 0;
    }

    .rtl-text {
        direction: rtl;
        text-align: right;
    }

    .ltr-text {
        direction: ltr;
        text-align: left;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #262730;
        border-radius: 8px 8px 0 0;
        padding: 12px 24px;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background-color: #0066CC !important;
        color: white !important;
    }

    /* Dataframe styling */
    .stDataFrame {
        background-color: #1e1e2e;
        border-radius: 12px;
        padding: 10px;
    }

    /* Sidebar */
    .css-1d391kg {
        background-color: #1e1e2e;
    }

    /* Metric cards */
    .metric-card {
        background-color: #262730;
        border: 2px solid #4a4a4a;
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        transition: transform 0.3s;
    }

    .metric-card:hover {
        transform: translateY(-5px);
        border-color: #0066CC;
    }

    .metric-value {
        font-size: 36px;
        font-weight: bold;
        color: #0066CC;
    }

    .metric-label {
        font-size: 14px;
        color: #aaa;
        margin-top: 8px;
    }

    /* Arrow between branches */
    .arrow-container {
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 40px;
        color: #0066CC;
    }

    /* Warning/Info boxes */
    .info-box {
        background-color: #1e3a5f;
        border-left: 4px solid #0066CC;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        color: #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# Haversine distance calculation
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

def estimate_driving_time(distance_km, city_name=""):
    city_name = city_name.lower()
    big_cities = ['jeddah', 'riyadh', 'makkah', 'mecca', 'madinah', 'medina', 'dammam', 'khobar']

    if distance_km <= 5:
        speed = 25
    elif distance_km <= 20:
        if any(city in city_name for city in big_cities):
            speed = 35
        else:
            speed = 50
    elif distance_km <= 50:
        speed = 70
    elif distance_km <= 100:
        speed = 90
    else:
        speed = 110

    time_hours = distance_km / speed
    time_minutes = time_hours * 60
    return round(time_minutes, 1), round(speed, 1)

def format_time(minutes):
    if minutes < 60:
        return f"{int(minutes)} دقيقة"
    else:
        hours = int(minutes // 60)
        mins = int(minutes % 60)
        if mins == 0:
            return f"{hours} ساعة"
        return f"{hours} ساعة {mins} دقيقة"

def format_time_en(minutes):
    if minutes < 60:
        return f"{int(minutes)} min"
    else:
        hours = int(minutes // 60)
        mins = int(minutes % 60)
        if mins == 0:
            return f"{hours} hr"
        return f"{hours} hr {mins} min"

def extract_city(address):
    cities = ['Jeddah', 'Makkah', 'Mecca', 'Madinah', 'Medina', 'Riyadh', 'Dammam', 'Khobar', 
              'Taif', 'Khamis Mushait', 'Abha', 'Hail', 'Jizan', 'Tabuk', 'Najran', 'Buraydah',
              'Unayzah', 'Al-Ahsa', 'Al-Hofuf', 'Al-Qatif', 'Al-Qunfudhah', 'Bisha', 'Yanbu',
              'Al-Baha', 'Arar', 'Sakaka', 'Turaif', 'Al-Kharj', 'Al-Khafji', 'Jubail',
              'Al-Majmaah', 'Hafar Al Batin', 'Al-Rass', 'Al-Zulfi', 'Baljurashi', 'Bariq',
              'Mahayel Asir', 'Ahad Rofida', 'Sarat Ebidah', 'Al-Makhwah', 'Al-Mandaq',
              'Al-Mubarraz', 'Al-Muzaylif', 'Al-Namas', 'Al-Qouz', 'Al-Aridhah',
              'Abu Areesh', 'Samtah', 'Saihat', 'Anak', 'Khulais', 'Rabigh', 'Al-Qurayyat',
              'Al-Henakiyah', 'Al-Jumum', 'Sabt Al-Alayah', 'Al-Wajh', 'Umluj', 'Baqaa',
              'Shaqra', 'Tubarjal', 'Al-Badayea', 'KAUST', 'Al-Haqu', 'Al-Qahma',
              'Farasan Island', 'Sharora', 'Al-Hait', 'Uyun Al-Jawa', 'Tayma',
              'Tathleeth', 'Badr', 'Al-Darb', 'Al-Aqiq', 'Al-Majarda', 'Duba',
              'Al-Nuairyah', 'Sabya', 'Mahd Al-Thahab']

    address_lower = address.lower()
    for city in cities:
        if city.lower() in address_lower:
            return city
    return "Unknown"

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_excel('branches_data.xlsx')
    except:
        try:
            df = pd.read_excel('/mnt/agents/output/branches_data.xlsx')
        except:
            df = pd.read_excel('https://raw.githubusercontent.com/streamlit/pharmacy-dashboard/main/branches_data.xlsx')

    df = df[df['SAP Store Code'] != 'SAP Store Code']
    df = df.dropna(subset=['SAP Store Code', 'Latitude', 'Longitude'])
    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
    df = df.dropna(subset=['Latitude', 'Longitude'])
    df = df.drop_duplicates(subset=['SAP Store Code'], keep='first')
    df = df.reset_index(drop=True)
    if 'City' not in df.columns:
        df['City'] = df['English Address'].apply(extract_city)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Sidebar
st.sidebar.markdown("""
<div style="text-align: center; padding: 20px 0;">
    <h2 style="color: #0066CC;">💊 نظام المسافات</h2>
    <p style="color: #888;">Pharmacy Branch Distance System</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# Stats in sidebar
col1, col2 = st.sidebar.columns(2)
with col1:
    st.metric("الفروع", f"{len(df)}")
with col2:
    st.metric("المدن", f"{df['City'].nunique()}")

st.sidebar.markdown("---")

# Language selector
language = st.sidebar.radio(
    "اللغة / Language",
    ["🇪🇬 العربية", "🇬🇧 English"],
    index=0
)

is_arabic = language == "🇪🇬 العربية"

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="font-size: 12px; color: #888; text-align: center; direction: rtl;">
    <p>⚠️ المسافات تقريبية (خط مستقيم)</p>
    <p>الوقت تقديري بناءً على نوع الطريق</p>
    <p style="margin-top: 10px; color: #555;">v1.1 - Persistent Results</p>
</div>
""", unsafe_allow_html=True)

# ==================== ARABIC INTERFACE ====================
if is_arabic:
    st.markdown('<div class="header-style rtl-text">📍 نظام حساب المسافات بين فروع الصيدليات</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🔍 مقارنة فرعين", "📊 فرع vs مجموعة", "🗺️ الخريطة التفاعلية"])

    # ===== TAB 1: Compare Two Branches =====
    with tab1:
        st.markdown('<div class="sub-header rtl-text">أدخل رقمي الفرعين للمقارنة</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            branch1_code = st.text_input("🔹 رقم الفرع الأول", value="P001", key="b1_ar")
        with col2:
            branch2_code = st.text_input("🔹 رقم الفرع الثاني", value="P300", key="b2_ar")

        if st.button("🔍 احسب المسافة", key="calc1_ar", use_container_width=True):
            branch1 = df[df['SAP Store Code'].str.upper() == branch1_code.upper().strip()]
            branch2 = df[df['SAP Store Code'].str.upper() == branch2_code.upper().strip()]

            if len(branch1) == 0:
                st.error(f"❌ الفرع {branch1_code} غير موجود في قاعدة البيانات!")
                st.session_state.tab1_result = None
            elif len(branch2) == 0:
                st.error(f"❌ الفرع {branch2_code} غير موجود في قاعدة البيانات!")
                st.session_state.tab1_result = None
            else:
                b1 = branch1.iloc[0]
                b2 = branch2.iloc[0]

                distance = haversine_distance(b1['Latitude'], b1['Longitude'], 
                                            b2['Latitude'], b2['Longitude'])
                time_min, speed = estimate_driving_time(distance, b1['City'])

                # Save to session state
                st.session_state.tab1_result = {
                    'b1_code': b1['SAP Store Code'],
                    'b1_address': b1['English Address'],
                    'b1_city': b1['City'],
                    'b1_lat': b1['Latitude'],
                    'b1_lon': b1['Longitude'],
                    'b2_code': b2['SAP Store Code'],
                    'b2_address': b2['English Address'],
                    'b2_city': b2['City'],
                    'b2_lat': b2['Latitude'],
                    'b2_lon': b2['Longitude'],
                    'distance': distance,
                    'time': time_min,
                    'speed': speed
                }
                st.rerun()

        # Display result from session state
        if st.session_state.tab1_result:
            r = st.session_state.tab1_result

            st.markdown("---")
            st.markdown(f"""
            <div class="result-card rtl-text">
                <h3 style="color: #0066CC; margin-bottom: 20px;">📊 نتيجة المقارنة</h3>
                <div style="display: flex; justify-content: space-between; align-items: stretch; margin: 20px 0; gap: 15px;">
                    <div class="branch-info" style="flex: 1; text-align: right;">
                        <h4 style="color: #ffc107; margin-bottom: 10px;">🔹 الفرع الأول: {r['b1_code']}</h4>
                        <p style="font-size: 14px; line-height: 1.6;">{r['b1_address']}</p>
                        <p style="color: #888; font-size: 13px; margin-top: 8px;">📍 {r['b1_city']}</p>
                    </div>
                    <div class="arrow-container">
                        ⬅️
                    </div>
                    <div class="branch-info" style="flex: 1; text-align: right;">
                        <h4 style="color: #ffc107; margin-bottom: 10px;">🔹 الفرع الثاني: {r['b2_code']}</h4>
                        <p style="font-size: 14px; line-height: 1.6;">{r['b2_address']}</p>
                        <p style="color: #888; font-size: 13px; margin-top: 8px;">📍 {r['b2_city']}</p>
                    </div>
                </div>
                <div style="text-align: center; margin-top: 25px; padding: 20px; background-color: #262730; border-radius: 12px;">
                    <span class="distance-badge">📏 {r['distance']:.1f} كم</span>
                    <span class="time-badge">🚗 {format_time(r['time'])}</span>
                    <p style="color: #888; margin-top: 15px; font-size: 14px;">⚡ متوسط السرعة المقدرة: {r['speed']} كم/س</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Map
            m = folium.Map(location=[(r['b1_lat'] + r['b2_lat'])/2, 
                                    (r['b1_lon'] + r['b2_lon'])/2], 
                          zoom_start=10)
            folium.Marker([r['b1_lat'], r['b1_lon']], 
                         popup=f"{r['b1_code']}", 
                         tooltip=f"الفرع 1: {r['b1_code']}",
                         icon=folium.Icon(color='blue', icon='play', prefix='fa')).add_to(m)
            folium.Marker([r['b2_lat'], r['b2_lon']], 
                         popup=f"{r['b2_code']}", 
                         tooltip=f"الفرع 2: {r['b2_code']}",
                         icon=folium.Icon(color='red', icon='stop', prefix='fa')).add_to(m)
            folium.PolyLine([(r['b1_lat'], r['b1_lon']), 
                            (r['b2_lat'], r['b2_lon'])], 
                           color='#00ff88', weight=4, opacity=0.8).add_to(m)
            st_folium(m, width=700, height=400, key="tab1_map")

    # ===== TAB 2: One vs Many =====
    with tab2:
        st.markdown('<div class="sub-header rtl-text">أدخل فرع مرجعي + مجموعة فروع للترتيب</div>', unsafe_allow_html=True)

        source_branch = st.text_input("🔹 رقم الفرع المرجعي", value="P001", key="source_ar")

        st.markdown("<p class='rtl-text' style='color: #aaa; margin-bottom: 8px;'>أدخل أرقام الفروع المقارنة (مفصولة بفاصلة أو سطر جديد):</p>", unsafe_allow_html=True)
        target_branches = st.text_area("", value="P002, P003, P004, P005, P010", height=100, key="targets_ar")

        if st.button("📊 رتب من الأقرب", key="calc2_ar", use_container_width=True):
            source = df[df['SAP Store Code'].str.upper() == source_branch.upper().strip()]

            if len(source) == 0:
                st.error(f"❌ الفرع {source_branch} غير موجود!")
                st.session_state.tab2_result = None
            else:
                src = source.iloc[0]
                target_list = [t.strip().upper() for t in re.split(r'[,\n]', target_branches) if t.strip()]

                results = []
                errors = []
                for t_code in target_list:
                    target = df[df['SAP Store Code'].str.upper() == t_code]
                    if len(target) > 0:
                        tgt = target.iloc[0]
                        dist = haversine_distance(src['Latitude'], src['Longitude'],
                                                tgt['Latitude'], tgt['Longitude'])
                        time_min, speed = estimate_driving_time(dist, src['City'])
                        results.append({
                            'الترتيب': len(results) + 1,
                            'رقم الفرع': t_code,
                            'العنوان': tgt['English Address'],
                            'المدينة': tgt['City'],
                            'المسافة (كم)': round(dist, 1),
                            'الوقت': format_time(time_min),
                            'السرعة (كم/س)': speed,
                            'lat': tgt['Latitude'],
                            'lon': tgt['Longitude']
                        })
                    else:
                        errors.append(t_code)

                if results:
                    results_df = pd.DataFrame(results).sort_values('المسافة (كم)')
                    results_df['الترتيب'] = range(1, len(results_df) + 1)

                    st.session_state.tab2_result = {
                        'source_code': src['SAP Store Code'],
                        'source_address': src['English Address'],
                        'source_city': src['City'],
                        'source_lat': src['Latitude'],
                        'source_lon': src['Longitude'],
                        'results': results_df.to_dict('records'),
                        'errors': errors
                    }
                    st.rerun()
                else:
                    st.warning("⚠️ لم يتم العثور على أي من الفروع المدخلة!")

        # Display result from session state
        if st.session_state.tab2_result:
            r = st.session_state.tab2_result

            st.markdown("---")
            st.markdown(f"""
            <div class="result-card rtl-text">
                <h3 style="color: #0066CC; margin-bottom: 15px;">📊 الفروع مرتبة من الأقرب لـ {r['source_code']}</h3>
                <p style="color: #888; margin-bottom: 15px;">📍 {r['source_address']} ({r['source_city']})</p>
            </div>
            """, unsafe_allow_html=True)

            if r['errors']:
                st.warning(f"⚠️ فروع غير موجودة: {', '.join(r['errors'])}")

            results_df = pd.DataFrame(r['results'])
            display_df = results_df[['الترتيب', 'رقم الفرع', 'المدينة', 'المسافة (كم)', 'الوقت']].copy()

            # Color coding based on distance
            def highlight_distance(val):
                if val <= 10:
                    return 'background-color: #1b5e20; color: white'
                elif val <= 50:
                    return 'background-color: #f57f17; color: white'
                elif val <= 100:
                    return 'background-color: #e65100; color: white'
                else:
                    return 'background-color: #b71c1c; color: white'

            styled_df = display_df.style.map(highlight_distance, subset=['المسافة (كم)'])
            st.dataframe(styled_df, use_container_width=True, hide_index=True, height=400)

            # Show top 5 on map
            st.markdown("<h4 class='rtl-text' style='color: #e0e0e0; margin-top: 20px;'>🗺️ أقرب 5 فروع على الخريطة</h4>", unsafe_allow_html=True)

            top5 = results_df.head(5)
            m = folium.Map(location=[r['source_lat'], r['source_lon']], zoom_start=6)
            folium.Marker([r['source_lat'], r['source_lon']], 
                         popup=f"مرجع: {r['source_code']}", 
                         tooltip=f"📍 {r['source_code']} (المرجع)",
                         icon=folium.Icon(color='black', icon='star', prefix='fa')).add_to(m)

            colors = ['red', 'orange', 'yellow', 'green', 'blue']
            color_names = ['أحمر', 'برتقالي', 'أصفر', 'أخضر', 'أزرق']

            for idx, row in top5.iterrows():
                color = colors[min(idx, len(colors)-1)]
                folium.Marker([row['lat'], row['lon']], 
                             popup=f"{row['رقم الفرع']} - {row['المسافة (كم)']} كم",
                             tooltip=f"#{idx+1} {row['رقم الفرع']} ({row['المدينة']})",
                             icon=folium.Icon(color=color, icon='circle', prefix='fa')).add_to(m)
                folium.PolyLine([(r['source_lat'], r['source_lon']),
                                (row['lat'], row['lon'])],
                               color=color, weight=3, opacity=0.7).add_to(m)

            # Legend
            legend_html = """
            <div style="position: fixed; bottom: 50px; right: 50px; z-index: 1000; 
                        background-color: rgba(30,30,46,0.95); padding: 15px; border-radius: 10px;
                        border: 1px solid #4a4a4a; color: white; font-size: 12px;">
                <h4 style="margin: 0 0 10px 0; color: #ffc107;">🎯 الترتيب</h4>
                <div><span style="color: red;">●</span> #1 الأقرب</div>
                <div><span style="color: orange;">●</span> #2</div>
                <div><span style="color: yellow;">●</span> #3</div>
                <div><span style="color: green;">●</span> #4</div>
                <div><span style="color: blue;">●</span> #5</div>
            </div>
            """
            m.get_root().html.add_child(folium.Element(legend_html))

            st_folium(m, width=700, height=450, key="tab2_map")

    # ===== TAB 3: Map View =====
    with tab3:
        st.markdown('<div class="sub-header rtl-text">🗺️ خريطة جميع الفروع التفاعلية</div>', unsafe_allow_html=True)

        all_cities = sorted(df['City'].unique())
        city_filter = st.multiselect("🔍 تصفية بالمدينة", 
                                    options=all_cities,
                                    default=[],
                                    key="city_filter_ar")

        filtered_df = df if not city_filter else df[df['City'].isin(city_filter)]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 الفروع المعروضة", len(filtered_df))
        with col2:
            st.metric("🏙️ المدن", filtered_df['City'].nunique())
        with col3:
            avg_lat = filtered_df['Latitude'].mean()
            avg_lon = filtered_df['Longitude'].mean()
            st.metric("📍 مركز الخريطة", f"{avg_lat:.2f}, {avg_lon:.2f}")

        if len(filtered_df) > 0:
            m = folium.Map(location=[filtered_df['Latitude'].mean(), filtered_df['Longitude'].mean()], 
                          zoom_start=5,
                          tiles='CartoDB dark_matter')

            for idx, row in filtered_df.iterrows():
                folium.CircleMarker(
                    [row['Latitude'], row['Longitude']],
                    radius=5,
                    popup=f"""
                    <div style="direction: rtl; text-align: right; font-family: Cairo;">
                        <b>{row['SAP Store Code']}</b><br>
                        {row['English Address']}<br>
                        <span style="color: #666;">📍 {row['City']}</span>
                    </div>
                    """,
                    tooltip=row['SAP Store Code'],
                    color='#0066CC',
                    fill=True,
                    fillColor='#0066CC',
                    fillOpacity=0.8
                ).add_to(m)

            st_folium(m, width=800, height=600, key="full_map")

        st.markdown("---")
        st.markdown("<h4 class='rtl-text' style='color: #e0e0e0;'>📋 قائمة الفروع</h4>", unsafe_allow_html=True)
        display_df = filtered_df[['SAP Store Code', 'English Address', 'City', 'Latitude', 'Longitude']].copy()
        display_df.columns = ['رقم الفرع', 'العنوان', 'المدينة', 'خط العرض', 'خط الطول']
        st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)

# ==================== ENGLISH INTERFACE ====================
else:
    st.markdown('<div class="header-style">📍 Pharmacy Branch Distance Dashboard</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🔍 Compare Two", "📊 One vs Many", "🗺️ Full Map"])

    with tab1:
        st.markdown('<div class="sub-header">Enter two branch codes to compare</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            branch1_code = st.text_input("🔹 First Branch", value="P001", key="b1_en")
        with col2:
            branch2_code = st.text_input("🔹 Second Branch", value="P300", key="b2_en")

        if st.button("🔍 Calculate Distance", key="calc1_en", use_container_width=True):
            branch1 = df[df['SAP Store Code'].str.upper() == branch1_code.upper().strip()]
            branch2 = df[df['SAP Store Code'].str.upper() == branch2_code.upper().strip()]

            if len(branch1) == 0:
                st.error(f"❌ Branch {branch1_code} not found!")
                st.session_state.tab1_result = None
            elif len(branch2) == 0:
                st.error(f"❌ Branch {branch2_code} not found!")
                st.session_state.tab1_result = None
            else:
                b1 = branch1.iloc[0]
                b2 = branch2.iloc[0]

                distance = haversine_distance(b1['Latitude'], b1['Longitude'], 
                                            b2['Latitude'], b2['Longitude'])
                time_min, speed = estimate_driving_time(distance, b1['City'])

                st.session_state.tab1_result = {
                    'b1_code': b1['SAP Store Code'],
                    'b1_address': b1['English Address'],
                    'b1_city': b1['City'],
                    'b1_lat': b1['Latitude'],
                    'b1_lon': b1['Longitude'],
                    'b2_code': b2['SAP Store Code'],
                    'b2_address': b2['English Address'],
                    'b2_city': b2['City'],
                    'b2_lat': b2['Latitude'],
                    'b2_lon': b2['Longitude'],
                    'distance': distance,
                    'time': time_min,
                    'speed': speed
                }
                st.rerun()

        if st.session_state.tab1_result:
            r = st.session_state.tab1_result

            st.markdown("---")
            st.markdown(f"""
            <div class="result-card">
                <h3 style="color: #0066CC; margin-bottom: 20px;">📊 Comparison Result</h3>
                <div style="display: flex; justify-content: space-between; align-items: stretch; margin: 20px 0; gap: 15px;">
                    <div class="branch-info" style="flex: 1;">
                        <h4 style="color: #ffc107; margin-bottom: 10px;">🔹 From: {r['b1_code']}</h4>
                        <p style="font-size: 14px; line-height: 1.6;">{r['b1_address']}</p>
                        <p style="color: #888; font-size: 13px; margin-top: 8px;">📍 {r['b1_city']}</p>
                    </div>
                    <div class="arrow-container">
                        ➡️
                    </div>
                    <div class="branch-info" style="flex: 1;">
                        <h4 style="color: #ffc107; margin-bottom: 10px;">🔹 To: {r['b2_code']}</h4>
                        <p style="font-size: 14px; line-height: 1.6;">{r['b2_address']}</p>
                        <p style="color: #888; font-size: 13px; margin-top: 8px;">📍 {r['b2_city']}</p>
                    </div>
                </div>
                <div style="text-align: center; margin-top: 25px; padding: 20px; background-color: #262730; border-radius: 12px;">
                    <span class="distance-badge">📏 {r['distance']:.1f} km</span>
                    <span class="time-badge">🚗 {format_time_en(r['time'])}</span>
                    <p style="color: #888; margin-top: 15px; font-size: 14px;">⚡ Estimated speed: {r['speed']} km/h</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            m = folium.Map(location=[(r['b1_lat'] + r['b2_lat'])/2, 
                                    (r['b1_lon'] + r['b2_lon'])/2], 
                          zoom_start=10)
            folium.Marker([r['b1_lat'], r['b1_lon']], 
                         popup=f"{r['b1_code']}", 
                         tooltip=f"From: {r['b1_code']}",
                         icon=folium.Icon(color='blue', icon='play', prefix='fa')).add_to(m)
            folium.Marker([r['b2_lat'], r['b2_lon']], 
                         popup=f"{r['b2_code']}", 
                         tooltip=f"To: {r['b2_code']}",
                         icon=folium.Icon(color='red', icon='stop', prefix='fa')).add_to(m)
            folium.PolyLine([(r['b1_lat'], r['b1_lon']), 
                            (r['b2_lat'], r['b2_lon'])], 
                           color='#00ff88', weight=4, opacity=0.8).add_to(m)
            st_folium(m, width=700, height=400, key="tab1_map_en")

    with tab2:
        st.markdown('<div class="sub-header">Enter source branch + multiple targets</div>', unsafe_allow_html=True)

        source_branch = st.text_input("🔹 Source Branch", value="P001", key="source_en")

        st.markdown("<p style='color: #aaa; margin-bottom: 8px;'>Enter target branch codes (comma or newline separated):</p>", unsafe_allow_html=True)
        target_branches = st.text_area("", value="P002, P003, P004, P005, P010", height=100, key="targets_en")

        if st.button("📊 Sort by Distance", key="calc2_en", use_container_width=True):
            source = df[df['SAP Store Code'].str.upper() == source_branch.upper().strip()]

            if len(source) == 0:
                st.error(f"❌ Branch {source_branch} not found!")
                st.session_state.tab2_result = None
            else:
                src = source.iloc[0]
                target_list = [t.strip().upper() for t in re.split(r'[,\n]', target_branches) if t.strip()]

                results = []
                errors = []
                for t_code in target_list:
                    target = df[df['SAP Store Code'].str.upper() == t_code]
                    if len(target) > 0:
                        tgt = target.iloc[0]
                        dist = haversine_distance(src['Latitude'], src['Longitude'],
                                                tgt['Latitude'], tgt['Longitude'])
                        time_min, speed = estimate_driving_time(dist, src['City'])
                        results.append({
                            'Rank': len(results) + 1,
                            'Branch': t_code,
                            'Address': tgt['English Address'],
                            'City': tgt['City'],
                            'Distance (km)': round(dist, 1),
                            'Time': format_time_en(time_min),
                            'Speed (km/h)': speed,
                            'lat': tgt['Latitude'],
                            'lon': tgt['Longitude']
                        })
                    else:
                        errors.append(t_code)

                if results:
                    results_df = pd.DataFrame(results).sort_values('Distance (km)')
                    results_df['Rank'] = range(1, len(results_df) + 1)

                    st.session_state.tab2_result = {
                        'source_code': src['SAP Store Code'],
                        'source_address': src['English Address'],
                        'source_city': src['City'],
                        'source_lat': src['Latitude'],
                        'source_lon': src['Longitude'],
                        'results': results_df.to_dict('records'),
                        'errors': errors
                    }
                    st.rerun()
                else:
                    st.warning("⚠️ No valid branches found!")

        if st.session_state.tab2_result:
            r = st.session_state.tab2_result

            st.markdown("---")
            st.markdown(f"""
            <div class="result-card">
                <h3 style="color: #0066CC; margin-bottom: 15px;">📊 Branches sorted by distance from {r['source_code']}</h3>
                <p style="color: #888; margin-bottom: 15px;">📍 {r['source_address']} ({r['source_city']})</p>
            </div>
            """, unsafe_allow_html=True)

            if r['errors']:
                st.warning(f"⚠️ Not found: {', '.join(r['errors'])}")

            results_df = pd.DataFrame(r['results'])
            display_df = results_df[['Rank', 'Branch', 'City', 'Distance (km)', 'Time']].copy()

            def highlight_distance(val):
                if val <= 10:
                    return 'background-color: #1b5e20; color: white'
                elif val <= 50:
                    return 'background-color: #f57f17; color: white'
                elif val <= 100:
                    return 'background-color: #e65100; color: white'
                else:
                    return 'background-color: #b71c1c; color: white'

            styled_df = display_df.style.map(highlight_distance, subset=['Distance (km)'])
            st.dataframe(styled_df, use_container_width=True, hide_index=True, height=400)

            st.markdown("<h4 style='color: #e0e0e0; margin-top: 20px;'>🗺️ Top 5 Nearest on Map</h4>", unsafe_allow_html=True)

            top5 = results_df.head(5)
            m = folium.Map(location=[r['source_lat'], r['source_lon']], zoom_start=6)
            folium.Marker([r['source_lat'], r['source_lon']], 
                         popup=f"Source: {r['source_code']}", 
                         tooltip=f"📍 {r['source_code']} (Source)",
                         icon=folium.Icon(color='black', icon='star', prefix='fa')).add_to(m)

            colors = ['red', 'orange', 'yellow', 'green', 'blue']
            for idx, row in top5.iterrows():
                color = colors[min(idx, len(colors)-1)]
                folium.Marker([row['lat'], row['lon']], 
                             popup=f"{row['Branch']} - {row['Distance (km)']} km",
                             tooltip=f"#{idx+1} {row['Branch']} ({row['City']})",
                             icon=folium.Icon(color=color, icon='circle', prefix='fa')).add_to(m)
                folium.PolyLine([(r['source_lat'], r['source_lon']),
                                (row['lat'], row['lon'])],
                               color=color, weight=3, opacity=0.7).add_to(m)

            legend_html = """
            <div style="position: fixed; bottom: 50px; right: 50px; z-index: 1000; 
                        background-color: rgba(30,30,46,0.95); padding: 15px; border-radius: 10px;
                        border: 1px solid #4a4a4a; color: white; font-size: 12px;">
                <h4 style="margin: 0 0 10px 0; color: #ffc107;">🎯 Ranking</h4>
                <div><span style="color: red;">●</span> #1 Nearest</div>
                <div><span style="color: orange;">●</span> #2</div>
                <div><span style="color: yellow;">●</span> #3</div>
                <div><span style="color: green;">●</span> #4</div>
                <div><span style="color: blue;">●</span> #5</div>
            </div>
            """
            m.get_root().html.add_child(folium.Element(legend_html))

            st_folium(m, width=700, height=450, key="tab2_map_en")

    with tab3:
        st.markdown('<div class="sub-header">🗺️ Interactive Map of All Branches</div>', unsafe_allow_html=True)

        all_cities = sorted(df['City'].unique())
        city_filter = st.multiselect("🔍 Filter by City", 
                                    options=all_cities,
                                    default=[],
                                    key="city_filter_en")

        filtered_df = df if not city_filter else df[df['City'].isin(city_filter)]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Branches", len(filtered_df))
        with col2:
            st.metric("🏙️ Cities", filtered_df['City'].nunique())
        with col3:
            avg_lat = filtered_df['Latitude'].mean()
            avg_lon = filtered_df['Longitude'].mean()
            st.metric("📍 Map Center", f"{avg_lat:.2f}, {avg_lon:.2f}")

        if len(filtered_df) > 0:
            m = folium.Map(location=[filtered_df['Latitude'].mean(), filtered_df['Longitude'].mean()], 
                          zoom_start=5,
                          tiles='CartoDB dark_matter')

            for idx, row in filtered_df.iterrows():
                folium.CircleMarker(
                    [row['Latitude'], row['Longitude']],
                    radius=5,
                    popup=f"""
                    <div style="font-family: Arial;">
                        <b>{row['SAP Store Code']}</b><br>
                        {row['English Address']}<br>
                        <span style="color: #666;">📍 {row['City']}</span>
                    </div>
                    """,
                    tooltip=row['SAP Store Code'],
                    color='#0066CC',
                    fill=True,
                    fillColor='#0066CC',
                    fillOpacity=0.8
                ).add_to(m)

            st_folium(m, width=800, height=600, key="full_map_en")

        st.markdown("---")
        st.markdown("<h4 style='color: #e0e0e0;'>📋 Branch List</h4>", unsafe_allow_html=True)
        display_df = filtered_df[['SAP Store Code', 'English Address', 'City', 'Latitude', 'Longitude']].copy()
        st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)
