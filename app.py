# app.py - Streamlit UI for Vehicle Allocation Dashboard (core features)
import streamlit as st
import pandas as pd
import plotly.express as px
import io
import os
from utils import detect_header_and_read, auto_map_columns, parse_times, detect_conflicts, compute_utilization, generate_sample_excel

st.set_page_config(page_title='Vehicle Allocation Dashboard', layout='wide')

# simple theming palettes (CSS will be injected based on selection)
# beomes fully responsvive after being deployed, could be implemented or removed//
THEMES = {
    "Premium Green": {"accent": "#0b7a3d", "bg": "#f4fff6", "text": "#0b3e20"},
    "Beige Minimal": {"accent": "#c9b79c", "bg": "#fbf8f5", "text": "#5a4b3a"},
    "Minimal Grey": {"accent": "#8a8f94", "bg": "#f6f7f8", "text": "#2b2f31"},
    "Cobalt Blue": {"accent": "#0f4c81", "bg": "#f3f8ff", "text": "#05253f"}
}


def inject_css(theme):
    accent = theme["accent"]
    bg = theme["bg"]
    text = theme["text"]
    css = f"""
    <style>
    :root {{ --accent: {accent}; --bg: {bg}; --text: {text}; }}
    .stApp {{ background: linear-gradient(180deg, var(--bg), white); color: var(--text); }}
    .card {{ border-radius:12px; padding:12px; box-shadow: 0 6px 18px rgba(0,0,0,0.06); background: white; }}
    .header-accent {{ color: var(--accent); }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


st.title('🚛 Vehicle Allocation Dashboard')

# Sidebar: Theme + Upload + Sample
st.sidebar.header('Appearance')
theme_choice = st.sidebar.selectbox(
    'Choose theme', options=list(THEMES.keys()), index=0)
inject_css(THEMES[theme_choice])

st.sidebar.header('Data')
upload = st.sidebar.file_uploader(
    'Upload Excel (.xlsx/.xls)', type=['xlsx', 'xls'])

if st.sidebar.button('Download sample template'):
    buf = io.BytesIO()
    generate_sample_excel(buf)
    buf.seek(0)
    st.sidebar.download_button('Download sample_data.xlsx', data=buf, file_name='sample_data.xlsx',
                               mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# Read file or load sample
if upload is not None:
    try:
        df = detect_header_and_read(upload)
        st.sidebar.success('File loaded')
    except Exception as e:
        st.sidebar.error(f'Unable to read file: {e}')
        st.stop()
else:
    st.info('No file uploaded — using internal sample data.')
    sample_buf = io.BytesIO()
    generate_sample_excel(sample_buf)
    sample_buf.seek(0)
    df = detect_header_and_read(sample_buf)

st.sidebar.subheader('Column mapping (auto-detected)')
mapping = auto_map_columns(df)
col_map = {}
for logical in ['day', 'vehicle', 'start', 'end', 'purpose', 'route', 'passengers']:
    detected = mapping.get(logical, '')
    chosen = st.sidebar.selectbox(f'{logical} column', options=[
                                  ''] + list(df.columns), index=(list(df.columns).index(detected) + 1) if detected in df.columns else 0)
    col_map[logical] = chosen if chosen != '' else None

parsed = parse_times(df, col_map)

with st.expander('Preview parsed data (first 10 rows)'):
    st.dataframe(parsed.head(10))

vehicle_col = col_map.get('vehicle') or 'Vehicle ID'
if vehicle_col not in parsed.columns:
    candidates = [c for c in parsed.columns if 'vehicle' in c.lower()
                  or 'veh' in c.lower()]
    vehicle_col = candidates[0] if candidates else parsed.columns[0]

# metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric('Total Vehicles', int(parsed[vehicle_col].nunique()))
col2.metric('Total Allocations', int(len(parsed)))
col3.metric('Average Duration (hrs)', float(parsed['duration_hours'].mean()))
col4.metric('Total Operational Hours', float(parsed['duration_hours'].sum()))

# Conflict detection
conflicts_df = detect_conflicts(parsed, vehicle_col)
if not conflicts_df.empty:
    st.warning(f'{len(conflicts_df)} scheduling conflict(s) detected')
    with st.expander('Show conflicts'):
        st.dataframe(conflicts_df)
else:
    st.success('No scheduling conflicts detected')

# Filters
st.sidebar.header('Filters')
vehicle_filter = st.sidebar.multiselect('Vehicles', options=sorted(
    parsed[vehicle_col].unique()), default=sorted(parsed[vehicle_col].unique()))
day_col = col_map.get('day') or 'Day'
if day_col not in parsed.columns:
    day_opts = []
else:
    day_opts = sorted(parsed[day_col].dropna().unique())
day_filter = st.sidebar.multiselect('Days', options=day_opts, default=day_opts)

filtered = parsed[parsed[vehicle_col].isin(vehicle_filter)]
if day_opts:
    filtered = filtered[filtered[day_col].isin(day_filter)]

st.header('Gantt Timeline (weekly view)')
if filtered.empty:
    st.info('No data for selected filters')
else:
    fig = px.timeline(filtered, x_start='start_dt', x_end='end_dt', y=vehicle_col, color=vehicle_col, hover_data=[
                      'duration_hours', col_map.get('purpose') or 'Journey Purpose'])
    fig.update_yaxes(autorange='reversed')
    st.plotly_chart(fig, use_container_width=True)

st.header('Vehicle Utilization')
util = compute_utilization(parsed, vehicle_col)
fig2 = px.bar(util, x=vehicle_col, y='total_hours',
              labels={'total_hours': 'Total Hours'})
st.plotly_chart(fig2, use_container_width=True)

st.header('Daily Allocation Overview')
if day_col in parsed.columns:
    daily_counts = filtered.groupby(day_col).size().reindex(
        day_opts).fillna(0).reset_index(name='count')
    fig3 = px.bar(daily_counts, x=day_col, y='count')
    st.plotly_chart(fig3, use_container_width=True)

st.write('---')
st.caption('Tips: Upload files with clear column names for best mapping. If times lack dates, the app attaches a reference week to produce a weekly Gantt.')
