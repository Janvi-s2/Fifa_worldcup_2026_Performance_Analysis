
import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="FIFA World Cup Analytics",
    page_icon="⚽",
    layout="wide"
)

# ---------------- CUSTOM DESIGN ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0b1120, #172554);
    color: #f8fafc;
}
[data-testid="stSidebar"] {
    background-color: #111827;
}
h1, h2, h3 {
    color: #60a5fa;
}
[data-testid="stMetric"] {
    background: #1e293b;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #334155;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.title("⚽ FIFA World Cup Analytics")
st.markdown(
    "### Explore teams, player performance and tournament statistics"
)
st.divider()

# ---------------- DATASET UPLOAD ----------------
st.sidebar.header("📂 Dataset")

uploaded_file = st.sidebar.file_uploader(
    "Upload FIFA World Cup CSV",
    type=["csv"]
)

if uploaded_file is None:
    st.info("👈 Upload your FIFA World Cup CSV file using the sidebar.")
    st.stop()

try:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
except Exception as e:
    st.error(f"Unable to read the CSV file: {e}")
    st.stop()

# ---------------- CHECK COLUMNS ----------------
required_columns = [
    "team",
    "position",
    "tournament_stage",
    "nationality",
    "goals"
]

missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    st.error(
        "Some required columns are missing: "
        + ", ".join(missing_columns)
    )
    st.write("Available columns:", df.columns.tolist())
    st.caption(
        "This version requires a player dataset containing "
        "team, position, tournament_stage, nationality and goals."
    )
    st.stop()

df["goals"] = pd.to_numeric(df["goals"], errors="coerce")
df = df.dropna(subset=["goals", "nationality"])

if df.empty:
    st.warning("No valid player records found in the dataset.")
    st.stop()

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("🎛️ Filters")

team_options = sorted(df["team"].dropna().unique().tolist())
position_options = sorted(df["position"].dropna().unique().tolist())
stage_options = sorted(
    df["tournament_stage"].dropna().unique().tolist()
)

selected_team = st.sidebar.selectbox(
    "Select Team",
    ["All Teams"] + team_options
)

selected_position = st.sidebar.selectbox(
    "Select Position",
    ["All Positions"] + position_options
)

selected_stage = st.sidebar.selectbox(
    "Select Tournament Stage",
    ["All Stages"] + stage_options
)

# ---------------- FILTER DATA ----------------
dash = df.copy()

if selected_team != "All Teams":
    dash = dash[dash["team"] == selected_team]

if selected_position != "All Positions":
    dash = dash[dash["position"] == selected_position]

if selected_stage != "All Stages":
    dash = dash[dash["tournament_stage"] == selected_stage]

if dash.empty:
    st.warning("No records found. Change the filters and try again.")
    st.stop()

# ---------------- KPI CARDS ----------------
st.subheader("📊 Tournament Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Player Records", f"{len(dash):,}")
c2.metric("Teams", f"{dash['team'].nunique():,}")
c3.metric("Total Goals", f"{dash['goals'].sum():,.0f}")
c4.metric("Average Goals", f"{dash['goals'].mean():.2f}")

st.divider()

# ---------------- TOP 10 NATIONALITIES ----------------
st.subheader("🏆 Top 10 Nationalities by Average Goals")

ng = (
    dash.groupby("nationality")["goals"]
    .mean()
    .nlargest(10)
    .sort_values()
)

if not ng.empty:
    nationality_df = ng.rename("Average Goals").reset_index()

    fig1 = px.bar(
        nationality_df,
        x="Average Goals",
        y="nationality",
        orientation="h",
        color="Average Goals",
        color_continuous_scale="Blues",
        template="plotly_dark",
        title="Nationality-wise Goal Analysis",
        labels={"nationality": "Nationality"}
    )

    fig1.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False
    )

    st.plotly_chart(fig1, use_container_width=True)

# ---------------- TEAM GOALS ----------------
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
        color_continuous_scale="Teal",
        template="plotly_dark",
        title="Top 10 Teams by Total Goals"
    )

    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        xaxis_tickangle=-45
    )

    st.plotly_chart(fig2, use_container_width=True)

# ---------------- POSITION DISTRIBUTION ----------------
with right:
    st.subheader("👟 Player Position Distribution")

    position_df = (
        dash["position"]
        .value_counts()
        .rename_axis("Position")
        .reset_index(name="Player Records")
    )

    fig3 = px.pie(
        position_df,
        names="Position",
        values="Player Records",
        hole=0.5,
        template="plotly_dark",
        title="Records by Position"
    )

    fig3.update_layout(
        paper_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(fig3, use_container_width=True)

# ---------------- DATA TABLE ----------------
st.divider()
st.subheader("📋 FIFA World Cup Player Data")

st.dataframe(
    dash,
    use_container_width=True,
    hide_index=True
)

# ---------------- DOWNLOAD BUTTON ----------------
st.download_button(
    label="⬇️ Download Filtered Data CSV",
    data=dash.to_csv(index=False).encode("utf-8"),
    file_name="fifa_filtered_data.csv",
    mime="text/csv"
)

st.markdown("---")
st.caption("FIFA World Cup Analytics | Python • Pandas • Streamlit • Plotly")
