import pandas as pd
import math
from collections import defaultdict
import streamlit as st
from datetime import datetime

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
            continue 
        parts = line.split('-')
        if len(parts) >= 2:
            name = parts[0].strip()
            position = parts[1].strip().upper()
            skill = 3 
            
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

    total_players = len(players)
    if num_teams < 1:
        num_teams = 1
    
    team_size = max(1, total_players // num_teams)

    # Sort all players by Skill ASCENDING (1 is Best, 4 is Worst)
    players = sorted(players, key=lambda x: x['Skill'], reverse=False)
    players_by_position = {pos: [p for p in players if p['Position'] == pos] for pos in RATIO}
    
    teams = defaultdict(list)

    # 1. Distribute based on position ratio using a snake draft
    for pos, count in RATIO.items():
        pos_players = players_by_position[pos]
        needed_per_team = math.floor(count / TOTAL_RATIO * team_size)
        
        for _ in range(needed_per_team):
            team_order = list(range(1, num_teams + 1))
            for team_idx in team_order:
                if pos_players:
                    teams[team_idx].append(pos_players.pop(0))

    # 2. Collect remaining players 
    remaining_players = []
    for pos_players in players_by_position.values():
        remaining_players.extend(pos_players)

    # Sort remaining players globally by skill ascending
    remaining_players = sorted(remaining_players, key=lambda x: x['Skill'], reverse=False)

    # 3. Distribute remaining players via continuous snake draft
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
######### STATE MANAGEMENT (Default Roster)
####################################################
raw_default_roster = """Ismail - DEF - 2
Harry - MID - 2
Ayobamidele - DEF - 1
Bilal - DEF - 1
Segun - DEF - 4
Demo - ATT - 1
Jide - MID - 3
Big George - MID - 2
Joe - ATT - 2
King - DEF - 1
Uncle T - DEF - 3
Gbenga olusanya - MID - 2
Cj - ATT - 1
Msj - ATT - 4
Gozern - MID - 2
Hush - DEF - 2
Comm Tony - ATT - 3
Joboy - ATT - 1
Capt adeoye - ATT - 1
 Moh Afolabi - ATT - 1
Barka b - DEF - 1
Josh - DEF - 2
Mohammed - ATT - 3
Oscar - MID - 3
Gbenga - ATT - 2
Solaj - MID - 1
Kenny - MID - 1
Deolu - MID - 1
Stevo - ATT - 3
Dare - DEF - 4
Dave - ATT - 3
Dubem - DEF - 2
Hammed - DEF - 2
Stain - MID - 3
Supa - MID - 2
Dr Toyin - DEF - 4
Wisdom - DEF - 2
Timi - MID - 4
Eddy - DEF - 2
George - MID - 2
Victor - DEF - 1
Emperor - DEF - 3
Micheal Tblack - DEF - 2
Obi - MID - 2
Ola - MID - 2
Moe - DEF - 3
Dolat - DEF - 2
Shaffi - ATT - 3
Fola - DEF - 3
Lummy - ATT - 1
David - DEF - 4
Mr promise - DEF - 2
Hydaar - DEF - 2
Emmanuel - ATT - 1
FBI - MID - 2
Azodo - DEF - 2
Omar - MID - 1
KDB - DEF - 2
Ay - MID - 1
Nonso - DEF - 1
Halim - DEF - 2
Emy - DEF - 1
Vini - ATT - 3
Ezekiel - ATT - 4"""

# Initialize session state so we can clear/refresh it dynamically
if 'roster' not in st.session_state:
    parsed_defaults, _ = parse_player_input(raw_default_roster)
    df = pd.DataFrame(parsed_defaults)
    # Default is now False (Unticked)
    df["Available ✅"] = False 
    st.session_state.roster = df

def clear_roster():
    # Provide one empty row with the availability column when cleared (Unticked)
    st.session_state.roster = pd.DataFrame([{"Name": "", "Position": None, "Skill": 3, "Available ✅": False}])

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
    **Improvements made from the start:**
    1. **SaaS Dashboard UI:** Responsive card layouts.
    2. **Interactive Editor:** Pre-loaded 64 player database. 
    3. **Skill-Weighted Balancing:** 1-4 custom ranking draft.
    4. **Blind Output:** Player ratings hidden from generated cards.
    5. **Persistent Roster:** All players default to unticked. Toggle `Available ✅` week-to-week to build your squad!
    6. **Dynamic Team Sizing:** Automatically recommends number of teams based on available players (allows >5 per team for subs!).
    7. **Mobile Sequential Stacking:** UI perfectly stacks teams in order 1,2,3,4 on phones.
    8. **CSV Export:** Download timestamped results instantly.
    """)

####################################################
######### MAIN UI WORKSPACE
####################################################
st.title("⚽ 5-a-Side Team Generator")
st.markdown("Instantly build perfectly balanced soccer squads based on player positions and talent levels.")

# --- INPUT SECTION (Card-Based Layout) ---
with st.container(border=True):
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📝 Player Roster Database")
        input_method = st.radio("Choose Input Method:", ["Interactive Table", "File Upload"], horizontal=True, label_visibility="collapsed")
        
        if input_method == "Interactive Table":
            table_head_1, table_head_2 = st.columns([3, 1])
            with table_head_1:
                st.caption("Check 'Available ✅' for players showing up this week. Click '+' to add permanent new players!")
            with table_head_2:
                st.button("🗑️ Clear All", on_click=clear_roster, use_container_width=True)
            
            edited_df = st.data_editor(
                st.session_state.roster,
                num_rows="dynamic",
                hide_index=True,
                use_container_width=True,
                height=400,
                column_config={
                    # Checkbox defaults to False for new rows
                    "Available ✅": st.column_config.CheckboxColumn("Available ✅", default=False),
                    "Name": st.column_config.TextColumn("Player Name", required=True, max_chars=50),
                    "Position": st.column_config.SelectboxColumn("Position", options=["ATT", "MID", "DEF"], required=True),
                    "Skill": st.column_config.NumberColumn("Rank (1=Good, 4=Ok)", min_value=1, max_value=4, required=True, format="%d")
                }
            )
            
            st.session_state.roster = edited_df 
            
            input_data = "" 
            players = []
            for _, row in edited_df.iterrows():
                if pd.notna(row['Name']) and str(row['Name']).strip() != "" and pd.notna(row['Position']) and row.get('Available ✅', False):
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
        
        # --- DYNAMIC TEAM CALCULATION ---
        # Calculate optimal teams (Floor of players / 5). Minimum of 2 teams if people are playing.
        num_players = len(players)
        optimal_teams = max(2, num_players // 5) if num_players >= 8 else (1 if num_players > 0 else 2)
        
        num_teams = st.number_input("Number of Teams:", min_value=1, max_value=20, value=optimal_teams, step=1)
        
        st.markdown("<br>", unsafe_allow_html=True)
        generate_btn = st.button("🚀 Generate Teams", type="primary", use_container_width=True)

        # Show projection info based on the dynamic calculation
        if num_teams > 0 and num_players > 0:
            avg_size = num_players / num_teams
            st.info(f"**Selected Players:** {num_players}\n\n**Est. Team Size:** ~{math.floor(avg_size)} to {math.ceil(avg_size)} players per squad.")
        elif num_players == 0:
            st.info("Tick players in the roster to see team projections.")

# --- PROCESSING & OUTPUT SECTION ---
if generate_btn:
    if not players and not input_data.strip():
        st.warning("⚠️ Please select at least one available player from the roster.")
    else:
        if errors:
            st.error("🚨 Found errors in your roster:")
            for error in errors:
                st.write(f"- {error}")
        else:
            st.success(f"✅ Successfully loaded {len(players)} available players!")
            st.markdown("---")
            
            try:
                teams = create_balanced_teams(players, num_teams)
                
                st.markdown("### 🏆 Your Balanced Squads")
                
                # --- MOBILE SEQUENTIAL GRID FIX ---
                cols_per_row = 3
                team_items = list(teams.items())
                
                export_data = []
                
                for row_start in range(0, len(team_items), cols_per_row):
                    row_cols = st.columns(cols_per_row)
                    row_teams = team_items[row_start : row_start + cols_per_row]
                    
                    for col, (team_idx, members) in zip(row_cols, row_teams):
                        with col:
                            with st.container(border=True):
                                st.markdown(f"<h4 style='text-align: center;'>Team {team_idx}</h4>", unsafe_allow_html=True)
                                st.caption(f"👥 Players: {len(members)}")
                                
                                df = pd.DataFrame(members)[['Name', 'Position']] if members else pd.DataFrame(columns=['Name', 'Position'])
                                
                                st.dataframe(
                                    df,
                                    use_container_width=True,
                                    hide_index=True,
                                    column_config={
                                        "Name": st.column_config.TextColumn("Player"),
                                        "Position": st.column_config.TextColumn("Pos")
                                    }
                                )
                                
                                for _, row in df.iterrows():
                                    export_data.append({
                                        "Team": f"Team {team_idx}",
                                        "Player": row["Name"],
                                        "Position": row["Position"]
                                    })
                
                st.markdown("---")
                
                # --- SNAPSHOT / EXPORT BUTTON ---
                if export_data:
                    export_df = pd.DataFrame(export_data)
                    csv = export_df.to_csv(index=False).encode('utf-8')
                    
                    current_date = datetime.now().strftime("%Y-%m-%d")
                    filename = f"5aside_teams_{current_date}.csv"
                    
                    st.download_button(
                        label="📸 Download Squads (CSV)",
                        data=csv,
                        file_name=filename,
                        mime="text/csv",
                        type="primary"
                    )

            except Exception as e:
                st.error(f"An error occurred while generating teams: {e}")
