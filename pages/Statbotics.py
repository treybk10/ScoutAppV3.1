import json
import os

import statbotics
import requests
import streamlit as st


TBA_API_KEY = st.secrets["TBA_KEY"]

headers = {
    "X-TBA-Auth-Key": TBA_API_KEY
}

sb = statbotics.Statbotics()

BASE_DIR = os.path.dirname(__file__)
st.set_page_config(page_title="Metal Muscle Scouting", layout="centered")
MetalMuscleLogo = os.path.join(BASE_DIR, "More Files", "1506-logo.jpg")

st.image(MetalMuscleLogo)

st.badge("Statbotics server is currently down! Some features may not work!", color="red")

st.page_link("pages/CurrentRankings.py", label="Current Rankings")
st.page_link("pages/StandScouting.py", label="Stand Scouting")
st.page_link("pages/Statbotics.py", label="Statbotics")

event_key = st.text_input("Event Key: ", value="2026miwrc")


with st.expander("TBA Match Prediction"):

    playoffTBA = st.toggle("Playoff Match", value=False)
    finalsTBA = st.toggle("Finals Match", value=False)
    matchNumber = st.number_input("Please enter match number: ", step=1, value=1)

    if st.button("Find Predictions"):
        if matchNumber is not None and matchNumber > 0:

            

            if playoffTBA == True:
                MATCH_KEY = f"{event_key}_sf{matchNumber}m1"
            elif finalsTBA == True:
                MATCH_KEY = f"{event_key}_f1m{matchNumber}"
            else:
                MATCH_KEY = f"{event_key}_qm{matchNumber}"

            #st.write(MATCH_KEY)

            url = f"https://www.thebluealliance.com/api/v3/match/{MATCH_KEY}"    

            oprURL = f"https://www.thebluealliance.com/api/v3/event/{event_key}/oprs"

            response = requests.get(url, headers=headers)
            oprResponse = requests.get(oprURL, headers=headers)
            
            if response.status_code == 200 and oprResponse.status_code == 200:
                match_data = response.json()   
                opr_data = oprResponse.json()

                alliances = match_data.get("alliances", {})

                globalOPR = opr_data.get("oprs", {})

                red_teams = [team.replace("frc", "") for team in alliances.get("red", {}).get("team_keys", [])]
                blue_teams = [team.replace("frc", "") for team in alliances.get("blue", {}).get("team_keys", [])]

                red_alliance_opr = 0.0
                blue_alliance_opr = 0.0

                col1, col2 = st.columns(2)
                with col1:
                    st.error("RED ALLIANCE")
                    for teams in red_teams:
                        team_opr = globalOPR.get(f"frc{teams}", 0.0) 
                        red_alliance_opr += team_opr
                        st.write(teams, round(team_opr, 1))
                    st.error(f"Total Red OPR: {round(red_alliance_opr, 1)}")
                with col2:
                    st.info("BLUE ALLIANCE")
                    for teams in blue_teams:
                        team_opr = globalOPR.get(f"frc{teams}", 0.0) 
                        blue_alliance_opr += team_opr
                        st.write(teams, round(team_opr, 1))
                    st.info(f"Total Blue OPR: {round(blue_alliance_opr, 1)}")

                if red_alliance_opr > blue_alliance_opr:
                    st.error(f"Red Wins by {round(red_alliance_opr - blue_alliance_opr, 1)}")
                else:
                    st.info(f"Blue Wins by {round(blue_alliance_opr - red_alliance_opr, 1)}")

        else:
            st.error("Can't find match")

# st.badge("Match predictions will not work due to statbotics API issue!", color="red")
# with st.expander("Match Predicctions: "):
#     match_number = st.number_input("Match Number: ", value=1)
#     if st.toggle("Playoff Match"):
#         Playoff = True
#     else:
#         Playoff = False
#     if st.toggle("Elimination Match"):
#         Elimination = True
#     else:
#         Elimination = False


#     if st.button("Find Match Predictions"):
#         if Playoff:
#             final_key = f"{event_key}_f1m{match_number}"
#         elif Elimination:
#             final_key = f"{event_key}_sf{match_number}m1"
#         else:
#             final_key = f"{event_key}_qm{match_number}"
#         #match_data = sb.get_match(final_key)

#         final_key = final_key.strip().lower() 

#         api_url = f"https://api.statbotics.io/v3/match/{final_key}"

#         try: 
#             response = requests.get(api_url)

#             if response.status_code == 200:
        
#                 match_data = response.json()
                
#                 # Extract predicted metrics
#                 winner = match_data.get("predicted_winner") # API key update: predicted_winner
#                 red_prob = match_data.get("red_win_prob", 0.5)

#                 # Extract alliance team numbers
#                 red1 = match_data.get("red_1")
#                 red2 = match_data.get("red_2")
#                 red3 = match_data.get("red_3")
                
#                 blue1 = match_data.get("blue_1")
#                 blue2 = match_data.get("blue_2")
#                 blue3 = match_data.get("blue_3")

#                 video = match_data.get("video")

#                 if winner:  
#                     readable_winner = str(winner).upper()
#                     if readable_winner == "RED":
#                         prob = red_prob * 100
#                     elif readable_winner == "BLUE":
#                         prob = (1.0 - red_prob) * 100
#                     else:
#                         prob = 50.0     

#                 else:
#                     readable_winner = "UNKNOWN"
#                     prob = 0.0

#                 m1, m2 = st.columns(2)
#                 m1.metric(label="Predicted Winner Alliance", value=readable_winner)
#                 m2.metric(label="Win Probability", value=f"{prob:.1f}%")

#                 col1, col2 = st.columns(2)
#                 with col1:
#                     st.error("RED ALLIANCE")
#                     st.write(f":red-background[{red1}]")
#                     st.write(f":red-background[{red2}]")
#                     st.write(f":red-background[{red3}]")
#                 with col2:
#                     st.info("BLUE ALLIANCE")
#                     st.write(f":blue-background[{blue1}]")
#                     st.write(f":blue-background[{blue2}]")
#                     st.write(f":blue-background[{blue3}]")

#                 if video:
#                     video_URL = f"https://www.youtube.com/watch?v={video}"
#                     st.link_button("Match Video", video_URL)

#                 with st.expander("See raw match data: "):
#                     st.write(match_data)

#             elif response.status_code == 404:
#                 st.warning("Match data not found. Check if the match key or event key is entered correctly.")
#             else:
#                 st.error(f"Statbotics API returned an error code: {response.status_code}")

#         except requests.exceptions.RequestException as e:
#             st.error(f"Failed to connect to Statbotics. Network error: {e}")


with st.expander("Current Rankings:"):

    tba_url = f"https://www.thebluealliance.com/api/v3/event/{event_key}/rankings"

    response = requests.get(tba_url, headers=headers)

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

with st.expander("Team Match Schedule: "):
    wanted_team = st.number_input("Team Number", step=1)
    if st.button("Find Matches"):
        url = f'https://www.thebluealliance.com/api/v3/team/frc{wanted_team}/event/{event_key}/matches'
        response = requests.get(url, headers=headers)

        allMatches = response.json()
        print(f"Successfully retrieved {len(allMatches)} matches.")

        matches = [m for m in allMatches if m['comp_level'] == 'qm']
        matches = sorted(matches, key=lambda x: x['match_number'])

        playoffMatches = [m for m in allMatches if m['comp_level'] in ['sf', 'f']]
        playoffMatches = sorted(playoffMatches, key=lambda x: x.get('time') or 0)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.warning("MATCH NUMBER")
        with col2:
            st.error("RED ALLIANCE")
        with col3:
            st.info("BLUE ALLIANCE")

        
        for match in matches:
            match_number = match['match_number']
            red_alliance = match['alliances']['red']['team_keys']
            blue_alliance = match['alliances']['blue']['team_keys']

            red1, red2, red3 = red_alliance
            blue1, blue2, blue3 = blue_alliance

            col1, col2, col3 = st.columns(3)
            with col1:
                st.text(match_number)
            with col2:
                st.write(f":red-background[{red1}]")
                st.write(f":red-background[{red2}]")
                st.write(f":red-background[{red3}]")
            with col3:
                st.write(f":blue-background[{blue1}]")
                st.write(f":blue-background[{blue2}]")
                st.write(f":blue-background[{blue3}]")

        st.subheader("Playoffs")

        for match in playoffMatches:
            if match['comp_level'] == 'sf':
                display_label = f"Playoff {match['set_number']}"
            elif match['comp_level'] == 'f':
                display_label = f"Finals {match['match_number']}"
            else:
                display_label = f"Match {match['match_number']}"
            red_alliance = match['alliances']['red']['team_keys']
            blue_alliance = match['alliances']['blue']['team_keys']

            red1, red2, red3 = red_alliance
            blue1, blue2, blue3 = blue_alliance

            col1, col2, col3 = st.columns(3)
            with col1:
                st.text(display_label)
            with col2:
                st.write(f":red-background[{red1}]")
                st.write(f":red-background[{red2}]")
                st.write(f":red-background[{red3}]")
            with col3:
                st.write(f":blue-background[{blue1}]")
                st.write(f":blue-background[{blue2}]")
                st.write(f":blue-background[{blue3}]")



with st.expander("Event Match Schedule: "):
    url = f'https://www.thebluealliance.com/api/v3/event/{event_key}/matches'
    response = requests.get(url, headers=headers)

    allMatches = response.json()
    print(f"Successfully retrieved {len(allMatches)} matches.")

    matches = [m for m in allMatches if m['comp_level'] == 'qm']
    matches = sorted(matches, key=lambda x: x['match_number'])

    playoffMatches = [m for m in allMatches if m['comp_level'] in ['sf', 'f']]
    playoffMatches = sorted(playoffMatches, key=lambda x: x.get('time') or 0)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.warning("MATCH NUMBER")
    with col2:
        st.error("RED ALLIANCE")
    with col3:
        st.info("BLUE ALLIANCE")

    
    for match in matches:
        match_number = match['match_number']
        red_alliance = match['alliances']['red']['team_keys']
        blue_alliance = match['alliances']['blue']['team_keys']

        red1, red2, red3 = red_alliance
        blue1, blue2, blue3 = blue_alliance

        col1, col2, col3 = st.columns(3)
        with col1:
            st.text(match_number)
        with col2:
            st.write(f":red-background[{red1}]")
            st.write(f":red-background[{red2}]")
            st.write(f":red-background[{red3}]")
        with col3:
            st.write(f":blue-background[{blue1}]")
            st.write(f":blue-background[{blue2}]")
            st.write(f":blue-background[{blue3}]")


    st.subheader("Playoffs")


    for match in playoffMatches:
        if match['comp_level'] == 'sf':
            display_label = f"Playoff {match['set_number']}"
        elif match['comp_level'] == 'f':
            display_label = f"Finals {match['match_number']}"
        else:
            display_label = f"Match {match['match_number']}"
        red_alliance = match['alliances']['red']['team_keys']
        blue_alliance = match['alliances']['blue']['team_keys']

        red1, red2, red3 = red_alliance
        blue1, blue2, blue3 = blue_alliance

        col1, col2, col3 = st.columns(3)
        with col1:
            st.text(display_label)
        with col2:
            st.write(f":red-background[{red1}]")
            st.write(f":red-background[{red2}]")
            st.write(f":red-background[{red3}]")
        with col3:
            st.write(f":blue-background[{blue1}]")
            st.write(f":blue-background[{blue2}]")
            st.write(f":blue-background[{blue3}]")


#st.badge("Team data will not work due to statbotics API issue!", color="red")
with st.expander("Find Team Data"):
    search_team = st.number_input("Enter Team Number", step=1)

    if st.button("Search For Team"):
        try:
            team_data = sb.get_team(search_team)

            epa_data = team_data['norm_epa']
            record_data = team_data['record']

            st.header(f"Team {team_data['name']}")
            st.subheader(f"EPA: {epa_data['current']}")
            st.subheader(f"Win Rate: {record_data['winrate']}")

            st.subheader(f"Country: {team_data['country']}")
            st.subheader(f"State: {team_data['state']}")
            st.subheader(f"Rookie Year: {team_data['rookie_year']}")
            with st.expander("View Raw Team Data"):
                st.write(team_data)

        except Exception as e:
            st.error("Can't find data on team. Make sure team number is set correctly!")