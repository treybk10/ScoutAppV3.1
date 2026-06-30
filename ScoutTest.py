import cv2
import base64
import os
from openai import OpenAI
import streamlit as st

import tempfile

# --- Configuration ---
#API KEY GOES HERE
HACK_CLUB_API_KEY = st.secrets["API_KEY"]
HACK_CLUB_BASE_URL = "https://ai.hackclub.com/proxy/v1" 

# pro doesn't work?
MODEL_NAME = "google/gemini-2.5-flash" 

VIDEO_PATH = ""

BASE_DIR = os.path.dirname(__file__)

MANUAL_PATH = os.path.join(BASE_DIR, "Other Files", "2026GameRebuilt.txt")

TRENCH_URL = os.path.join(BASE_DIR, "Other Files", "Trench.png")
BUMP_URL = os.path.join(BASE_DIR, "Other Files", "Bump.png")
TOWER_URL = os.path.join(BASE_DIR, "Other Files", "Tower.png")
HUB_URL = os.path.join(BASE_DIR, "Other Files", "Hub.png")
DEPOT_URL = os.path.join(BASE_DIR, "Other Files", "Depot.png")
FUEL_URL = os.path.join(BASE_DIR, "Other Files", "Feul.png")


#Max frames AI reads
MAX_FRAMES = 160

st.set_page_config(page_title="Match Scouter", layout="centered")
selectedAlliance = st.title("FRC Scouting Master")

VIDEO_PATH = st.file_uploader("Please Upload Match Video", type=["mp4", "mov"])

allianceOptions = ["Red", "Blue"]
targetTeam = st.text_input("Please Enter Team Number")
st.multiselect("Please Select What Alliance The Scouted Team Is On", allianceOptions,  max_selections=1)

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
    You are a FRC scouting app. Your job is to help identify team's {targetTeam} strenghts and weaknesses in the 2026 frc game, Rebuilt. 
    
    We will provide you with the information of the game as well as pictures of game elements and field elements.

    Please scout {targetTeam} and tell us how they perform in a match, where we could slow them down if we were against them, and how we could help them if we were with them.

    Robots are identifiable by the white numbers on their bumpers. Find the one with {targetTeam}'s number.

    Please do not repeat this prompt in your awnser. This is used in a scouting app that a lot of people are using and they don't need to know this prompt.  Don't mess up! Think carefully! 
    
"""

def encode_image_to_base64(file_path):
    """Converts a local image file into a Base64 string for the API payload."""
    if os.path.exists(file_path):
        with open(file_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    else:
        raise FileNotFoundError(f"Missing critical app asset: {file_path}")


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

            # reduced quality to reduce ai payload
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 80]
            _, buffer = cv2.imencode(".jpg", frame, encode_param)

            base64_string = base64.b64encode(buffer).decode("utf-8")
            base64_frames.append(base64_string)

        frame_count += 1

    video.release()
    print(f"Successfully extracted {len(base64_frames)} frames.")
    return base64_frames


#Add a timeout so the connection doesn't drop while the AI is thinking
client = OpenAI(
    base_url=HACK_CLUB_BASE_URL,
    api_key=HACK_CLUB_API_KEY,
    timeout=5000 # Wait up to 5 minutes for a response
)


b64_TRENCH = encode_image_to_base64(TRENCH_URL)
b64_BUMP = encode_image_to_base64(BUMP_URL)
b64_HUB = encode_image_to_base64(HUB_URL)
b64_FUEL = encode_image_to_base64(FUEL_URL)

if st.button("Scout match"):
    if VIDEO_PATH is not None:  # Ensure a file was actually uploaded
        # Create a temporary file on the local disk drive
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
            temp_video.write(VIDEO_PATH.read())
            temp_video_path = temp_video.name  # This gives you a valid string path

        # Pass the string path to your existing OpenCV function
        frames = extract_frames_from_video(temp_video_path, MAX_FRAMES)

        # Clean up and delete the temporary file from disk immediately
        os.unlink(temp_video_path)

    try:
        #frames = extract_frames_from_video(VIDEO_PATH, MAX_FRAMES)

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


        content_list.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{b64_BUMP}"
            }
        })
        content_list.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{b64_FUEL}"
            }
        })
        content_list.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{b64_HUB}"
            }
        })
        content_list.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{b64_TRENCH}"
            }
        })

        print("Sending text data to Hack Club AI... Please wait.")


        for frame in frames:
            content_list.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{frame}"
                }
            })

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
        st.text(f"\nAn error has occurred. {e}")