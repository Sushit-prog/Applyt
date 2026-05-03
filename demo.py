import streamlit as st
from PIL import Image

logo = Image.open("Applytlogo-removebg-preview.png")
st.sidebar.image(logo, width=140)  # ✅ fixed

st.sidebar.markdown("Hello World App")

st.title("Hello World")
st.write("Welcome to my first RAG application")