import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(layout="wide")

# -----------------------------
# SESSION STATE INIT
# -----------------------------
if "analyzed" not in st.session_state:
    st.session_state.analyzed = False

if "saved" not in st.session_state:
    st.session_state.saved = False

# -----------------------------
# CUSTOM CSS
# -----------------------------
st.markdown("""
<style>
.main {
    background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
    color: white;
}
.card {
    background-color: rgba(255,255,255,0.08);
    padding: 20px;
    border-radius: 15px;
    backdrop-filter: blur(10px);
}
.big-font {
    font-size: 28px !important;
    font-weight: bold;
}
.center {
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# DATABASE CONNECTION
# -----------------------------
DB_URL = st.secrets["DB_URL"]

engine = create_engine(
    DB_URL,
    pool_pre_ping=True
)

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    return pd.read_sql("SELECT * FROM health_data", engine)

with st.spinner("Analyzing your data..."):
    df = load_data()

# -----------------------------
# HEADER
# -----------------------------
st.markdown("<h1 class='center'>Health Intelligence System</h1>", unsafe_allow_html=True)
st.markdown("<p class='center'>Real-time comparison with population data</p>", unsafe_allow_html=True)

st.divider()

# -----------------------------
# LAYOUT
# -----------------------------
col1, col2 = st.columns([1, 2])

# -----------------------------
# INPUT PANEL
# -----------------------------
with col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Enter Your Data")

    gender = st.selectbox("Gender", ["Male", "Female"])
    height_in = st.slider("Height (inches)", 50, 90, 65)
    weight_kg = st.slider("Weight (kg)", 30, 150, 70)

    if st.button("Analyze 🚀"):
        st.session_state.analyzed = True
        st.session_state.saved = False  # reset save flag

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# FUNCTIONS
# -----------------------------
def bmi_calc(w, h):
    h_m = h * 0.0254
    return w / (h_m**2)

def category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"

def save_user(data):
    df_new = pd.DataFrame([data])
    df_new.to_sql("health_data", engine, if_exists="append", index=False)

# -----------------------------
# RESULTS
# -----------------------------
if st.session_state.analyzed:

    # Reload latest data BEFORE comparison
    df = load_data()

    # Calculate user values
    user_bmi = bmi_calc(weight_kg, height_in)
    cat = category(user_bmi)

    percentile = (df["bmi"] < user_bmi).mean() * 100
    avg = df["bmi"].mean()

    # -----------------------------
    # SAVE USER (ONLY ONCE)
    # -----------------------------
    if not st.session_state.saved:
        data = {
            "gender": gender,
            "height_in": height_in,
            "weight_kg": weight_kg,
            "bmi": user_bmi,
            "bmi_category": cat,
            "source": "user"
        }

        # Debug check (optional)
        # st.write("DEBUG:", data)

        save_user(data)
        st.session_state.saved = True

        # Refresh cache so new data appears
        st.cache_data.clear()
        df = load_data()

    # -----------------------------
    # RESULT CARDS
    # -----------------------------
    with col2:
        c1, c2, c3 = st.columns(3)

        c1.markdown(f"<div class='card center'><p>BMI</p><p class='big-font'>{user_bmi:.2f}</p></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card center'><p>Category</p><p class='big-font'>{cat}</p></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card center'><p>Percentile</p><p class='big-font'>{percentile:.1f}%</p></div>", unsafe_allow_html=True)

        # Insight banner
        if percentile > 75:
            st.error("⚠️ High BMI compared to population")
        elif percentile < 25:
            st.success("✅ You are in a healthier range than most users")
        else:
            st.info("ℹ️ You are around the average range")

    # -----------------------------
    # DISTRIBUTION
    # -----------------------------
    st.divider()
    st.subheader("Population Distribution")

    fig = px.histogram(df, x="bmi", nbins=25)

    fig.add_vline(
        x=user_bmi,
        line_dash="dash",
        annotation_text="YOU",
        annotation_position="top"
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# ANALYTICS TABS
# -----------------------------
st.divider()

tab1, tab2, tab3 = st.tabs(["Overview", "Gender Analysis", "Categories"])

with tab1:
    st.subheader("Overview")
    colA, colB = st.columns(2)
    colA.metric("Average BMI", round(df["bmi"].mean(), 2))
    colB.metric("Total Users", len(df))

with tab2:
    st.subheader("Gender Comparison")
    fig2 = px.box(df, x="gender", y="bmi")
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.subheader("BMI Categories")
    fig3 = px.pie(df, names="bmi_category")
    st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# INSIGHTS ENGINE
# -----------------------------
st.divider()
st.subheader("Insights Engine")

if st.session_state.analyzed:
    insights = []

    if user_bmi > df["bmi"].mean():
        insights.append("Your BMI is above the population average")

    if percentile > 80:
        insights.append("You fall into the top 20% BMI group")

    if cat == "Obese":
        insights.append("Your category indicates potential health risks")

    for i in insights:
        st.write("•", i)
