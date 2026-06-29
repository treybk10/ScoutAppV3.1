from openrouter import OpenRouter
import streamlit as st


st.set_page_config(page_title="My Streamlit App", layout="centered")
st.title("FRC Scouting App")
st.write("Welcome to your first Streamlit application! Adjust the filters to see the chart update instantly.")

num_rows = st.sidebar.slider("Select number of data points:", min_value=10, max_value=200, value=50)
client = OpenRouter(
    api_key = st.secrets["API_KEY"],
    server_url="https://ai.hackclub.com/proxy/v1",
)
if st.button("Load matches"):
    st.text("Works!")

    response = client.chat.send(
        model="google/gemini-3.1-pro-preview",
        messages=[
            {"role": "user", "content": """Please give me pthon code to be able to import a youtube link and export a .mp4 file of that youtube video. Please use streamlit also. Don't use yt_dlp"""}
        ],
        stream=False,
    )

    print(response.choices[0].message.content)
    st.text(response.choices[0].message.content)