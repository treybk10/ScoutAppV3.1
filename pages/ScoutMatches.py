import cv2
import base64
import os
from openai import OpenAI
import requests
import streamlit as st
import random

import tempfile

TBA_API_KEY = st.secrets["TBA_KEY"]
TBA_URL = "https://thebluealliance.com"
HEADERS = {
    "X-TBA-Auth-Key": TBA_API_KEY,
    "accept": "application/json"
}

VIDEO_PATH = ""

BASE_DIR = os.path.dirname(__file__)

MetalMuscleLogo = os.path.join(BASE_DIR, "More Files", "1506-logo.jpg")



st.image(MetalMuscleLogo)

st.set_page_config(page_title="Match Scouter", layout="centered")
selectedAlliance = st.title("FRC Scouting Master")
st.subheader("Scout Matches!")

st.badge("Please Know That This Page Does Not Work Yet!", color="red", icon="🚨")


endpoint = f"{TBA_URL}/events/2026"
response = requests.get(endpoint, headers=HEADERS)
st.text(response)