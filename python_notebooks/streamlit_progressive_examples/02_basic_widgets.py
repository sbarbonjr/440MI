import streamlit as st

st.title("Basic Streamlit Widgets")

name = st.text_input("What is your name?")

age = st.slider(
    "Select your age",
    min_value=0,
    max_value=100,
    value=25
)

student = st.checkbox("I am a student")

st.write("Name:", name)
st.write("Age:", age)
st.write("Student:", student)
