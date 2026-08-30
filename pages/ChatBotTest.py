import json

import cv2
import base64
import os
from openai import OpenAI
import streamlit as st
import requests

# --- Configuration ---
#API KEY GOES HERE
HACK_CLUB_API_KEY = st.secrets["AI_API"]
HACK_CLUB_BASE_URL = "https://ai.hackclub.com/proxy/v1" 

MODEL_NAME = "openrouter/free" 

if "allInput" not in st.session_state:
    st.session_state.allInput = []

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key= st.secrets["AI_API"],
    timeout=5000 # Wait up to 5 minutes for a response
)

st.session_state.setup = True

currentRespone = "user"
BASE_DIR = os.path.dirname(__file__)

MANUAL_PATH = os.path.join(BASE_DIR, "More Files", "2026GameRebuilt.txt")
ALLIANCE_SELECTION_PATH = os.path.join(BASE_DIR, "More Files", "AllianceSelection.txt")
MetalMuscleLogo = os.path.join(BASE_DIR, "More Files", "1506-logo.jpg")

st.set_page_config(page_title="Metal Muscle Scouting", layout="centered")
st.image(MetalMuscleLogo)

selectedAlliance = st.title("FRC Scouting Master")

user_input = st.chat_input(placeholder="Message Here")

if user_input is not None:
    content_list = [{"type": "text", "text": f"You are a FRC scouting app. Your job is to provide the most reasonable scouting response to this prompt from the user: {user_input}. The Previous Conversation is here: {st.session_state.allInput}. Please give the best response you can."}]


    with st.spinner(f"Asking AI: {user_input}"):
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": content_list
                }
            ]
        )

    st.session_state.allInput.append(user_input)
    st.session_state.allInput.append(response.choices[0].message.content)

    with st.expander("Full Conversation"):
        for data in st.session_state.allInput:
            with st.chat_message(currentRespone):
                if (currentRespone == "user"):
                    currentRespone = "ai"
                else:
                    currentRespone = "user"
                st.write(data)
    
    with st.chat_message(currentRespone):
        if (currentRespone == "user"):
            currentRespone = "ai"
        else:
            currentRespone = "user"
        st.write(user_input)
    with st.chat_message(currentRespone):
        if (currentRespone == "user"):
            currentRespone = "ai"
        else:
            currentRespone = "user"
        st.write(response.choices[0].message.content)
#st.write(st.session_state.allInput)