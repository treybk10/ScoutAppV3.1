import cv2
import base64
import os
from openai import OpenAI
import streamlit as st

# --- Configuration ---
#API KEY GOES HERE
HACK_CLUB_API_KEY = st.secrets["API_KEY"]
HACK_CLUB_BASE_URL = "https://ai.hackclub.com/proxy/v1" 

# pro doesn't work?
MODEL_NAME = "google/gemini-2.5-pro" 

BASE_DIR = os.path.dirname(__file__)

MANUAL_PATH = os.path.join(BASE_DIR, "More Files", "2026GameRebuilt.txt")
MetalMuscleLogo = os.path.join(BASE_DIR, "More Files", "1506-logo.jpg")

st.image(MetalMuscleLogo)

selectedAlliance = st.title("FRC Scouting Master")
st.subheader("This is to help with alliance selection. Import your scouting data and a prompt for AI and it will give you a pick list!")
st.badge("Please Note That This App Is Under Construction!", color="red")

CSV_PATH = st.file_uploader("Please Upload Scouting Data (.csv fromat)", type=["csv"])

user_prompt = st.text_input("Please enter prompt for AI")
base_prompt = f"You are a FRC scouter. Your job is to take the given files for the 2026 frc game rebuilt and figure out who would be the best robot to pick based on the other prompt. ONLY USE TEAMS FROM THE GIVEN LIST!"


#Add a timeout so the connection doesn't drop while the AI is thinking
client = OpenAI(
    base_url=HACK_CLUB_BASE_URL,
    api_key=HACK_CLUB_API_KEY,
    timeout=5000 # Wait up to 5 minutes for a response
)

if st.button("Scout teams"):
    try:
        readableCSV = CSV_PATH.read().decode("utf-8")
        #frames = extract_frames_from_video(VIDEO_PATH, MAX_FRAMES)

        if os.path.exists(MANUAL_PATH):
            with open(MANUAL_PATH, "r", encoding="utf-8", errors="ignore") as file:
                game_rules_text = file.read()
            print(f"Successfully loaded '{MANUAL_PATH}'.")
        else:
            raise FileNotFoundError(f"Could not find the file at {MANUAL_PATH}")

        # 2. Combine your prompt with the game rules text content
        full_text_prompt = f"{base_prompt}\n\n--- USER PROMPT: --- \n{user_prompt}\n\n--- REFERENCE GAME RULES FROM MANUAL ---\n{game_rules_text}\n\n--- FILE ---\n{readableCSV}"

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