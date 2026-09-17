import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Patient Risk Explorer",
    layout="wide"
)

def calculate_risk_score(
    age,
    temperature,
    heart_rate,
    smoker,
    diabetes
):
    score = 0

    if age >= 65:
        score += 2

    if temperature >= 38:
        score += 2

    if heart_rate >= 100:
        score += 1

    if smoker:
        score += 1

    if diabetes:
        score += 1

    return score

def classify_risk(score):
    if score <= 1:
        return "Low"
    elif score <= 3:
        return "Medium"
    else:
        return "High"

st.title("Patient Risk Explorer")

st.info(
    "Educational demo only. "
    "The score is fictional and is not a clinical model."
)

with st.sidebar:
    st.header("Patient input")

    age = st.slider("Age", 18, 100, 50)

    temperature = st.slider(
        "Temperature (°C)",
        35.0,
        41.0,
        36.8,
        0.1
    )

    heart_rate = st.slider(
        "Heart rate (bpm)",
        40,
        180,
        75
    )

    smoker = st.checkbox("Smoker")
    diabetes = st.checkbox("Diabetes")

score = calculate_risk_score(
    age,
    temperature,
    heart_rate,
    smoker,
    diabetes
)

risk_level = classify_risk(score)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Age", age)

with col2:
    st.metric("Temperature", f"{temperature:.1f} °C")

with col3:
    st.metric("Heart rate", f"{heart_rate} bpm")

st.subheader("Result")
st.metric("Toy risk score", score)

if risk_level == "Low":
    st.success("Low toy risk category")
elif risk_level == "Medium":
    st.warning("Medium toy risk category")
else:
    st.error("High toy risk category")

st.divider()

st.subheader("Example patient dataset")

patients = pd.DataFrame({
    "Patient": ["Anna", "Marco", "Elena", "Luca"],
    "Age": [42, 71, 55, 68],
    "Temperature": [36.8, 38.4, 37.2, 39.0],
    "Heart rate": [72, 104, 80, 110]
})

st.dataframe(
    patients,
    use_container_width=True
)

variable = st.selectbox(
    "Variable to plot",
    ["Temperature", "Heart rate", "Age"]
)

chart_data = patients.set_index("Patient")[[variable]]

st.bar_chart(chart_data)
