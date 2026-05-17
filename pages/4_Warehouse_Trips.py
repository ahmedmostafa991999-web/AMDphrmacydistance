import streamlit as st
import pandas as pd
import os
import io
import base64
from datetime import datetime
from PIL import Image

st.set_page_config(
    page_title="Warehouse Trips – United Pharmacy",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

BLUE   = "#0066CC"
TEAL   = "#00A693"
ORANGE = "#F7941D"
GREEN  = "#2ecc71"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, .main {{ font-family: 'Inter', sans-serif; background-color: #0e1117; }}
    .header-style {{
        color: {BLUE}; font-weight: 700; font-size: 28px;
        text-align: center; margin-bottom: 22px;
    }}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-style">🚚 Warehouse Trips</div>', unsafe_allow_html=True)

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

NEXT_DAY = {
    'Saturday': 'Sunday', 'Sunday': 'Monday', 'Monday': 'Tuesday',
    'Tuesday': 'Wednesday', 'Wednesday': 'Thursday', 'Thursday': 'Friday', 'Friday': 'Saturday',
}
WAREHOUSE_COLOR = {'Jeddah': TEAL, 'Riyadh': ORANGE}

@st.cache_data
def load_trips():
    for fname in ['Warehouse Trips.xlsx', 'Warehouse Trips (1).xlsx']:
        candidate = os.path.join(os.path.dirname(__file__), '..', fname)
        if os.path.exists(candidate):
            path = candidate
            break
    else:
        st.error("Warehouse Trips file not found")
        return {}
    schedule_days = ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday']
    trips = {}
    for warehouse in ['Jeddah', 'Riyadh']:
        df = pd.read_excel(path, sheet_name=warehouse, header=None)
        for col_idx, day in enumerate(schedule_days):
            branch_col = col_idx * 2
            for row_idx in range(2, len(df)):
                branch = str(df.iloc[row_idx, branch_col]).strip()
                if branch and branch.lower() != 'nan':
                    if branch not in trips:
                        trips[branch] = []
                    trips[branch].append((warehouse, day, NEXT_DAY[day]))
    return trips

trips_data   = load_trips()
all_branches = sorted(trips_data.keys())

jeddah_branches = sum(1 for v in trips_data.values() if any(w == 'Jeddah' for w, _, _ in v))
riyadh_branches = sum(1 for v in trips_data.values() if any(w == 'Riyadh' for w, _, _ in v))

st.sidebar.markdown("---")
st.sidebar.metric("🚚 Total Branches", len(all_branches))
st.sidebar.metric("🏭 Jeddah WH",     jeddah_branches)
st.sidebar.metric("🏭 Riyadh WH",     riyadh_branches)
st.sidebar.markdown("---")

today_en = datetime.now().strftime('%A')

PLACEHOLDER = "— Select Branch —"
selected_branch = st.selectbox("🔍 Branch Code", options=[PLACEHOLDER] + all_branches, index=0, key="wh_branch")

if selected_branch and selected_branch != PLACEHOLDER:
    branch_trips = trips_data[selected_branch]
    warehouse    = branch_trips[0][0]
    wh_color     = WAREHOUSE_COLOR[warehouse]

    st.markdown(f"""
    <div style="background:#1a1a2e; border-left:5px solid {wh_color};
                padding:16px 22px; border-radius:12px; margin:16px 0;">
        <div style="color:{wh_color}; font-size:13px; font-weight:600; margin-bottom:4px;">Warehouse</div>
        <div style="color:white; font-size:22px; font-weight:700;">🏭 {warehouse}</div>
        <div style="color:#888; font-size:13px; margin-top:4px;">
            Branch: <span style="color:{ORANGE}; font-weight:600;">{selected_branch}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"<p style='color:#666; font-size:13px; margin-top:20px;'>📅 Full weekly schedule for {selected_branch}:</p>",
                unsafe_allow_html=True)

    cols = st.columns(len(branch_trips))
    for i, (w, dep, arr) in enumerate(branch_trips):
        is_today     = (dep == today_en)
        border_color = GREEN if is_today else TEAL
        badge        = "⚡ Today" if is_today else "&nbsp;"
        with cols[i]:
            st.markdown(f"""
            <div style="background:#1a1a2e; border:2px solid {border_color};
                        border-radius:12px; padding:16px; text-align:center;">
                <div style="color:{border_color}; font-size:11px; font-weight:600; min-height:16px;">{badge}</div>
                <div style="color:#aaa; font-size:11px; margin-top:4px;">Departs</div>
                <div style="color:white; font-size:16px; font-weight:700;">{dep}</div>
                <div style="color:#555; font-size:20px; margin:6px 0;">↓</div>
                <div style="color:#aaa; font-size:11px;">Arrives</div>
                <div style="color:{GREEN}; font-size:16px; font-weight:700;">{arr}</div>
            </div>
            """, unsafe_allow_html=True)

else:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div style="background:#1a1a2e; border:1px solid #2a2a3a;
                    padding:20px; border-radius:12px; text-align:center;">
            <div style="color:{TEAL}; font-size:32px; font-weight:700;">{len(all_branches)}</div>
            <div style="color:#aaa; font-size:14px; margin-top:6px;">Total Branches</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div style="background:#1a1a2e; border:1px solid #2a2a3a;
                    padding:20px; border-radius:12px; text-align:center;">
            <div style="color:{TEAL}; font-size:32px; font-weight:700;">{jeddah_branches}</div>
            <div style="color:#aaa; font-size:14px; margin-top:6px;">🏭 Jeddah Warehouse</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div style="background:#1a1a2e; border:1px solid #2a2a3a;
                    padding:20px; border-radius:12px; text-align:center;">
            <div style="color:{ORANGE}; font-size:32px; font-weight:700;">{riyadh_branches}</div>
            <div style="color:#aaa; font-size:14px; margin-top:6px;">🏭 Riyadh Warehouse</div>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:#1a1a2e; border:1px solid #2a2a3a;
                padding:30px; border-radius:12px; text-align:center; margin-top:20px;">
        <div style="font-size:36px;">🚚</div>
        <div style="color:#aaa; font-size:16px; margin-top:10px;">
            Select a branch to see its warehouse and delivery schedule
        </div>
    </div>
    """, unsafe_allow_html=True)