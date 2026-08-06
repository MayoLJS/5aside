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
    """Creates teams balanced by both Position and Skill Rating, ensuring equal average skill levels."""
    RATIO = {'ATT': 1, 'MID': 2, 'DEF': 2}
    TOTAL_RATIO = sum(RATIO.values())
    MAX_TEAM_SIZE = 5

    total_players = len(players)
    if num_teams < 1:
        num_teams = 1
    
    team_size = max(1, total_players // num_teams)

    # Sort all players by Skill (descending) to ensure highest rated get drafted first
    players = sorted(players, key=lambda x: x['Skill'], reverse=True)
    players_by_position = {pos: [p for p in players if p['Position'] == pos] for pos in RATIO}
    
    teams = defaultdict(list)

    # 1. Distribute based on position ratio using a snake draft partitioned by skill
    for pos, count in RATIO.items():
        pos_players = players_by_position[pos]
        needed_per_team = math.floor(count / TOTAL_RATIO * team_size)
        
        for _ in range(needed_per_team):
            team_order = list(range(1, num_teams + 1))
            for team_idx in team_order:
                if pos_players:
                    teams[team_idx].append(pos_players.pop(0))

    # 2. Collect remaining players who didn't fit the exact mathematical ratio
    remaining_players = []
    for pos_players in players_by_position.values():
        remaining_players.extend(pos_players)

    # Sort remaining players globally by skill descending
    remaining_players = sorted(remaining_players, key=lambda x: x['Skill'], reverse=True)

    # 3. Distribute remaining players via a continuous snake draft to tightly match team skill averages
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

    st.markdown("### 🚀 Changelog & Evolution")
    st.info("""
    **Here are all the improvements made from the start:**
    1. **SaaS Dashboard UI:** Overhauled the top-down script into a card-based layout with responsive grid outputs.
    2. **Interactive Data Editor:** Replaced raw text boxes with a spreadsheet table featuring dropdowns for positions (`ATT`, `MID`, `DEF`) and star ratings (`1-5 ⭐`).
    3. **Skill-Weighted Balancing:** Integrated a continuous snake-draft algorithm that ensures teams match tightly on overall average skill and tactical ratios.
    4. **Team Metrics & Summary:** Added live team player counts and average star ratings (`Avg Skill / 5.0`) to every generated squad card.
    5. **12-Player Simulation Ready:** Pre-loaded the interactive table with 12 players so you can instantly simulate 2 balanced teams out-of-the-box.
    """)

    st.markdown("### 📋 Text Upload Guide")
    st.markdown("""
    Format: `Name - Position - Skill(1-5)`  
    *Example:* `Tony - ATT - 5`  
    **Positions:** `ATT`, `MID`, `DEF`
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
            st.caption("Click '+' to add players. Pre-loaded with 12 players to simulate 2 balanced teams!")
            
            # Default starting grid pre-loaded with 12 players
            default_roster = pd.DataFrame([
                {"Name": "Tony", "Position": "ATT", "Skill": 4},
                {"Name": "Mayo", "Position": "DEF", "Skill": 5},
                {"Name": "Sarah", "Position": "MID", "Skill": 3},
                {"Name": "Alex", "Position": "ATT", "Skill": 3},
                {"Name": "David", "Position": "MID", "Skill": 4},
                {"Name": "John", "Position": "DEF", "Skill": 2},
                {"Name": "Emma", "Position": "MID", "Skill": 5},
                {"Name": "Chris", "Position": "ATT", "Skill": 2},
                {"Name": "Luke", "Position": "DEF", "Skill": 4},
                {"Name": "Sam", "Position": "MID", "Skill": 3},
                {"Name": "Marcus", "Position": "ATT", "Skill": 5},
                {"Name": "Kieran", "Position": "DEF", "Skill": 4}
            ])
            
            edited_df = st.data_editor(
                default_roster,
                num_rows="dynamic",
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Name": st.column_config.TextColumn("Player Name", required=True, max_chars=50),
                    "Position": st.column_config.SelectboxColumn("Position", options=["ATT", "MID", "DEF"], required=True),
                    "Skill": st.column_config.NumberColumn("Skill Level (1-5)", min_value=1, max_value=5, required=True, format="%d ⭐")
                }
            )
            
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
                teams = create_balanced_teams(players, num_teams)
                
                st.markdown("### 🏆 Your Balanced Squads")
                
                cols_per_row = min(len(teams), 3) 
                grid_cols = st.columns(cols_per_row)
                
                for i, (team_idx, members) in enumerate(teams.items()):
                    target_col = grid_cols[i % cols_per_row]
                    avg_skill = sum(m['Skill'] for m in members) / len(members) if members else 0
                    
                    with target_col:
                        with st.container(border=True):
                            st.markdown(f"<h4 style='text-align: center;'>Team {team_idx}</h4>", unsafe_allow_html=True)
                            st.caption(f"👥 Players: {len(members)} | ⭐ Avg Skill: {avg_skill:.2f} / 5.0")
                            
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
