
**Team Assignment App**

This Python-based application is designed to help users create balanced five-a-side soccer teams from a list of players and their positions. It utilizes **Streamlit** for an interactive web interface, making it easy to input data, generate teams, and export results.

---

**Features**

- Generates balanced teams based on predefined position ratios:
  - 1 Attacker (ATT)
  - 2 Midfielders (MID)
  - 2 Defenders (DEF)
- Handles random distribution of players to ensure fairness.
- Ensures teams adhere to the maximum size of 5 players.
- User-friendly functionalities:
  - Input player data in the format `Name - Position` (e.g., `Tony - ATT`).
  - Specify the desired number of teams.
  - View the generated teams directly in the app.


---

**Installation**

1. Clone the repository or download the project files.

2. Install the required dependencies:

```bash
pip install pandas streamlit
```

3. Run the Streamlit app:

```bash
streamlit run 5aside-streamlit.py
```

---

**How to Use**

1. Launch the app by running the command: `streamlit run app.py`.
2. Enter player data in the text area using the format: `Name - Position`. For example:

   ```
   Tony - ATT
   Mayo - DEF
   Jane - MID
   ```

3. Specify the number of teams you want to create.
4. View the generated teams displayed in the app.
5. Download the team assignments as an Excel file using the "Download Teams as Excel" button.

---

**Code Breakdown**

- **Libraries Used:**
  - **pandas**: For handling tabular data.
  - **math**: For rounding calculations.
  - **random**: To shuffle players for random distribution.
  - **defaultdict**: For streamlined dictionary operations.
  - **Streamlit**: For building an interactive web application.

- **Key Functions:**
  
  1. **parse_player_input:**
     - Parses input data into a list of (name, position) tuples.
     - Validates positions to ensure they are either ATT, MID, or DEF.
     - Returns a list of valid players and any formatting errors.

  2. **create_balanced_teams:**
     - Takes a list of players and the desired number of teams.
     - Balances teams based on predefined position ratios.
     - Distributes any leftover players evenly.


- **Streamlit Integration:**
  - Provides text areas for player input and team number selection.
  - Displays team assignments in a table format.

---

**Example Input and Output**

**Input**

Player Data:
```
Tony - ATT
Mayo - DEF
Jane - MID
Bob - ATT
Alice - MID
Chris - DEF
```
Number of Teams: 2

**Output** (Displayed in the app and available for download as an Excel file)

**Team 1**
| Name   | Position |
|--------|----------|
| Tony   | ATT      |
| Jane   | MID      |
| Chris  | DEF      |

**Team 2**
| Name   | Position |
|--------|----------|
| Bob    | ATT      |
| Alice  | MID      |
| Mayo   | DEF      |

---

**Error Handling**

- Warns users if invalid positions are entered (only `ATT`, `MID`, and `DEF` are allowed).
- Alerts users if the input format is incorrect (e.g., missing `-` or extra fields).
- Displays clear error messages for debugging.

---

**Contributing**

Contributions are welcome! If you'd like to improve this project, feel free to:

- Submit a pull request.
- Raise an issue to suggest a feature or report a bug.

---

**License**

This project is licensed under the MIT License.

---

**Contact**

For questions, feedback, or collaboration opportunities, feel free to reach out!
