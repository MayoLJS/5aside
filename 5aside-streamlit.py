import pandas as pd
import math
import random
from collections import defaultdict
import streamlit as st

####################################################
######### SETUP & PAGE CONFIG
####################################################
st.set_page_config(
    page_title='5aside Soccer',
    page_icon='⚽',
    layout='wide',
    initial_sidebar_state="expanded"
)

# Custom CSS for UI Polish (Light/Dark Mode Compatible)
st.markdown("""
<style>
    /* Add subtle styling to the primary button */
    div.stButton > button:first-child {
        font-weight: 600;
        font-size: 1.1rem;
        padding: 0.5rem 1rem;
        border-radius: 8px;
    }
    
    /* Clean up the dataframe headers */
    [data-testid="stDataFrame"] {
        border-radius: 8px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

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
        if not line.strip():
            continue # Skip empty lines
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

####################################################
######### SIDEBAR & INSTRUCTIONS
####################################################
with st.sidebar:
    st.title("⚽ 5-a-Side Settings")
    st.markdown("---")
    
    # Safely load images with error handling in case files are missing
    try:
        st.image('./img/ballers.jpeg', width=150)
    except:
        pass # Skip if image not found

    st.markdown("### 📋 Formatting Guide")
    st.info("""
    Use the format:  
    `Name - Position`
    
    **Accepted Positions:** 🏃‍♂️ **ATT** (Attacker)  
    🎯 **MID** (Midfielder)  
    🛡️ **DEF** (Defender)
    """)
    
    try:
        st.image('./img/Template.png', caption='Input Template', use_container_width=True)
    except:
        pass # Skip if image not found

####################################################
######### MAIN UI WORKSPACE
####################################################
st.title("⚽ 5-a-Side Team Generator")
st.markdown("Instantly build perfectly balanced soccer squads based on player positions.")

# --- INPUT SECTION (Card-Based Layout) ---
with st.container(border=True):
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📝 Player Roster")
        input_method = st.radio("Choose Input Method:", ["Manual Entry", "File Upload"], horizontal=True)
        
        if input_method == "Manual Entry":
            input_data = st.text_area("Enter your players below:", height=200, 
                                      placeholder="Tony - ATT\nMayo - DEF\nSarah - MID")
        else:
            uploaded_file = st.file_uploader("Upload a text file (.txt)", type=["txt"])
            input_data = uploaded_file.getvalue().decode("utf-8") if uploaded_file else ""

    with col2:
        st.markdown("### ⚙️ Constraints")
        num_teams = st.number_input("Number of Teams:", min_value=1, max_value=20, value=2, step=1)
        
        st.markdown("<br>", unsafe_allow_html=True) # visual spacing spacer
        
        # Action button to trigger the algorithm
        generate_btn = st.button("🚀 Generate Teams", type="primary", use_container_width=True)

# --- PROCESSING & OUTPUT SECTION ---
if generate_btn:
    if not input_data.strip():
        st.warning("⚠️ Please enter or upload some player data first.")
    else:
        players, errors = parse_player_input(input_data)

        if errors:
            st.error("🚨 Found errors in your roster:")
            for error in errors:
                st.write(f"- {error}")
        else:
            st.success(f"✅ Successfully loaded {len(players)} players!")
            st.markdown("---")
            
            try:
                # Run the backend logic
                teams = create_balanced_teams(players, num_teams)
                
                # Render Teams in a Dynamic Grid
                st.markdown("### 🏆 Your Balanced Squads")
                
                # Determine how many columns to use based on team count (max 3 wide)
                cols_per_row = min(len(teams), 3) 
                grid_cols = st.columns(cols_per_row)
                
                for i, (team_idx, members) in enumerate(teams.items()):
                    # Wrap each team in its own bordered card
                    target_col = grid_cols[i % cols_per_row]
                    
                    with target_col:
                        with st.container(border=True):
                            st.markdown(f"<h4 style='text-align: center;'>Team {team_idx}</h4>", unsafe_allow_html=True)
                            
                            df = pd.DataFrame(members, columns=['Name', 'Position'])
                            
                            # Polished dataframe rendering
                            st.dataframe(
                                df,
                                use_container_width=True,
                                hide_index=True, # Looks much cleaner without the row numbers
                                column_config={
                                    "Name": st.column_config.TextColumn("Player"),
                                    "Position": st.column_config.TextColumn("Pos")
                                }
                            )
            except Exception as e:
                st.error(f"An error occurred while generating teams: {e}")
