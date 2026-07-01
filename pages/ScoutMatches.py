import os
import streamlit as st
import requests
import pandas as pd

#session state for streamlit
if "found_teams" not in st.session_state:
    st.session_state.found_teams = False
if "selected_team_state" not in st.session_state:
    st.session_state.selected_team_state = []
if "entered_data" not in st.session_state:
    st.session_state.entered_data = []
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

    selected_team = st.multiselect("Please select team:", wanted_teams, key="selected_team_state", max_selections=1)

if st.session_state.selected_team_state:
    st.subheader("Auto!")
    starting_auto = st.multiselect("Select auto starting location", auto_starting, max_selections=1)

    if starting_auto:
        if "Center" in starting_auto:
            center_intake = st.toggle("Intaked extra fuel?")
            center_shoot = st.toggle("Shot any fuel?")
            neutral_passes = 0
        else:
            neutral_passes = st.number_input("Number of passes to neutral zone", step=1)
            center_intake = False
            center_shoot = False
        robo_auto_climb = st.toggle("Climb in auto")

        st.subheader("Tele-op!")

        robo_shooter_type = st.multiselect("Shooter type: ", shooter_types, max_selections=1)
        robo_hopper_size = st.select_slider("Hopper size (roughly)", ["Small (<30)", "Medium (31-60)", "Large (>61)"])
        robo_has_scored = st.toggle("Robot has scored")
        if robo_has_scored:
            robo_accuracy = st.slider("Shooter accuracy %", min_value=0, max_value=100, step=1, value=50)
            robo_throughput = st.multiselect("Robot shooting speed", ["Very Slow", "Below Average", "Average", "Above Average", "Very Quick"])
        if not robo_has_scored:
            robo_accuracy = 0
            robo_throughput = "They didn't score"
        robo_cycle_time = st.select_slider("Robot cycle time", ["Terrible (includes mechanical failures)", "It's ok, but could be better", "Average", "Good", "Great!", "Can't Do Better"])

        robo_driving = st.select_slider("How fluid is their driving?", ["Not real sure what they're doing", "Mechanical failure that hinders drive performance", "Could be better", "They did great!", "Couldn't be better"])

        robo_intake = st.multiselect("How do they intake?", ["Floor", "Outpost/Human Player", "Both"], max_selections=1)
        if "Floor" in robo_intake:
            robo_intake_rating = st.select_slider("How's the intake?", ["There's an intake?", "Jammed several times", "Average", "Above Average", "Awesome!"])
        if "Floor" not in robo_intake:
            robo_intake_rating = "Can't intake from floor"

        robo_do_when_inactive = st.multiselect("When the hub is inactive, what do they do? (Can select more that one)", ["Nothing", "Defense", "Clear opposing alliances fuel", "Pass/Collect fuel"])

        robo_sotm = st.toggle("Shoot on the move?")
        robo_trench = st.toggle("Did the robot drive under the trench?")
        robo_bump = st.toggle("Did the robot drive over the bump?")

        robo_play_defense = st.toggle("Did they play defense?")
        if robo_play_defense:
            robo_defense_effeciency = st.select_slider("How effecient was their defense?", ["Hurt more than helped", "It's ok", "Great!", "Amazing!"])
        if not robo_play_defense:
            robo_defense_effeciency = "No defense"

        robo_had_defense = st.toggle("Did anyone play defense against them?")
        if robo_had_defense:
            robo_had_defense_rating = st.select_slider("How much did defense hurt them?", ["Wait, what defense?", "It kinda did", "Significantly hurt them", "Cost them the match"])
            robo_played_defense_on_team = st.text_input("Who played defense on them?")
        if not robo_had_defense:
            robo_had_defense_rating = "No defense against them"
            robo_played_defense_on_team = "No one"
        robo_tele_climb = st.toggle("Climb in tele-op")


        robo_extra = st.text_area("Anything else we should know about this match?")

        if st.button("Save match results"):
            #st.session_state.entered_data = [st.session_state.selected_team_state, qualMatch, starting_auto, center_intake, center_shoot, neutral_passes, robo_auto_climb, robo_shooter_type, robo_hopper_size, robo_accuracy, robo_cycle_time, robo_driving, robo_intake, robo_intake_rating, robo_do_when_inactive, robo_sotm, robo_trench, robo_bump, robo_play_defense, robo_defense_effeciency, robo_had_defense, robo_had_defense_rating, robo_played_defense_on_team, robo_tele_climb, robo_extra]
            match_data_entered = {
                "Team": st.session_state.selected_team_state,
                "Qual Number": qualMatch,
                "Auto Location": starting_auto,
                "Center Intake": center_intake,
                "Center Shoot": center_shoot,
                "Neutral Passes": neutral_passes,
                "Robot Auto Climb": robo_auto_climb,
                "Robot Shooter Type": robo_shooter_type,
                "Robot Hopper Size": robo_hopper_size,
                "Robot Has Scored Fuel": robo_has_scored,
                "Robot Accuracy": robo_accuracy,
                "Robot Throughput": robo_throughput,
                "Robot Cycle Time": robo_cycle_time,
                "Robot Driving Rating": robo_driving,
                "Robot Intake": robo_intake,
                "Robot Intake Rating": robo_intake_rating,
                "Robot Does When Inactive": ", ".join(robo_do_when_inactive),
                "Robot Shoot On The Move": robo_sotm,
                "Robot Trench": robo_trench,
                "Robot Bump": robo_bump,
                "Robot Played Defense": robo_play_defense,
                "Robot Defense Rating": robo_defense_effeciency,
                "Robot Had Defense": robo_had_defense,
                "Who Played Defense Against Team": robo_played_defense_on_team,
                "Robot Climbed In End Game": robo_tele_climb,
                "Extra Notes": robo_extra
            }
            #match_data_entered_raw = {st.session_state.selected_team_state, qualMatch, starting_auto, center_intake, center_shoot, neutral_passes, robo_auto_climb, robo_shooter_type, robo_hopper_size, robo_accuracy, robo_cycle_time, robo_driving, robo_intake, robo_intake_rating, ", ".join(robo_do_when_inactive), robo_sotm, robo_trench, robo_bump, robo_play_defense, robo_defense_effeciency, robo_had_defense, robo_had_defense_rating, robo_played_defense_on_team, robo_tele_climb, robo_extra}
            st.session_state.entered_data = match_data_entered

if st.session_state.entered_data:
    raw_data = st.session_state.entered_data
    downloadable_data = pd.DataFrame([raw_data])
    covert_data = downloadable_data.to_csv(index=False, header=False).encode('utf-8')

    st.download_button(
        label="Download Match",
        data=covert_data,
        file_name="Match_Data.csv",
        mime="text/csv"
    )