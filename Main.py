from openrouter import OpenRouter
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="My Streamlit App", layout="centered")
st.title("FRC Scouting App")
st.write("Welcome to your first Streamlit application! Adjust the filters to see the chart update instantly.")

num_rows = st.sidebar.slider("Select number of data points:", min_value=10, max_value=200, value=50)

if st.button("Load matches"):
    st.text("Works!")


client = OpenRouter(
    api_key="Key Here",
    server_url="https://ai.hackclub.com/proxy/v1",
)

response = client.chat.send(
    model="google/gemini-3.1-pro-preview",
    messages=[
        {"role": "user", "content": "Tell me a robotics joke"}
    ],
    stream=False,
)

print(response.choices[0].message.content)