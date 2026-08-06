import pandas as pd
import math
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
def parse_player_input(input_data):
    """Parses legacy text input data into a list of player dictionaries."""
    players = []
    errors = []
    lines = input_data.splitlines()
    for line in lines:
        if not line.strip():
            continue # Skip empty lines
        parts = line.split('-')
        if len(parts) >= 2:
            name = parts[0].strip()
            position = parts[1].strip().upper()
            skill = 3 # Default skill if not provided
            
            # Allow for optional skill metric in text upload (e.g. Tony - ATT - 5)
            if len(parts) == 3:
                try:
                    skill = int(parts[2].strip())
                except ValueError:
                    pass
            
            if position in ['ATT', 'MID', 'DEF']:
                players.append({"Name": name, "Position": position, "Skill": skill})
            else:
                errors.append(f"Invalid position '{position}' for player '{name}'. Only 'ATT', 'MID', and 'DEF' are allowed.")
        else:
            errors.append(f"Invalid format: '{line}'. Use 'Name - Position' or 'Name - Position - Skill'.")
    return players, errors

def create_balanced_teams(players, num_teams):
    """Creates teams balanced by both Position and Skill Rating."""
    RATIO = {'ATT': 1, 'MID': 2, 'DEF': 2}
    TOTAL_RATIO = sum(RATIO.values())
    MAX_TEAM_SIZE = 5

    total_players = len(players)
    min_teams = max(1, math.ceil(total_players / MAX_TEAM_SIZE))
    num_teams = min(num_teams, min_teams)
    team_size = total_players // num_teams

    # Sort all players by Skill (descending) to ensure highest rated get drafted first
    players = sorted(players, key=lambda x: x['Skill'], reverse=True)
    players_by_position = {pos: [p for p in players if p['Position'] == pos] for pos in RATIO}
    
    teams = defaultdict(list)

    # Distribute based on ratio using a snake draft to balance talent
    for pos, count in RATIO.items():
        pos_players = players_by_position[pos]
        needed_per_team = math.floor(count / TOTAL_RATIO * team_size)
        
        for _ in range(needed_per_team):
            # Snake draft: forwards 1 to N, then backwards N to 1
            for team_idx in range(1, num_teams + 1):
                if pos_players:
                    teams[team_idx].append(pos_players.pop(0))

    # Collect remaining players who didn't fit the perfect mathematical ratio
    remaining_players = []
    for pos_players in players_by_position.values():
        remaining_players.extend(pos_players)

    # Distribute remaining players (snake draft by skill)
    remaining_players = sorted(remaining_players, key=lambda x: x['Skill'], reverse=True)
    team_idx = 1
    direction = 1
    for player in remaining_players:
        teams[team_idx].append(player)
        team_idx += direction
        if team_idx > num_teams:
            team_idx = num_teams
            direction = -1
        elif team_idx < 1:
            team_idx = 1
            direction = 1

    return teams

####################################################
######### SIDEBAR & INSTRUCTIONS
####################################################
with st.sidebar:
    st.title("⚽ 5-a-Side Settings")
    st.markdown("---")
    
    try:
        st.image('./img/ballers.jpeg', width=150)
    except:
        pass

    st.markdown("### 📋 Text Upload Guide")
    st.info("""
    If you are uploading a text file rather than using the interactive table, use the format:  
    `Name - Position - Skill(1-5)`
    
    *Example:* `Tony - ATT - 5`
    
    **Accepted Positions:** 🏃‍♂️ **ATT** (Attacker)  
    🎯 **MID** (Midfielder)  
    🛡️ **DEF** (Defender)
    """)
    
    try:
        st.image('./img/Template.png', caption='Input Template', use_container_width=True)
    except:
        pass

####################################################
######### MAIN UI WORKSPACE
####################################################
st.title("⚽ 5-a-Side Team Generator")
st.markdown("Instantly build perfectly balanced soccer squads based on player positions and talent levels.")

# --- INPUT SECTION (Card-Based Layout) ---
with st.container(border=True):
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📝 Player Roster")
        input_method = st.radio("Choose Input Method:", ["Interactive Table", "File Upload"], horizontal=True)
        
        if input_method == "Interactive Table":
            st.caption("Click the '+' to add players. Select positions and rate skills from the dropdowns.")
            
            # Create a default starting grid
            default_roster = pd.DataFrame([
                {"Name": "Tony", "Position": "ATT", "Skill": 4},
                {"Name": "Mayo", "Position": "DEF", "Skill": 5},
                {"Name": "Sarah", "Position": "MID", "Skill": 3},
                {"Name": "", "Position": None, "Skill": 3} 
            ])
            
            # Render the interactive editor with column constraints
            edited_df = st.data_editor(
                default_roster,
                num_rows="dynamic",
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Name": st.column_config.TextColumn(
                        "Player Name", 
                        required=True, 
                        max_chars=50
                    ),
                    "Position": st.column_config.SelectboxColumn(
                        "Position",
                        options=["ATT", "MID", "DEF"],
                        required=True
                    ),
                    "Skill": st.column_config.NumberColumn(
                        "Skill Level (1-5)",
                        min_value=1,
                        max_value=5,
                        required=True,
                        format="%d ⭐"
                    )
                }
            )
            
            # Extract valid players from the table
            input_data = "" 
            players = []
            for _, row in edited_df.iterrows():
                if pd.notna(row['Name']) and str(row['Name']).strip() != "" and pd.notna(row['Position']):
                    players.append({
                        "Name": str(row['Name']).strip(),
                        "Position": str(row['Position']).strip(),
                        "Skill": int(row['Skill']) if pd.notna(row['Skill']) else 3
                    })
            
            errors = [] 
            
        else:
            uploaded_file = st.file_uploader("Upload a text file (.txt)", type=["txt"])
            input_data = uploaded_file.getvalue().decode("utf-8") if uploaded_file else ""
            
            if input_data.strip():
                players, errors = parse_player_input(input_data)
            else:
                players, errors = [], []

    with col2:
        st.markdown("### ⚙️ Constraints")
        num_teams = st.number_input("Number of Teams:", min_value=1, max_value=20, value=2, step=1)
        
        st.markdown("<br>", unsafe_allow_html=True)
        generate_btn = st.button("🚀 Generate Teams", type="primary", use_container_width=True)

# --- PROCESSING & OUTPUT SECTION ---
if generate_btn:
    if not players and not input_data.strip():
        st.warning("⚠️ Please enter or upload some player data first.")
    else:
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
                
                st.markdown("### 🏆 Your Balanced Squads")
                
                # Determine columns based on team count (max 3 wide)
                cols_per_row = min(len(teams), 3) 
                grid_cols = st.columns(cols_per_row)
                
                for i, (team_idx, members) in enumerate(teams.items()):
                    target_col = grid_cols[i % cols_per_row]
                    
                    with target_col:
                        with st.container(border=True):
                            st.markdown(f"<h4 style='text-align: center;'>Team {team_idx}</h4>", unsafe_allow_html=True)
                            
                            df = pd.DataFrame(members)
                            
                            st.dataframe(
                                df,
                                use_container_width=True,
                                hide_index=True,
                                column_config={
                                    "Name": st.column_config.TextColumn("Player"),
                                    "Position": st.column_config.TextColumn("Pos"),
                                    "Skill": st.column_config.NumberColumn("Skill", format="%d ⭐")
                                }
                            )
            except Exception as e:
                st.error(f"An error occurred while generating teams: {e}")
