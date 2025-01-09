import pandas as pd
import math
import random
from collections import defaultdict
import streamlit as st
from io import BytesIO

####################################################
######### SETUP
####################################################
st.set_page_config(
    page_title='5aside Soccer',
    page_icon='⚽',
    layout='wide',
)

# Add logo (ensure the image exists in the directory or provide a valid path)
st.image('./img/ballers.jpeg', width=200)

# Display template image for guidance
st.image('./img/Template.png', caption='Use this template as a guide', width=200)

####################################################
######### FUNCTIONS
####################################################
# Helper function to validate player input
def parse_player_input(input_data):
    """Parses input data into a list of (name, position) tuples."""
    players = []
    errors = []
    lines = input_data.splitlines()
    for line in lines:
        parts = line.split('-')
        if len(parts) == 2:
            name = parts[0].strip()
            position = parts[1].strip().upper()
            if position in ['ATT', 'MID', 'DEF']:
                players.append((name, position))
            else:
                errors.append(f"Invalid position '{position}' for player '{name}'. Only 'ATT', 'MID', and 'DEF' are allowed.")
        else:
            errors.append(f"Invalid format: '{line}'. Use 'Name - Position'.")
    return players, errors

# Function to create teams with balanced ratios
def create_balanced_teams(players, num_teams):
    """Creates balanced teams based on player positions."""
    RATIO = {'ATT': 1, 'MID': 2, 'DEF': 2}  # Define position ratios
    TOTAL_RATIO = sum(RATIO.values())
    MAX_TEAM_SIZE = 5

    # Ensure there are enough players to form teams
    position_counts = {pos: len([p for p in players if p[1] == pos]) for pos in RATIO}
    total_players = len(players)
    
    min_teams = max(1, math.ceil(total_players / MAX_TEAM_SIZE))
    num_teams = min(num_teams, min_teams)

    team_size = total_players // num_teams
    extra_players = total_players % num_teams

    # Shuffle the players for random distribution
    random.shuffle(players)

    players_by_position = {pos: [p for p in players if p[1] == pos] for pos in RATIO}

    teams = defaultdict(list)
    for team_idx in range(1, num_teams + 1):
        for pos, count in RATIO.items():
            for _ in range(math.floor(count / TOTAL_RATIO * team_size)):
                if players_by_position[pos]:
                    teams[team_idx].append(players_by_position[pos].pop(0))

    remaining_players = []
    for pos, players_list in players_by_position.items():
        remaining_players.extend(players_list)

    # Distribute remaining players
    for idx, player in enumerate(remaining_players):
        team_idx = (idx % num_teams) + 1
        teams[team_idx].append(player)

    return teams

# Function to save teams to an Excel file
def save_teams_to_excel(teams):
    """Saves the teams to an Excel file and returns the file-like object."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for team_idx, members in teams.items():
            df = pd.DataFrame(members, columns=['Name', 'Position'])
            df.to_excel(writer, sheet_name=f'Team_{team_idx}', index=False)
    output.seek(0)
    return output

####################################################
######### STREAMLIT APP
####################################################
st.title("Five Aside Soccer ⚽")
st.write("You can **paste** or **upload a file** with player names and positions in the format `Name - Position` (e.g., `Tony - ATT`, `Mayo - DEF`).")

# Create two columns for input fields
col1, col2 = st.columns(2)

# Input for player data
with col1:
    input_method = st.radio("Input method:", ["Manual", "File Upload"])
    if input_method == "Manual":
        input_data = st.text_area("Enter player data (e.g., `Tony - ATT`):")
    else:
        uploaded_file = st.file_uploader("Upload a file containing player data:", type=["txt"])
        if uploaded_file is not None:
            input_data = uploaded_file.getvalue().decode("utf-8")
        else:
            input_data = ""

# Input for number of teams
with col2:
    num_teams = st.number_input("Enter the number of teams you want to create:", min_value=1, step=1)

if input_data:
    # Parse player input
    players, errors = parse_player_input(input_data)

    # Display current count of valid players
    st.write(f"**Number of players added:** {len(players)}")

    # Display errors if any
    if errors:
        for error in errors:
            st.warning(error)
    else:
        try:
            # Create teams
            teams = create_balanced_teams(players, num_teams)

            # Display teams
            for team_idx, members in teams.items():
                st.subheader(f"Team {team_idx}")
                df = pd.DataFrame(members, columns=['Name', 'Position'])
                st.dataframe(df, use_container_width=True)

            # Save to Excel and provide download button
            excel_data = save_teams_to_excel(teams)
            st.download_button(
                label="Download Teams as Excel",
                data=excel_data,
                file_name="teams_output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"An error occurred: {e}")
