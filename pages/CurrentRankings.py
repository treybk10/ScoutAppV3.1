import json


import base64
import os

import streamlit as st
import requests

TBA_API_KEY = st.secrets["TBA_KEY"]

headers = {
    "X-TBA-Auth-Key": TBA_API_KEY
}


BASE_DIR = os.path.dirname(__file__)

MANUAL_PATH = os.path.join(BASE_DIR, "More Files", "2026GameRebuilt.txt")
ALLIANCE_SELECTION_PATH = os.path.join(BASE_DIR, "More Files", "AllianceSelection.txt")
MetalMuscleLogo = os.path.join(BASE_DIR, "More Files", "1506-logo.jpg")

st.set_page_config(page_title="Metal Muscle Scouting", layout="centered")
st.image(MetalMuscleLogo)

st.page_link("pages/StandScouting.py", label="Stand Scouting")
st.page_link("pages/CurrentRankings.py", label="Current Rankings")
st.page_link("pages/Statbotics.py", label="Statbotics")

selectedAlliance = st.title("FRC Scouting Master")
st.subheader("Event Rankings")
st.badge("Please Note That This App Is Under Construction!", color="red")

comp = st.text_input("Event Key: ", value="2026misal")
tba_url = f"https://www.thebluealliance.com/api/v3/event/{comp}/rankings"

response = requests.get(tba_url, headers=headers)


if st.button("Load Rankings"):
    try:
        
        if response.status_code == 200:
            data = response.json()
            rankings = data.get("rankings", [])

            if isinstance(rankings, list):
                st.write("rank, team, wins, losses, ties, played, dq")
                for team in rankings:
                    team_info = {
                        "rank": team.get("rank"),
                        "team_number": team.get("team_key").replace("frc", ""),
                        "wins": team.get("record", {}).get("wins"),
                        "losses": team.get("record", {}).get("losses"),
                        "ties": team.get("record", {}).get("ties"),
                        "played": team.get("matches_played"),
                        "dq": team.get("dq"),
                    }
                    rank = team.get("rank")
                    team_number = team.get("team_key").replace("frc", "")
                    wins = team.get("record", {}).get("wins")
                    losses = team.get("record", {}).get("losses")
                    ties = team.get("record", {}).get("ties")
                    played = team.get("matches_played")
                    dq = team.get("dq")
                    st.write(rank, team_number, wins, losses, ties, played, dq)


            else:
                error_payload = {
                    "error": "Unexpected data format from TBA",
                    "raw_response": rankings
                }
                print(json.dumps(error_payload))
                st.write(json.dumps(error_payload))
                st.error("Something didn't work")

        
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        st.text(f"\nAn error has occurred. {e}")