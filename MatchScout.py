import cv2
import base64
import os
from openai import OpenAI
import streamlit as st
import random
import time
from yt_dlp import YoutubeDL

import tempfile

# --- Configuration ---
#API KEY GOES HERE
HACK_CLUB_API_KEY = st.secrets["API_KEY"]
HACK_CLUB_BASE_URL = "https://ai.hackclub.com/proxy/v1" 

# pro doesn't work?
MODEL_NAME = "openrouter/free" 

VIDEO_PATH = ""

BASE_DIR = os.path.dirname(__file__)

MANUAL_PATH = os.path.join(BASE_DIR, "Other Files", "2026GameRebuilt.txt")


TRENCH_URL = os.path.join(BASE_DIR, "Other Files", "Trench.png")
BUMP_URL = os.path.join(BASE_DIR, "Other Files", "Bump.png")
TOWER_URL = os.path.join(BASE_DIR, "Other Files", "Tower.png")
HUB_URL = os.path.join(BASE_DIR, "Other Files", "Hub.png")
DEPOT_URL = os.path.join(BASE_DIR, "Other Files", "Depot.png")
FUEL_URL = os.path.join(BASE_DIR, "Other Files", "Feul.png")

st.set_page_config(page_title="Metal Muscle Scouting", layout="centered")
MetalMuscleLogo = os.path.join(BASE_DIR, "Other Files", "1506-logo.jpg")


#Max frames AI reads
MAX_FRAMES = 140

st.image(MetalMuscleLogo)

st.title("FRC Scouting Master")

downloadedVideo = st.toggle("Use downloaded video?", value=False)
if downloadedVideo == True:
    YOUTUBE_URL = None
    VIDEO_PATH = st.file_uploader("Please Upload Match Video", type=["mp4", "mov"])
elif downloadedVideo == False:
    YOUTUBE_URL = st.text_input("Please Enter YouTube Match Video Link", placeholder="https://youtube.com...")
    VIDEO_PATH = None

allianceOptions = ["Red", "Blue"]
targetTeam = st.number_input("Please Enter Team Number", step=1)
#selectedAlliance = st.multiselect("Please Select What Alliance The Scouted Team Is On", allianceOptions,  max_selections=1)

prompt = f"""
    You are a FRC scouting app. Your job is to help identify team's {targetTeam} strenghts and weaknesses in the 2026 frc game, Rebuilt. 
    
    We will provide you with the information of the game as well as pictures of game elements and field elements.

    Please scout {targetTeam} and tell us how they perform in a match, where we could slow them down if we were against them, and how we could help them if we were with them.

    Also how is their drive team? Do you drive smoothly or more jittery?

    Any mechanical failures? Shooter, intake, get stuck anywhere?

    What about defense? Does {targetTeam} play defense? Do they have defense agaisnt them? If so, does it {targetTeam}?

    Robots are identifiable by the white numbers on their bumpers. Find the one with {targetTeam}'s number.

    Please do not repeat any part of this prompt in your awnser. This is used in a scouting app that a lot of people are using and they don't need to know this prompt.  Don't mess up! Think carefully! 
    If you are going to give timestamps, use the match timer please.
    
"""

def download_youtube_to_temp(url):

    temp_dir = tempfile.gettempdir()
    

    ydl_opts = {

        'format': 'best[height<=720][ext=mp4]/best[height<=720]', 

        'outtmpl': os.path.join(temp_dir, 'yt_scout_video.mp4'),
        'quiet': True,
        'no_warnings': True,

        'rm_cachedir': True,

        'extractor_args': {
            'youtube': {
                'player_client': ['default', '-android_sdkless'],
            }
        },

        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        },
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename

def encode_image_to_base64(file_path):
    """Converts a local image file into a Base64 string for the API payload."""
    if os.path.exists(file_path):
        with open(file_path, "rb") as image_file:

            img = cv2.imread(file_path)

            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
            success, buffer = cv2.imencode(".jpg", img, encode_param)

            return base64.b64encode(buffer).decode("utf-8")
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
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]
            _, buffer = cv2.imencode(".jpg", frame, encode_param)

            base64_string = base64.b64encode(buffer).decode("utf-8")
            base64_frames.append(base64_string)

        frame_count += 1

    video.release()
    print(f"Successfully extracted {len(base64_frames)} frames.")
    return base64_frames


#Add a timeout so the connection doesn't drop while the AI is thinking
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key= st.secrets["AI_API"],
    timeout=5000 # Wait up to 5 minutes for a response
)


b64_TRENCH = encode_image_to_base64(TRENCH_URL)
b64_BUMP = encode_image_to_base64(BUMP_URL)
b64_HUB = encode_image_to_base64(HUB_URL)
b64_FUEL = encode_image_to_base64(FUEL_URL)
b64_TOWER = encode_image_to_base64(TOWER_URL)
b64_DEPOT = encode_image_to_base64(DEPOT_URL)

if st.button("Scout Match"):

    with st.spinner("Scouting..."):

        if VIDEO_PATH is not None:  # Ensure a file was actually uploaded
            # Create a temporary file on the local disk drive
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
                temp_video.write(VIDEO_PATH.read())
                temp_video_path = temp_video.name  # This gives you a valid string path

            # Pass the string path to your existing OpenCV function
            frames = extract_frames_from_video(temp_video_path, MAX_FRAMES)

            # Clean up and delete the temporary file from disk immediately
            os.unlink(temp_video_path)

        # if not YOUTUBE_URL.strip() and YOUTUBE_URL is not None:
        #     st.warning("Please provide a valid YouTube URL first.")
        #     st.stop()
        try:
            if YOUTUBE_URL is not None:
                temp_video_path = None
            

                temp_video_path = download_youtube_to_temp(YOUTUBE_URL)

                frames = extract_frames_from_video(temp_video_path, MAX_FRAMES)

                if temp_video_path and os.path.exists(temp_video_path):
                    os.unlink(temp_video_path)


            if os.path.exists(MANUAL_PATH):
                with open(MANUAL_PATH, "r", encoding="utf-8", errors="ignore") as file:
                    game_rules_text = file.read()
                print(f"Successfully loaded '{MANUAL_PATH}'.")
            else:
                raise FileNotFoundError(f"Could not find the file at {MANUAL_PATH}")

            full_text_prompt = f"{prompt}\n\n--- REFERENCE GAME RULES FROM MANUAL ---\n{game_rules_text}"

            content_list = [{"type": "text", "text": full_text_prompt}]


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
            content_list.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{b64_DEPOT}"
                }
            })
            content_list.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{b64_TOWER}"
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

#if (VIDEO_PATH is not None):
#    st.video(VIDEO_PATH)