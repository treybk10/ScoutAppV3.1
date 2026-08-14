import os

import requests
import streamlit as st

TBA_API_KEY = st.secrets["TBA_KEY"]

headers = {
    "X-TBA-Auth-Key": TBA_API_KEY
}

BASE_DIR = os.path.dirname(__file__)
MetalMuscleLogo = os.path.join(BASE_DIR, "More Files", "1506-logo.jpg")

st.set_page_config(page_title="Metal Muscle Scouting", layout="centered")
st.image(MetalMuscleLogo)

selectedAlliance = st.title("FRC Scouting Master")
st.subheader("Figure out next match")

event_key = st.text_input("Event Key", value="2026miwrc")



wanted_team = st.number_input("Team Number", step=1, value=1506)
if st.button("Find Matches"):
    try: 
        url = f'https://www.thebluealliance.com/api/v3/team/frc{wanted_team}/event/{event_key}/matches'
        response = requests.get(url, headers=headers)

        allMatches = response.json()
        print(f"Successfully retrieved {len(allMatches)} matches.")

        matches = [m for m in allMatches if m['comp_level'] == 'qm']
        matches = sorted(matches, key=lambda x: x['match_number'])

        playoffMatches = [m for m in allMatches if m['comp_level'] in ['sf', 'f']]
        playoffMatches = sorted(playoffMatches, key=lambda x: x.get('time') or 0)


        st.subheader("Quals Matches")
        for match in matches:
            match_number = match['match_number']

            with st.expander(f"{match_number}"):

                red_alliance = match['alliances']['red']['team_keys']
                blue_alliance = match['alliances']['blue']['team_keys']

                red1, red2, red3 = red_alliance
                blue1, blue2, blue3 = blue_alliance

                col1, col2, col3 = st.columns(3)
                # with col1:
                #     st.text(match_number)
                with col1:
                    with st.expander(red1):
                        st.write(f":red-background[{red1}]")
                    with st.expander(red2):
                        st.write(f":red-background[{red2}]")
                    with st.expander(red3):
                        st.write(f":red-background[{red3}]")
                with col2:
                    with st.expander(blue1):
                        st.write(f":blue-background[{blue1}]")
                    with st.expander(blue2):
                        st.write(f":blue-background[{blue2}]")
                    with st.expander(blue3):
                        st.write(f":blue-background[{blue3}]")

        st.subheader("Playoffs")

        for match in playoffMatches:
            if match['comp_level'] == 'sf':
                display_label = f"Playoff {match['set_number']}"
            elif match['comp_level'] == 'f':
                display_label = f"Finals {match['match_number']}"
            else:
                display_label = f"Match {match['match_number']}"

            with st.expander(f"{display_label}"):
                
                red_alliance = match['alliances']['red']['team_keys']
                blue_alliance = match['alliances']['blue']['team_keys']

                red1, red2, red3 = red_alliance
                blue1, blue2, blue3 = blue_alliance

                col1, col2, col3 = st.columns(3)
                # with col1:
                #     st.text(display_label)
                with col1:
                    with st.expander(red1):
                        st.write(f":red-background[{red1}]")
                    with st.expander(red2):
                        st.write(f":red-background[{red2}]")
                    with st.expander(red3):
                        st.write(f":red-background[{red3}]")
                with col2:
                    with st.expander(blue1):
                        st.write(f":blue-background[{blue1}]")
                    with st.expander(blue2):
                        st.write(f":blue-background[{blue2}]")
                    with st.expander(blue3):
                        st.write(f":blue-background[{blue3}]")
    except Exception as e:
        st.error("Something went wrong. Please check event key and team number")
        with st.expander("Error Code:"):
            st.write(e)