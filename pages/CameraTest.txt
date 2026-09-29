import json
import os

import gspread
from google.oauth2.service_account import Credentials
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st


BASE_DIR = os.path.dirname(__file__)
st.set_page_config(page_title="Metal Muscle Scouting", layout="centered")
MetalMuscleLogo = os.path.join(BASE_DIR, "More Files", "1506-logo.jpg")

st.image(MetalMuscleLogo)

#st.camera_input("Take a photo!")