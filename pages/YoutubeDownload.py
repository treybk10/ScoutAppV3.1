import cv2
import base64
import os
from openai import OpenAI
import streamlit as st
import random
import time
from yt_dlp import YoutubeDL

import tempfile


BASE_DIR = os.path.dirname(__file__)

st.set_page_config(page_title="Metal Muscle Scouting", layout="centered")
MetalMuscleLogo = os.path.join(BASE_DIR, "Other Files", "1506-logo.jpg")

st.image(MetalMuscleLogo)

st.title("FRC Scouting Master")


YOUTUBE_URL = st.text_input("Please Enter YouTube Match Video Link", placeholder="https://youtube.com...")

def download_youtube_to_temp(url):

    download_dir = os.path.join(BASE_DIR, "Downloaded_Matches")
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    

    ydl_opts = {
    'format': 'best[height<=720][ext=mp4]/best[height<=720]', 
    'outtmpl': os.path.join(download_dir, '%(title)s [%(id)s].%(ext)s'),
    'quiet': True,
    'no_warnings': True,
    'rm_cachedir': True,

    'extractor_args': {
        'youtube': {
            'player_client': ['default', 'ios'], 
        }
    },
    
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    },
}
    
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename


if st.button("Download") and YOUTUBE_URL is not None:
    download_youtube_to_temp(YOUTUBE_URL)