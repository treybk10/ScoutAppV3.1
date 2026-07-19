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
if "all_teams" not in st.session_state:
    st.session_state.all_teams = []
if "all_scouting_data" not in st.session_state:
    st.session_state.all_scouting_data = []
if "save_locked" not in st.session_state:
    st.session_state.save_locked = False

TBA_API_KEY = st.secrets["TBA_KEY"]

headers = {
    "X-TBA-Auth-Key": TBA_API_KEY
}

submit_match = False



BASE_DIR = os.path.dirname(__file__)

st.set_page_config(page_title="Metal Muscle Scouting", layout="centered")
MetalMuscleLogo = os.path.join(BASE_DIR, "More Files", "1506-logo.jpg")

st.image(MetalMuscleLogo)

st.page_link("pages/StandScouting.py", label="Stand Scouting")
st.page_link("pages/CurrentRankings.py", label="Current Rankings")
st.page_link("pages/Statbotics.py", label="Statbotics")

selectedAlliance = st.title("FRC Scouting Master")
st.subheader("Scout Matches!")

Entered_Match_Key = st.text_input("Please enter event key: ", value="2026micmp1")
qualMatch = st.text_input("Please enter match number:")
allianceOptions = ["Red", "Blue"]

RedPrediction = None
BluePrediction = None
#selectedAlliance = st.multiselect("Please Select What Alliance The Scouted Team Is On", allianceOptions,  max_selections=1)
#MATCH_KEY = f"2026micmp1_qm{qualMatch}"

MATCH_KEY = f"{Entered_Match_Key}_qm{qualMatch}"

url = f"https://www.thebluealliance.com/api/v3/match/{MATCH_KEY}"


auto_starting = ["Left", "Right", "Center"]
shooter_types = ["Single Dumper", "Multi-Wide Dumper", "Single Turret", "Dual Turret"]

total_scouting_data = []

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
            st.session_state.all_teams = [team.replace("frc", "") for team in alliances.get("red", {}).get("team_keys", [])] + [team.replace("frc", "") for team in alliances.get("blue", {}).get("team_keys", [])]
            st.session_state.found_teams = True


if st.session_state.found_teams:
    col1, col2 = st.columns(2)
    with col1:
        st.error("RED ALLIANCE")
        for teams in st.session_state.red_teams:
            st.write(teams)
        RedPrediction = st.number_input("Red Predicted Score", step=1)
    with col2:
        st.info("BLUE ALLIANCE")
        for teams in st.session_state.blue_teams:
            st.write(teams)
        BluePrediction = st.number_input("Blue Predicted Score", step=1)

    selected_team = st.multiselect("Please select team:", st.session_state.all_teams, key="selected_team_state", max_selections=1)

if st.session_state.selected_team_state:

    st.subheader("Auto!")
    starting_auto = st.multiselect("Select auto starting location", auto_starting, max_selections=1)
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
    robo_has_scored = st.toggle("Robot has scored", value=True)
    if robo_has_scored:
        robo_accuracy = st.slider("Shooter accuracy %", min_value=0, max_value=100, step=1, value=50)
        robo_throughput = st.select_slider("Robot shooting speed", ["Very Slow", "Below Average", "Average", "Above Average", "Very Quick"])
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


match_data_entered = None

# Only build the dictionary if a team is actively selected to prevent crashes
if st.session_state.selected_team_state:
    # Ensure team selection handles fallback formatting for lists safely
    team_clean = st.session_state.selected_team_state[0] if isinstance(st.session_state.selected_team_state, list) and st.session_state.selected_team_state else "Unknown"
    
    match_data_entered = {
        "Team": team_clean,
        "Qual Number": qualMatch,
        "Auto Location": starting_auto[0] if starting_auto else "None",
        "Center Intake": center_intake,
        "Center Shoot": center_shoot,
        "Neutral Passes": neutral_passes,
        "Robot Auto Climb": robo_auto_climb,
        "Robot Shooter Type": robo_shooter_type[0] if robo_shooter_type else "None",
        "Robot Hopper Size": robo_hopper_size,
        "Robot Has Scored Fuel": robo_has_scored,
        "Robot Accuracy": robo_accuracy,
        "Robot Throughput": robo_throughput,
        "Robot Cycle Time": robo_cycle_time,
        "Robot Driving Rating": robo_driving,
        "Robot Intake": robo_intake[0] if robo_intake else "None",
        "Robot Intake Rating": robo_intake_rating,
        "Robot Does When Inactive": ", ".join(robo_do_when_inactive) if robo_do_when_inactive else "Nothing",
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

st.divider()

# --- STEP 2: TRIGGER THE SAVE ACTION ---
# Consolidated into a single button layout to prevent duplicate state submissions
col_save, col_clear = st.columns(2)

with col_save:
    st.badge("Add current data to list", color="yellow")
    if st.button("Save Match Data"):   
        if match_data_entered:
            st.session_state.all_scouting_data.append(match_data_entered)
        else:
            st.error("Please ensure a team is selected and data is entered before saving.")

with col_clear:
    st.badge("This will clear current match results!", color="red")
    if st.button("Clear Current Data"):
        st.session_state.all_scouting_data = []
        st.toast("Local session memory has been wiped clean.", icon="⚠️")
        st.rerun()


if st.session_state.all_scouting_data:
    #st.subheader(f"Currently Collected Matches ({len(st.session_state.all_scouting_data)})")
    
    downloadable_data = pd.DataFrame(st.session_state.all_scouting_data)
    st.dataframe(downloadable_data)

    convert_data = downloadable_data.to_csv(index=False, header=False).encode('utf-8')

    st.download_button(
        label="Download All Data",
        data=convert_data,
        file_name=f"Scouting_Data_{Entered_Match_Key}.csv",
        mime="text/csv"
    )
else:
    st.info("No matches have been saved in this cache session yet.")

if RedPrediction is not None and BluePrediction is not None:
    if RedPrediction > 0 and BluePrediction > 0:
        st.subheader("Real Match Results")
        col1_2, col2_2 = st.columns(2)
        
        with col1_2:
            realRedScore = st.number_input("Real Red Score", step=1, min_value=0, value=0)
        with col2_2:
            realBlueScore = st.number_input("Real Blue Score", step=1, min_value=0, value=0)
            
        if realRedScore > 0 and realBlueScore > 0:
            redErrorOff = round((abs(realRedScore - RedPrediction) / realRedScore) * 100)
            blueErrorOff = round((abs(realBlueScore - BluePrediction) / realBlueScore) * 100)

            col1_3, col2_3 = st.columns(2)
            with col1_3:
                st.error("Red Prediction Error Margin: ")
                st.subheader(f"{redErrorOff}%")
            with col2_3:
                st.info("Blue Prediction Error Margin: ")
                st.subheader(f"{blueErrorOff}%")
                
            percentageOff = (redErrorOff + blueErrorOff) / 2
            st.warning("Average Strategy Deviation (Lower Is Better): ")
            st.title(f"{percentageOff}%")
