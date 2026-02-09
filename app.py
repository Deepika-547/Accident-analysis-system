import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(layout="wide", page_title="Traffic Analysis System")

# 2. FIXED: Corrected CSS Error (unsafe_allow_html)
st.markdown("""
    <style>
    .stButton>button { border-radius: 8px; height: 3.5em; font-weight: bold; font-size: 16px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar Navigation
with st.sidebar:
    st.title("🚦 Traffic Analysis")
    st.markdown("---")
    
    if 'active_page' not in st.session_state:
        st.session_state.active_page = "Overall Accident Analysis"

    topics = {
        "Overall Accident Analysis": "📊",
        "Drunk Driver Analysis": "🍺",
        "Weather Based Analysis": "🌦️",
        "Roads Based Analysis": "🛣️",
        "Weekly Hours Analysis": "📅",
        "Accident Peak Hours": "⏰"
    }

    st.write("### Analysis Topics")
    for t, icon in topics.items():
        if st.button(
            f"{icon} {t}", 
            use_container_width=True, 
            type="primary" if st.session_state.active_page == t else "secondary"
        ):
            st.session_state.active_page = t
            st.rerun()

# 4. Data Loading & Cleaning (Fixes the "Faded" & "None" errors)
@st.cache_data
def load_data():
    df = pd.read_csv("traffic_accidents.csv")
    df['Time'] = pd.to_datetime(df['Time'])
    df['Hour'] = df['Time'].dt.hour
    
    # Fill missing values so the Sunburst chart isn't empty/faded
    cols = ['Road_surface_type', 'Light_conditions', 'Weather_conditions', 'Fitness_of_casuality']
    for col in cols:
        df[col] = df[col].fillna('Not Specified').replace('', 'Not Specified')
    
    return df

topic = st.session_state.active_page

try:
    df = load_data()

    # 5. Main Screen Logic
    st.title(f"{topics[topic]} {topic}")

    if topic == "Overall Accident Analysis":
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Records", f"{len(df):,}")
        m2.metric("Top Weather", df['Weather_conditions'].mode()[0])
        m3.metric("Peak Hour", f"{df['Hour'].mode()[0]}:00")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("⚠️ Severity Breakdown")
            # Using high-contrast colors
            fig_pie = px.pie(df, names='Accident_severity', hole=0.4, 
                             color_discrete_sequence=px.colors.qualitative.Set1)
            fig_pie.update_traces(textinfo='percent+label', pull=[0.1, 0, 0])
            st.plotly_chart(fig_pie, use_container_width=True)
        with col2:
            st.subheader("📅 Weekly Frequency")
            fig_day = px.bar(df['Day_of_week'].value_counts(), color_discrete_sequence=['#E41A1C'])
            st.plotly_chart(fig_day, use_container_width=True)

    elif topic == "Drunk Driver Analysis":
        st.subheader("Driver Fitness Analysis")
        # Log Scale makes small categories visible
        fig = px.histogram(df, x='Fitness_of_casuality', color='Accident_severity', 
                           barmode='group', log_y=True,
                           color_discrete_sequence=px.colors.qualitative.Bold)
        st.plotly_chart(fig, use_container_width=True)

    elif topic == "Weather Based Analysis":
        st.subheader("Accidents by Weather")
        # Horizontal bars prevent names from overlapping
        fig = px.histogram(df, y='Weather_conditions', color='Accident_severity', 
                           orientation='h', log_x=True,
                           color_discrete_sequence=px.colors.qualitative.Vivid)
        st.plotly_chart(fig, use_container_width=True)

    elif topic == "Roads Based Analysis":
        st.subheader("Road & Light Condition Distribution")
        # FIXED: Bold color scale so it doesn't look faded
        fig = px.sunburst(df, path=['Road_surface_type', 'Light_conditions'], 
                          color='Road_surface_type', 
                          color_discrete_sequence=px.colors.qualitative.Dark24)
        fig.update_traces(textinfo='label+percent entry')
        st.plotly_chart(fig, use_container_width=True)

    elif topic == "Weekly Hours Analysis":
        st.subheader("Accident Intensity Heatmap")
        fig = px.density_heatmap(df, x="Hour", y="Day_of_week", text_auto=True, 
                                 color_continuous_scale='YlOrRd')
        st.plotly_chart(fig, use_container_width=True)

    elif topic == "Accident Peak Hours":
        st.subheader("Hourly Accident Trends")
        hour_counts = df['Hour'].value_counts().sort_index().reset_index()
        hour_counts.columns = ['Hour', 'Accidents']
        fig = px.area(hour_counts, x='Hour', y='Accidents', markers=True, 
                      color_discrete_sequence=['#377EB8'])
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Something went wrong: {e}")