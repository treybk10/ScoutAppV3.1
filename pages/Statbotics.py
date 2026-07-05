import os

import statbotics
import streamlit as st

sb = statbotics.Statbotics()


BASE_DIR = os.path.dirname(__file__)
st.set_page_config(page_title="Metal Muscle Scouting", layout="centered")
MetalMuscleLogo = os.path.join(BASE_DIR, "More Files", "1506-logo.jpg")

st.image(MetalMuscleLogo)
st.badge("Please Note That This App Is Under Construction!", color="red")



event_key = st.text_input("Event Key: ", value="2026misal")
with st.expander("Match Predicctions: "):
    match_number = st.number_input("Match Number: ", value=1)
    if st.toggle("Playoff Match"):
        Playoff = True
    else:
        Playoff = False
    if st.toggle("Elimination Match"):
        Elimination = True
    else:
        Elimination = False


    if st.button("Find Match Predictions"):
        if Playoff:
            final_key = f"{event_key}_f1m{match_number}"
        elif Elimination:
            final_key = f"{event_key}_sf{match_number}m1"
        else:
            final_key = f"{event_key}_qm{match_number}"
        match_data = sb.get_match(final_key)
        #st.write(match_data)
        
        predictions = match_data.get("pred")

        winner = predictions.get("winner")
        red_prob = predictions.get("red_win_prob")

        if winner:  
            readable_winner = str(winner).upper()

            if readable_winner == "RED":
                prob = red_prob * 100
            elif readable_winner == "BLUE":
                prob = (1.0 - red_prob) * 100
            else:
                prob = 50.0  # Perfectly even prediction split

        else:
            readable_winner = "UNKNOWN"
            prob = 0.0

        m1, m2 = st.columns(2)
        m1.metric(label="Predicted Winner Alliance", value=readable_winner)
        m2.metric(label="Win Probability", value=f"{prob:.1f}%")
        with st.expander("See raw match data: "):
            st.write(match_data)



with st.expander("Team Match Schedule: "):
    target_team = st.number_input("Enter a specific team: ", step=1)

    if st.button("Find Matches"):
        event_mathces = sb.get_matches(event=event_key, team=target_team, fields=["match_name", "alliances"])

        for match in event_mathces:
            match_number = match["match_name"]

            alliances_data = match["alliances"]
        
            red_alliance = alliances_data["red"]["team_keys"]
            blue_alliance = alliances_data["blue"]["team_keys"]

            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(match_number)
            with col2:
                st.write(red_alliance)
            with col3:
                st.write(blue_alliance)


with st.expander("Event Match Schedule: "):
    event_mathces = sb.get_matches(event=event_key, fields=["match_name", "alliances"])

    for match in event_mathces:
        match_number = match["match_name"]

        alliances_data = match["alliances"]
    
        red_alliance = alliances_data["red"]["team_keys"]
        blue_alliance = alliances_data["blue"]["team_keys"]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(match_number)
        with col2:
            st.write(red_alliance)
        with col3:
            st.write(blue_alliance)

with st.expander("Find Team Data"):
    search_team = st.number_input("Enter Team Number", step=1)
    if st.button("Search For Team"):
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