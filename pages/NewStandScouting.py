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

bufferLeft, middleData, bufferRight = st.columns([0.1, 0.8, 0.1])

with middleData:
    if st.session_state.selected_team_state:

        scouter_name = st.text_input("Scouter's name:", max_chars=20)

        st.divider()
        st.subheader("Auto!")
        starting_auto = st.multiselect("Select auto starting location: ", auto_starting, max_selections=2)
        if "Center" in starting_auto:
            center_scored = st.toggle("Scored any fuel?")
            center_intake = st.toggle("Intaked other fuel besides preload?")
            neutral_passes = 0
        else:
            neutral_passes = st.number_input("Number of passes to neutral zone", step=1, max_value=3, min_value=0)
            center_intake = False
            center_shoot = False

        robo_auto_climb = st.toggle("Climb in auto?", value=False)
        if robo_auto_climb == True:
            robo_auto_level = st.slider("What level climb?", min_value=1, max_value=3)
        elif robo_auto_climb == False:
            robo_auto_level = 0

        st.divider()
        st.subheader("Tele-op!")

        robo_scored = st.toggle("Did robot score fuel?", value=True)
        if robo_scored == True:
            robo_shooter_type = st.multiselect("Shooter type: ", shooter_types, max_selections=2)
            robo_hopper_size = st.select_slider("Hopper capacity: ", ["Small (<30)", "Medium (31-60)", "Large (>61)"], value="Medium (31-60)")
            robo_accuracy = st.slider("Robot accuracy: ", min_value=1, max_value=100, value=80)
            robo_cycle_time = st.select_slider("Robot cycle time: ", ["Extremely Slow", "Below Average", "Average", "Above Average", "Super Fast"], value="Average")
            robo_throughput = st.select_slider("Shooting speed: ", ["Extremely Slow", "Below Average", "Average", "Above Average", "Super Fast"], value="Average")
        elif robo_scored == False:
            robo_shooter_type = "N/A"
            robo_hopper_size = "N/A"
            robo_accuracy = 0
            robo_throughput = "N/A"

        robo_driving = st.select_slider("How fluid is their driving?", ["Not real sure what they're doing", "Mechanical failure that hinders drive performance", "Could be better", "Average", "Above Average", "Couldn't be better"], value="Average")

        robo_intake = st.multiselect("How do they intake?", ["Floor", "Outpost/Human Player", "Both"], max_selections=2)
        if "Floor" in robo_intake:
            robo_intake_rating = st.select_slider("How's the intake?", ["There's an intake?", "Jammed several times", "Average", "Above Average", "Awesome!"], value="Average")
        if "Floor" not in robo_intake:
            robo_intake_rating = "Can't intake from floor"

        robo_do_when_inactive = st.multiselect("When the hub is inactive, what do they do? (Can select more that one)", ["Nothing", "Defense", "Clear opposing alliances fuel", "Pass/Collect fuel"])

        robo_sotm = st.toggle("Shoot on the move?")
        robo_trench = st.toggle("Did the robot drive under the trench?", value=True)
        robo_bump = st.toggle("Did the robot drive over the bump?", value=True)

        if robo_trench == True and robo_bump == True:
            robo_prefered_travel = st.multiselect("Prefered method of travel: ", ["Trench", "Bump"])
        else:
            robo_prefered_travel = "Don't do both"

        robo_play_defense = st.toggle("Did they play defense?")
        if robo_play_defense:
            robo_defense_effeciency = st.select_slider("How effecient was their defense?", ["Hurt more than helped", "It's ok", "Great!", "Amazing!"])
        if not robo_play_defense:
            robo_defense_effeciency = "N/A"

        robo_had_defense = st.toggle("Did anyone play defense against them?")
        if robo_had_defense:
            robo_had_defense_rating = st.select_slider("How much did defense hurt them?", ["Wait, what defense?", "It kinda did", "Significantly hurt them", "Cost them the match"])
            robo_played_defense_on_team = st.text_input("Who played defense on them?")
        if not robo_had_defense:
            robo_had_defense_rating = "N/A"
            robo_played_defense_on_team = "N/A"

        robo_tele_climb = st.toggle("Climb in endgame?", value=False)
        if robo_tele_climb == True:
            robo_teleop_level = st.slider("What level climb?", min_value=1, max_value=3)
        elif robo_tele_climb == False:
            robo_teleop_level = 0

        robo_broke = st.toggle("Did the robot break?", value=False)
        if robo_broke == True:
            robo_broke_explanation = st.text_area("Why did the robot break? How did it affect them?")
        elif robo_broke == False:
            robo_broke_explanation = "Didn't break"

        robo_extra = st.text_area("Anything else we should know about this match?")
        



match_data_entered = None

# Only build the dictionary if a team is actively selected to prevent crashes
if st.session_state.selected_team_state:
    # Ensure team selection handles fallback formatting for lists safely
    team_clean = st.session_state.selected_team_state[0] if isinstance(st.session_state.selected_team_state, list) and st.session_state.selected_team_state else "Unknown"
    
    match_data_entered = {
        "Scouter Name": scouter_name,
        "Team": team_clean,
        "Qual Number": qualMatch,
        "Auto Location": starting_auto[0] if starting_auto else "Not entered",
        "Center Intake": center_intake,
        "Center Auto Scored": center_shoot,
        "Neutral Auto Passes": neutral_passes,
        "Robot Auto Climb": robo_auto_climb,
        "Robot Auto Climb Level": robo_auto_level,
        "Robot Has Scored Fuel": robo_scored,
        "Robot Shooter Type": robo_shooter_type[0] if robo_shooter_type else "Not entered",
        "Robot Hopper Size": robo_hopper_size,
        "Robot Accuracy": robo_accuracy,
        "Robot Throughput": robo_throughput,
        "Robot Cycle Time": robo_cycle_time,
        "Robot Driving Rating": robo_driving,
        "Robot Intake": robo_intake[0] if robo_intake else "Not entered",
        "Robot Intake Rating": robo_intake_rating,
        "Robot Does When Inactive": ", ".join(robo_do_when_inactive) if robo_do_when_inactive else "Not entered",
        "Robot Shoot On The Move": robo_sotm,
        "Robot Trench": robo_trench,
        "Robot Bump": robo_bump,
        "Robot Prefered Travel Path": robo_prefered_travel,
        "Robot Played Defense": robo_play_defense,
        "Robot Defense Rating": robo_defense_effeciency,
        "Robot Had Defense": robo_had_defense,
        "Robot Defense Effect": robo_had_defense_rating,
        "Who Played Defense Against Team": robo_played_defense_on_team,
        "Robot Climbed In End Game": robo_tele_climb,
        "Robot Endgame Climb Level": robo_teleop_level,
        "Did Robot Break": robo_broke,
        "Robot Broke Explanation": robo_broke_explanation,
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
        st.toast("All match data has been deleted")
        st.rerun()

if st.session_state.all_scouting_data:

    #st.subheader(f"Currently Collected Matches ({len(st.session_state.all_scouting_data)})")
    
    downloadable_data = pd.DataFrame(st.session_state.all_scouting_data)
    st.dataframe(downloadable_data)

    convert_data = downloadable_data.to_csv(index=False, header=True).encode('utf-8')

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
            redErrorOff = max(0, round(100 - ((abs(realRedScore - RedPrediction) / realRedScore) * 100)))
            blueErrorOff = max(0, round(100 - ((abs(realBlueScore - BluePrediction) / realBlueScore) * 100)))

            col1_3, col2_3 = st.columns(2)
            with col1_3:
                st.error("Red Prediction Score: ")
                st.subheader(f"{redErrorOff}%")
            with col2_3:
                st.info("Blue Prediction Score: ")
                st.subheader(f"{blueErrorOff}%")
                
            percentageOff = (redErrorOff + blueErrorOff) / 2
            st.warning("Total Score (Lower Is Better): ")
            st.title(f"{percentageOff}%")
