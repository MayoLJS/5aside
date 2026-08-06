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
                
                # List to hold data for the CSV export
                export_data = []
                
                for i, (team_idx, members) in enumerate(teams.items()):
                    target_col = grid_cols[i % cols_per_row]
                    
                    with target_col:
                        with st.container(border=True):
                            st.markdown(f"<h4 style='text-align: center;'>Team {team_idx}</h4>", unsafe_allow_html=True)
                            st.caption(f"👥 Players: {len(members)}")
                            
                            # Create DataFrame and instantly drop the Skill column so it stays hidden
                            df = pd.DataFrame(members)[['Name', 'Position']]
                            
                            st.dataframe(
                                df,
                                use_container_width=True,
                                hide_index=True,
                                column_config={
                                    "Name": st.column_config.TextColumn("Player"),
                                    "Position": st.column_config.TextColumn("Pos")
                                }
                            )
                            
                            # Append to our export data
                            for _, row in df.iterrows():
                                export_data.append({
                                    "Team": f"Team {team_idx}",
                                    "Player": row["Name"],
                                    "Position": row["Position"]
                                })
                
                st.markdown("---")
                
                # --- SNAPSHOT / EXPORT BUTTON ---
                export_df = pd.DataFrame(export_data)
                csv = export_df.to_csv(index=False).encode('utf-8')
                
                st.download_button(
                    label="📸 Download Squads (CSV)",
                    data=csv,
                    file_name="5aside_teams.csv",
                    mime="text/csv",
                    type="primary"
                )

            except Exception as e:
                st.error(f"An error occurred while generating teams: {e}")
