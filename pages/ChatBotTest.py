import json

import cv2
import base64
import os
from openai import OpenAI
import streamlit as st
import re
import requests

# --- Configuration ---
#API KEY GOES HERE
HACK_CLUB_API_KEY = st.secrets["AI_API"]
HACK_CLUB_BASE_URL = "https://ai.hackclub.com/proxy/v1" 

MODEL_NAME = "openrouter/free" 
TTS_MODEL_NAME = "fish-audio/s2.1-pro-free:free"

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




def readable_ai_conversion(text: str) -> str:
    """Cleans up raw AI markdown text so it reads naturally for TTS."""
    # 1. Remove bold, italic, and strikethrough characters (**, *, __, _, ~~)
    text = re.sub(r"\*+", "", text)
    text = re.sub(r"_+", "", text)
    text = re.sub(r"~+", "", text)

    # 2. Replace bullet points (*, -, +, •) with a comma/pause, or just clean up the prefix
    # This matches bullets at the start of any line
    text = re.sub(r"^\s*[\*\-\+•]\s*", " ", text, flags=re.MULTILINE)

    # 3. Clean up multiple or consecutive newlines into single spaces so the AI doesn't pause awkwardly
    text = re.sub(r"\n+", " ", text)

    # 4. Clean up any accidental double spaces
    text = re.sub(r" +", " ", text)

    return text.strip()



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

        ai_readable = readable_ai_conversion(response.choices[0].message.content)
        
        tts_response = client.audio.speech.create(
            model=TTS_MODEL_NAME,
            voice="601e4808613a487f88416690ea564b8c",
            input=response.choices[0].message.content,
            response_format="mp3"
        )
    st.audio(tts_response.content, format="audio/mp3", autoplay=True)

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