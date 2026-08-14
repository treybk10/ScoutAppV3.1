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

st.page_link("pages/CurrentRankings.py", label="Current Rankings")
st.page_link("pages/StandScouting.py", label="Stand Scouting")
st.page_link("pages/Statbotics.py", label="Statbotics")

secrets_info = st.secrets["connections"]["gsheets"]
creds_dict = {
    "type": secrets_info["type"],
    "project_id": secrets_info["project_id"],
    "private_key_id": secrets_info["private_key_id"],
    "private_key": secrets_info["private_key"],
    "client_email": secrets_info["client_email"],
    "client_id": secrets_info["client_id"],
    "auth_uri": secrets_info["auth_uri"],
    "token_uri": secrets_info["token_uri"],
    "auth_provider_x509_cert_url": secrets_info["auth_provider_x509_cert_url"],
    "client_x509_cert_url": secrets_info["client_x509_cert_url"]
}

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']


creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
client = gspread.authorize(creds)

sh = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])

worksheet = sh.get_worksheet(0)

row = ["Test", 1, True]
if st.button("Upload"):
    worksheet.append_row(row)