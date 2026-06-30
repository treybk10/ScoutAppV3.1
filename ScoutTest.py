import cv2
import base64
import os
from openai import OpenAI
import streamlit as st

# --- Configuration ---
# WARNING: Put your NEW API key here!
HACK_CLUB_API_KEY = st.secrets["API_KEY"]
HACK_CLUB_BASE_URL = "https://ai.hackclub.com/proxy/v1" 

# FIX 1: Change to a valid model name
MODEL_NAME = "google/gemini-2.5-flash" 

VIDEO_PATH = ""

MANUAL_PATH = "/workspaces/ScoutAppV3.1/Other Files/2026GameRebuilt.txt"

TRENCH_URL = "/workspaces/ScoutAppV3.1/Other Files/Trench.png"
BUMP_URL = "/workspaces/ScoutAppV3.1/Other Files/Bump.png"
TOWER_URL = "/workspaces/ScoutAppV3.1/Other Files/Tower.png"
HUB_URL = "/workspaces/ScoutAppV3.1/Other Files/Hub.png"
DEPOT_URL = "/workspaces/ScoutAppV3.1/Other Files/Depot.png"
FEUL_URL = "/workspaces/ScoutAppV3.1/Other Files/Feul.png"



# FIX 2: Lower the frame count to prevent payload size limits
MAX_FRAMES = 20

st.set_page_config(page_title="Match Scouter", layout="centered")
selectedAlliance = st.title("FRC Scouting Master")

VIDEO_PATH = st.file_uploader("Please Upload Match Video", type=["mp4", "mov"])

allianceOptions = ["Red", "Blue"]
targetTeam = st.text_input("Please enter team number")
st.multiselect("Please select alliance", allianceOptions)

oldPrompt = f"""
    You are a FRC scouting app. Your job is to help identify team's {targetTeam} strenghts and weaknesses in the 2026 frc game, Rebuilt. PLEASE READ THE GIVEN FILE FOR INFO ABOUT THE GAME AND PICTURES FOR 
    FIELD ELEMENTS! ALSO READ FROM VIDEO PROVIDED 

    Know that the trench is ABOVE ground and the bump is ON the ground. You can tell by the fact that you see carpet below the trench. PLEASE SEE PHOTOS OF FIELD ELEMENTS FOR DETAILS

    {targetTeam} is on {selectedAlliance}

    Look for {selectedAlliance} colored bumpers with the number {targetTeam} in white text. DO NOT PAY ATTENTION TO THE OTHER 5 ROBOTS! ONLY {targetTeam}'s ROBOT


    Specifically, we want:
    #1: How effecient is {targetTeam} geting to and from the zones

    #2: How big and effective are {targetTeam}'s cycles? Do they shoot on the move? If so how accurate are they? If they aren't, how fast can they dump their load and how many loads do they unload?

    #3: If you were to guess, how uch fuel did {targetTeam} score in the entire match? Break it down into teleop and auto. Use the example photos for game peice info.

    #4: How efficient is {targetTeam}'s intake? Can they intake feul quickly off the ground or does it get jammed? 

    #5: Where can {targetTeam} shoot from? Can they shoot close? How about far?

    #6: Did they play any defense? If so, how effective was it? If they did play defense, focus on any team they played defense against to see if they were "shut down"/were slowed down by defense

    #7: Did they have defense played against them? If so, did it hurt {targetTeam}?
    
    Please make the awnser easy to read and if you are going to give time stamps, please use what exact time it is in the video, not what time is left in the match. ONLY FOCUS ON KEY PARTS OF THE MATCH
"""

prompt = f"""
    You are a FRC scouting app. Your job is to help identify team's {targetTeam} strenghts and weaknesses in the 2026 frc game, Rebuilt. PLEASE READ THE GIVEN FILE FOR INFO ABOUT THE GAME AND PICTURES FOR 
    FIELD ELEMENTS! ALSO READ FROM VIDEO PROVIDED 

    Know that the trench is ABOVE ground and the bump is ON the ground. You can tell by the fact that you see carpet below the trench. PLEASE SEE PHOTOS OF FIELD ELEMENTS FOR DETAILS

    {targetTeam} is on {selectedAlliance}

    Look for {selectedAlliance} colored bumpers with the number {targetTeam} in white text. DO NOT PAY ATTENTION TO THE OTHER 5 ROBOTS! ONLY {targetTeam}'s ROBOT

    Please format the response good so that it is easy to read. Focus on the key parts of {targetTeam}. If you are going to use timestamps, use the match timer NOT how long it is in the video.
    Please do not repeat any part of this prompt. 

    You are to awnser LIKE A MATCH SCOUTER! Use this prompt, but do NOT use it in your response! This app will be shared with multiple people who didn't write the prompt!  


    Specifically, we want:
    #1: Does {targetTeam} have any issues getting around the field?

    #2: Where does {targetTeam} shoot from? Far? Close? Would defense be a stratagey to stop them from scoring?

    #3: Is there any other things you found that would help try and slow them down if we were put against {targetTeam}?

    #4: Does {targetTeam} play defense? If so, how efective is it? Who do they play it against?
    
"""


# --- 1. Video Processing Function ---
def extract_frames_from_video(video_path, max_frames=MAX_FRAMES):
    video = cv2.VideoCapture(video_path)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    if total_frames == 0:
        raise ValueError("Could not read video. Check the file path.")

    frame_interval = max(1, total_frames // max_frames)

    base64_frames = []
    frame_count = 0

    print(f"Extracting frames from {video_path}...")
    while video.isOpened() and len(base64_frames) < max_frames:
        success, frame = video.read()
        if not success:
            break

        if frame_count % frame_interval == 0:
            # Resize frame to save bandwidth
            frame = cv2.resize(frame, (512, 512))

            # FIX 3: Lower JPEG quality to 70% to drastically reduce file size
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]
            _, buffer = cv2.imencode(".jpg", frame, encode_param)

            base64_string = base64.b64encode(buffer).decode("utf-8")
            base64_frames.append(base64_string)

        frame_count += 1

    video.release()
    print(f"Successfully extracted {len(base64_frames)} frames.")
    return base64_frames



#uploaded_pdf = st.file_uploader("Upload Scouting PDF to analyze", type=["pdf"])



# --- 2. Setup AI Client ---
# FIX 4: Add a timeout so the connection doesn't drop while the AI is thinking
client = OpenAI(
    base_url=HACK_CLUB_BASE_URL,
    api_key=HACK_CLUB_API_KEY,
    timeout=2000 # Wait up to 2 minutes for a response
)
if st.button("Load matches"):
    try:
        frames = extract_frames_from_video(VIDEO_PATH, MAX_FRAMES)

        content_list = [{"type": "text", "text": prompt}]

        if os.path.exists(MANUAL_PATH):
            with open(MANUAL_PATH, "r", encoding="utf-8", errors="ignore") as file:
                game_rules_text = file.read()
            print(f"Successfully loaded '{MANUAL_PATH}'.")
        else:
            raise FileNotFoundError(f"Could not find the file at {MANUAL_PATH}")

        # 2. Combine your prompt with the game rules text content
        full_text_prompt = f"{prompt}\n\n--- REFERENCE GAME RULES FROM MANUAL ---\n{game_rules_text}"

        # 3. Create the payload content list
        content_list.append([{"type": "text", "text": full_text_prompt}])

        content_list.append([{
            "type": "image_url",
                    "image_url": {
                        "url": TRENCH_URL
                    }
        }])
        content_list.append([{
            "type": "image_url",
                    "image_url": {
                        "url": HUB_URL
                    }
        }])
        content_list.append([{
            "type": "image_url",
                    "image_url": {
                        "url": BUMP_URL
                    }
        }])
        content_list.append([{
            "type": "image_url",
                    "image_url": {
                        "url": FEUL_URL
                    }
        }])

        print("Sending text data to Hack Club AI... Please wait.")


        

        print(f"Sending {len(frames)} frames to Hack Club AI ({MODEL_NAME})... Please wait.")

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
        st.text(f"\nError")