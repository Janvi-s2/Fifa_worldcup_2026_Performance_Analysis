
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="FIFA World Cup Analytics",
    page_icon="⚽",
    layout="wide"
)

# ---------- CUSTOM CSS ----------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f8fafc, #e0f2fe);
    color: #1e293b;
}
[data-testid="stSidebar"] {
    background-color: #f1f5f9;
}
h1, h2, h3 {
    color: #1d4ed8;
}
[data-testid="stMetric"] {
    background-color: white;
    border: 1px solid #cbd5e1;
    padding: 18px;
    border-radius: 15px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)


# ---------- HEADER ----------
st.title("⚽ FIFA World Cup Analytics")
st.markdown(
    "### Player Performance | Team Analysis | World Cup Statistics"
)
st.divider()

# ---------- AUTOMATIC DATASET LOADING ----------
BASE_DIR = Path(__file__).resolve().parent

CSV_PATH = (
    BASE_DIR /
    "fifa_world_cup_2026_player_performance_dirty.csv"
)

@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path)

if not CSV_PATH.exists():
    st.error(
        "Dataset file not found. Please check that "
        "fifa_world_cup_2026_player_performance_dirty.csv "
        "is uploaded in the same GitHub folder as app.py."
    )
    st.stop()

try:
    df = load_data(str(CSV_PATH))
except Exception as e:
    st.error(f"Dataset could not be loaded: {e}")
    st.stop()

df.columns = df.columns.str.strip()

# ---------- COLUMN CHECK ----------
required = [
    "team",
    "position",
    "tournament_stage",
    "nationality",
    "goals"
]

missing = [col for col in required if col not in df.columns]

if missing:
    st.error(
        "Required columns not found: " + ", ".join(missing)
    )
    st.write("Available columns:", df.columns.tolist())
    st.stop()

df["goals"] = pd.to_numeric(df["goals"], errors="coerce")
df = df.dropna(subset=["goals", "nationality"])

if df.empty:
    st.warning("No valid player records found.")
    st.stop()

# ---------- SIDEBAR FILTERS ----------
st.sidebar.title("🎛️ Dashboard Filters")

team_list = sorted(df["team"].dropna().unique().tolist())
position_list = sorted(df["position"].dropna().unique().tolist())
stage_list = sorted(
    df["tournament_stage"].dropna().unique().tolist()
)

team = st.sidebar.selectbox(
    "Select Team", ["All Teams"] + team_list
)

position = st.sidebar.selectbox(
    "Select Position", ["All Positions"] + position_list
)

stage = st.sidebar.selectbox(
    "Select Tournament Stage", ["All Stages"] + stage_list
)

# ---------- FILTER DATA ----------
dash = df.copy()

if team != "All Teams":
    dash = dash[dash["team"] == team]

if position != "All Positions":
    dash = dash[dash["position"] == position]

if stage != "All Stages":
    dash = dash[dash["tournament_stage"] == stage]

if dash.empty:
    st.warning("No records found. Change your filters.")
    st.stop()

# ---------- KPI CARDS ----------
st.subheader("📊 Performance Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Player Records", f"{len(dash):,}")
c2.metric("Teams", f"{dash['team'].nunique():,}")
c3.metric("Total Goals", f"{dash['goals'].sum():,.0f}")
c4.metric("Average Goals", f"{dash['goals'].mean():.2f}")

st.divider()

# ---------- NATIONALITY CHART ----------
st.subheader("🏆 Top 10 Nationalities by Average Goals")

ng = (
    dash.groupby("nationality")["goals"]
    .mean()
    .nlargest(10)
    .sort_values()
)

nationality_df = ng.rename("Average Goals").reset_index()

fig1 = px.bar(
    nationality_df,
    x="Average Goals",
    y="nationality",
    orientation="h",
    color="Average Goals",
    color_continuous_scale="Blues",
    template="plotly_dark",
    title="Average Goals by Nationality"
)

fig1.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    coloraxis_showscale=False
)

st.plotly_chart(fig1, use_container_width=True)

# ---------- TEAM GOALS ----------
left, right = st.columns(2)

with left:
    st.subheader("🥅 Team-wise Goals")

    team_goals = (
        dash.groupby("team", as_index=False)["goals"]
        .sum()
        .sort_values("goals", ascending=False)
        .head(10)
    )

    fig2 = px.bar(
        team_goals,
        x="team",
        y="goals",
        color="goals",
        template="plotly_dark",
        title="Top 10 Teams by Goals"
    )

    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_tickangle=-45,
        coloraxis_showscale=False
    )

    st.plotly_chart(fig2, use_container_width=True)

# ---------- POSITION DISTRIBUTION ----------
with right:
    st.subheader("👟 Position Distribution")

    position_data = (
        dash["position"]
        .value_counts()
        .rename_axis("Position")
        .reset_index(name="Player Records")
    )

    fig3 = px.pie(
        position_data,
        names="Position",
        values="Player Records",
        hole=0.5,
        template="plotly_dark",
        title="Players by Position"
    )

    fig3.update_layout(
        paper_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(fig3, use_container_width=True)

# ---------- DATA TABLE ----------
st.divider()
st.subheader("📋 Player Records")

st.dataframe(
    dash,
    use_container_width=True,
    hide_index=True
)

# ---------- DOWNLOAD ----------
st.download_button(
    "⬇️ Download Filtered Dataset",
    data=dash.to_csv(index=False).encode("utf-8"),
    file_name="fifa_filtered_data.csv",
    mime="text/csv"
)

st.markdown("---")
st.caption("FIFA World Cup Analytics | Built with Streamlit & Plotly")
