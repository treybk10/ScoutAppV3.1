import json

import cv2
import base64
import os
from openai import OpenAI
import streamlit as st
import requests

# --- Configuration ---
#API KEY GOES HERE
HACK_CLUB_API_KEY = st.secrets["API_KEY"]
HACK_CLUB_BASE_URL = "https://ai.hackclub.com/proxy/v1" 

TBA_API_KEY = st.secrets["TBA_KEY"]

headers = {
    "X-TBA-Auth-Key": TBA_API_KEY
}



# pro doesn't work?
MODEL_NAME = "google/gemini-2.5-flash" 

BASE_DIR = os.path.dirname(__file__)

MANUAL_PATH = os.path.join(BASE_DIR, "More Files", "2026GameRebuilt.txt")
ALLIANCE_SELECTION_PATH = os.path.join(BASE_DIR, "More Files", "AllianceSelection.txt")
MetalMuscleLogo = os.path.join(BASE_DIR, "More Files", "1506-logo.jpg")

st.set_page_config(page_title="Metal Muscle Scouting", layout="centered")
st.image(MetalMuscleLogo)

selectedAlliance = st.title("FRC Scouting Master")
st.subheader("This will predict alliance selection")
st.badge("Please Note That This App Is Under Construction!", color="red")

CSV_PATH = st.file_uploader("Please Upload Scouting Data (.csv fromat)", type=["csv"])
declines = st.toggle("Allow Declines?")
user_prompt = st.text_area("Enter any additional notes for AI: ", value=".")
MATCH_KEY = f"2026misal"
tba_url = f"https://www.thebluealliance.com/api/v3/event/2026misal/rankings"

response = requests.get(tba_url, headers=headers)

AI_readable_rankings = []

#Add a timeout so the connection doesn't drop while the AI is thinking
client = OpenAI(
    base_url=HACK_CLUB_BASE_URL,
    api_key=HACK_CLUB_API_KEY,
    timeout=5000 # Wait up to 5 minutes for a response
)

if st.button("Generate Predictions"):
    try:
        readableCSV = CSV_PATH.read().decode("utf-8")

        if os.path.exists(MANUAL_PATH):
            with open(MANUAL_PATH, "r", encoding="utf-8", errors="ignore") as file:
                game_rules_text = file.read()
            print(f"Successfully loaded '{MANUAL_PATH}'.")
        else:
            raise FileNotFoundError(f"Could not find the file at {MANUAL_PATH}")
        
        if os.path.exists(ALLIANCE_SELECTION_PATH):
            with open(ALLIANCE_SELECTION_PATH, "r", encoding="utf-8", errors="ignore") as file:
                alliance_rules_text = file.read()
            print(f"Successfully loaded '{ALLIANCE_SELECTION_PATH}'.")
        else:
            raise FileNotFoundError(f"Could not find the file at {ALLIANCE_SELECTION_PATH}")
        
        if response.status_code == 200:
            data = response.json()
            rankings = data.get("rankings", [])

            if isinstance(rankings, list):

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
                    rank = team.get("rank"),
                    team_number = team.get("team_key").replace("frc", "")
                    wins = team.get("record", {}).get("wins")
                    losses = team.get("record", {}).get("losses")
                    ties = team.get("record", {}).get("ties")
                    # Append data to AI
                    AI_readable_rankings.append(team_info)

            else:
                # If the API returned a list or error object, wrap it nicely for the AI
                error_payload = {
                    "error": "Unexpected data format from TBA",
                    "raw_response": rankings
                }
                print(json.dumps(error_payload))
                st.write(json.dumps(error_payload))
                st.error("Something didn't work")

        else:
            st.write("An error has occured 2")
        #st.text(AI_readable_rankings)

        # 2. Combine your prompt with the game rules text content
        full_text_prompt = f"""Please use the given data to predict the alliances for the given event. GIVE EACH TEAMS 1ST PICK FIRST, THAN GIVE AWNSERS ON 2nd PICK! Game rule: {game_rules_text}, alliance selection
        rules: {alliance_rules_text}, scouting data (Weigh the current rankings slightly more than scouting data!): {readableCSV}, current rankings: {AI_readable_rankings} Use {declines} for if you should predict declining teams. 
        Please give your awnser in a way that follows alliance selection proccess. Note that pick go in decending order for 1st pick (1st - 8th) and acending for 2nd picks (8th - 1st). 
        Lastly, use {user_prompt} for anything else you should take into account. KNOW THAT THIS IS A SNAKE DRAFT!"""

        # 3. Create the payload content list
        content_list = [{"type": "text", "text": full_text_prompt}]


        print("Sending text data to Hack Club AI... Please wait.")

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": content_list
                }
            ]
        )

        print("\n--- AI RESPONSE ---")
        print(response.choices[0].message.content)
        st.text(response.choices[0].message.content)

    except Exception as e:
        print(f"\nAn error occurred: {e}")
        st.text(f"\nAn error has occurred. {e}")