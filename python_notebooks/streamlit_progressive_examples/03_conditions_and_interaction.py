import streamlit as st

st.title("Simple Interactive App")

temperature = st.slider(
    "Body temperature (°C)",
    min_value=35.0,
    max_value=41.0,
    value=36.8,
    step=0.1
)

if temperature >= 38.0:
    st.error("Fever")
elif temperature >= 37.5:
    st.warning("Slightly elevated temperature")
else:
    st.success("Temperature in the normal range")

st.write("Selected temperature:", temperature)
