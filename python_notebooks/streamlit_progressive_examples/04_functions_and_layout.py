import streamlit as st

st.title("Patient Check")

def has_fever(temperature, threshold=38.0):
    return temperature >= threshold

def bmi(weight_kg, height_m):
    return weight_kg / height_m**2

col1, col2 = st.columns(2)

with col1:
    temperature = st.slider(
        "Temperature (°C)",
        35.0,
        41.0,
        36.8,
        0.1
    )

    weight = st.number_input(
        "Weight (kg)",
        min_value=30.0,
        max_value=200.0,
        value=70.0
    )

with col2:
    height = st.number_input(
        "Height (m)",
        min_value=1.2,
        max_value=2.2,
        value=1.75
    )

    smoker = st.checkbox("Smoker")

patient_bmi = bmi(weight, height)

st.metric("BMI", f"{patient_bmi:.1f}")

if has_fever(temperature):
    st.error("The patient has fever")
else:
    st.success("No fever")

st.write("Smoker:", smoker)
