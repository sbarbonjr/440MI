import streamlit as st
import pandas as pd

st.title("Patient Data Explorer")

data = pd.DataFrame({
    "Patient": ["Anna", "Marco", "Elena", "Luca"],
    "Age": [42, 71, 55, 68],
    "Temperature": [36.8, 38.4, 37.2, 39.0],
    "Heart rate": [72, 104, 80, 110]
})

st.subheader("Dataset")
st.dataframe(data, use_container_width=True)

minimum_age = st.slider(
    "Show patients aged at least",
    18,
    100,
    50
)

filtered = data[
    data["Age"] >= minimum_age
]

st.subheader("Filtered data")
st.dataframe(filtered, use_container_width=True)

variable = st.selectbox(
    "Variable to plot",
    ["Temperature", "Heart rate", "Age"]
)

chart_data = filtered.set_index("Patient")[[variable]]

st.bar_chart(chart_data)
