import os
import streamlit as st
import requests

#session state for streamlit
if "found_teams" not in st.session_state:
    st.session_state.found_teams = False
if "selected_team_state" not in st.session_state:
    st.session_state.selected_team_state = []
if "red_teams" not in st.session_state:
    st.session_state.red_teams = []
if "blue_teams" not in st.session_state:
    st.session_state.blue_teams = []



TBA_API_KEY = st.secrets["TBA_KEY"]

headers = {
    "X-TBA-Auth-Key": TBA_API_KEY
}



BASE_DIR = os.path.dirname(__file__)

st.set_page_config(page_title="Metal Muscle Scouting", layout="centered")
MetalMuscleLogo = os.path.join(BASE_DIR, "More Files", "1506-logo.jpg")

st.image(MetalMuscleLogo)

selectedAlliance = st.title("FRC Scouting Master")
st.subheader("Scout Matches!")

st.badge("Please Note That This App Is Under Construction!", color="red")
st.badge("Matches for now are only for 2026 Michigan State Cahmpionship DTE field", color="red")

qualMatch = st.text_input("Please enter match number:")
allianceOptions = ["Red", "Blue"]
selectedAlliance = st.multiselect("Please Select What Alliance The Scouted Team Is On", allianceOptions,  max_selections=1)
MATCH_KEY = f"2026micmp1_qm{qualMatch}"

url = f"https://www.thebluealliance.com/api/v3/match/{MATCH_KEY}"


auto_starting = ["Left", "Right", "Center"]
shooter_types = ["Single Dumper", "Multi-Wide Dumper", "Single Turret", "Dual Turret"]



if st.button("Find Teams"):
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        match_data = response.json()

        if not match_data:
            st.warning("No match data! Please check event key!")
            st.session_state.found_teams = False
        else:
            alliances = match_data.get("alliances", {})
            st.session_state.red_teams = [team.replace("frc", "") for team in alliances.get("red", {}).get("team_keys", [])]
            st.session_state.blue_teams = [team.replace("frc", "") for team in alliances.get("blue", {}).get("team_keys", [])]
            st.session_state.found_teams = True

if st.session_state.found_teams:
    if "Red" in selectedAlliance:
        wanted_teams = st.session_state.red_teams
    if "Blue" in selectedAlliance:
        wanted_teams = st.session_state.blue_teams
        teamArray = [wanted_teams]

    col1, col2 = st.columns(2)
    with col1:
        st.warning("RED ALLIANCE")
        for teams in st.session_state.red_teams:
            st.write(teams)
    with col2:
        st.info("BLUE ALLIANCE")
        for teams in st.session_state.blue_teams:
            st.write(teams)

    selected_team = st.multiselect("Please select team:", wanted_teams, key="selected_team_state")

if st.session_state.selected_team_state:
    st.subheader("Auto!")
    starting_auto = st.multiselect("Select auto starting location", auto_starting, max_selections=1)

    if starting_auto:
        if "Center" in starting_auto:
            center_intake = st.toggle("Intaked extra fuel?")
            center_shoot = st.toggle("Shot any fuel?")
        else:
            neutral_passes = st.number_input("Number of passes to neutral zone", step=1)
        robo_auto_climb = st.toggle("Climb in auto")

        st.subheader("Tele-op!")

        robo_shooter_type = st.multiselect("Shooter type: ", shooter_types)
        robo_hopper_size = st.select_slider("Hopper size (roughly)", ["Small (<30)", "Medium (31-60)", "Large (>61)"])
        robo_accuracy = st.slider("Shooter accuracy %", min_value=0, max_value=100, step=1, value=50)
        robo_cycle_time = st.select_slider("Robot cycle time", ["Like 1506 at Marysville :) (includes mechanical failures)", "It's ok, but could be better", "Average", "Good", "Great!", "Equivalent to High Tide"])

        robo_driving = st.select_slider("How fluid is their driving?", ["Not real sure what they're doing", "Mechanical failure that hinders drive performance", "Could be better", "They did great!", "Couldn't be better"])

        robo_intake = st.multiselect("How do they intake? (Can select multiple)", ["Floor", "Outpost/Human Player"])
        if "Floor" in robo_intake:
            robo_intake = st.select_slider("How's the intake?", ["There's an intake?", "Jammed several times", "Average", "Awesome!"])

        st.multiselect("When the hub is inactive, what do they do? (Can select more that one)", ["Nothing", "Defense", "Clear opposing alliances fuel", "Pass/Collect fuel"])

        robo_sotm = st.toggle("Shoot on the move?")
        robo_trench = st.toggle("Did the robot drive under the trench?")
        robo_bump = st.toggle("Did the robot drive over the bump?")

        robo_play_defense = st.toggle("Did they play defense?")
        if robo_play_defense:
            robo_defense_effeciency = st.select_slider("How effecient was their defense?", ["Hurt more than helped", "It's ok", "Great!", "Amazing!"])
        robo_had_defense = st.toggle("Did anyone play defense against them?")
        if robo_had_defense:
            robo_had_defense_rating = st.select_slider("How much did defense hurt them?", ["Wait, what defense?", "It kinda did", "Significantly hurt them", "Cost them the match"])
            robo_played_defense_on_team = st.text_input("Who played defense on them?")


        robo_extra = st.text_area("Anything else we should know about this match?")