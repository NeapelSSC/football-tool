import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Football Tool", layout="wide")

# -------------------------------
# CSS für Layout & Farben
# -------------------------------
st.markdown("""
<style>
/* Hintergrund der App */
.stApp { background-color: #0e1a2b; }

/* Überschriften / Text */
h1, h2, h3, h4, h5, h6, p, div { color: white; }

/* Tabs */
button[data-baseweb="tab"] {
    background-color: #1c2b3a;
    color: white;
    border-radius: 10px;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background-color: #0099FF;
}

/* Buttons */
.stButton>button {
    background-color: #0099FF;
    color: white;
    border-radius: 8px;
}

/* Dropdowns */
div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #000000 !important;
}
div[data-baseweb="select"] span {
    color: #000000 !important;
}
ul {
    background-color: #ffffff !important;
    color: #000000 !important;
}
li:hover {
    background-color: #e6e6e6 !important;
}
label {
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# CSV Funktionen
# -------------------------------

PLAYERS_CSV = "players.csv"
MATCHES_CSV = "matches.csv"

def load_players():
    if os.path.exists(PLAYERS_CSV):
        return pd.read_csv(PLAYERS_CSV)
    else:
        return pd.DataFrame(columns=["Name", "Alter", "Position", "Verein", "Marktwert"])

def save_player(name, age, position, club, market_value):
    df = load_players()
    new_row = pd.DataFrame([[name, age, position, club, market_value]],
                           columns=df.columns)
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(PLAYERS_CSV, index=False)

def load_matches():
    if os.path.exists(MATCHES_CSV):
        return pd.read_csv(MATCHES_CSV)
    else:
        return pd.DataFrame(columns=["Team A", "Team B", "Formation A", "Formation B", "MW A", "MW B"])

def save_match(team_a, team_b, form_a, form_b, mw_a, mw_b):
    df = load_matches()
    new_row = pd.DataFrame([[team_a, team_b, form_a, form_b, mw_a, mw_b]],
                           columns=df.columns)
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(MATCHES_CSV, index=False)

# -------------------------------
# Tabs
# -------------------------------
tabs = st.tabs([
    "Team",
    "Datenbank Spieler",
    "Datenbank Spielberichte",
    "Leistung",
    "Import"
])

# -------------------------------
# TEAM TAB
# -------------------------------
with tabs[0]:
    if "selected_player" not in st.session_state:
        st.session_state.selected_player = None

    df_players = load_players()
    napoli_players = df_players[df_players["Verein"] == "SSC Neapel"]

    if st.session_state.selected_player is not None:
        player = st.session_state.selected_player
        st.header(f"👤 {player['Name']}")
        st.write(f"Position: {player['Position']}")
        st.write(f"Alter: {player['Alter']}")
        st.write(f"Marktwert: {int(player['Marktwert']):,} €")
        if st.button("⬅ Zurück"):
            st.session_state.selected_player = None
    else:
        st.subheader("Kader SSC Neapel")
        cols = st.columns(4)
        for i, row in napoli_players.iterrows():
            with cols[i % 4]:
                st.markdown(f"""
                <div style="
                    background-color:#1c2b3a;
                    padding:15px;
                    border-radius:15px;
                    text-align:center;
                    margin-bottom:15px;
                ">
                    <h4>{row['Name']}</h4>
                    <p>{row['Position']}</p>
                    <p>{row['Alter']} Jahre</p>
                    <p><b>{int(row['Marktwert']):,} €</b></p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Profil {row['Name']}", key=row['Name']):
                    st.session_state.selected_player = row

# -------------------------------
# DATENBANK SPIELER
# -------------------------------
with tabs[1]:
    st.header("Spieler-Datenbank")
    df_players = load_players()
    clubs = ["Alle"] + sorted(df_players["Verein"].unique())
    positions = ["Alle"] + sorted(df_players["Position"].unique())

    selected_club = st.selectbox("Verein", clubs)
    selected_position = st.selectbox("Position", positions)

    filtered = df_players.copy()
    if selected_club != "Alle":
        filtered = filtered[filtered["Verein"] == selected_club]
    if selected_position != "Alle":
        filtered = filtered[filtered["Position"] == selected_position]

    grouped = filtered.groupby("Verein")

    for club, group in grouped:
        st.subheader(f"🏟️ {club}")
        total_value = group["Marktwert"].sum()
        avg_age = group["Alter"].mean()
        for _, p in group.iterrows():
            st.write(f"{p['Name']} | {p['Alter']} | {p['Position']} | {int(p['Marktwert']):,} €")
        st.write(f"Spieler: {len(group)} | Gesamtwert: {int(total_value):,} € | Ø Alter: {avg_age:.1f}")
        st.divider()

# -------------------------------
# SPIELBERICHTE
# -------------------------------
with tabs[2]:
    st.header("Spielberichte")
    df_matches = load_matches()
    for _, m in df_matches.iterrows():
        st.write(f"{m['Team A']} vs {m['Team B']} | {m['Formation A']} vs {m['Formation B']} | MW: {m['MW A']} - {m['MW B']}")

# -------------------------------
# LEISTUNG
# -------------------------------
with tabs[3]:
    st.header("Leistung")
    st.write("Coming soon...")

# -------------------------------
# IMPORT
# -------------------------------
with tabs[4]:
    st.header("Import")
    text_input = st.text_area("Daten einfügen")

    if st.button("Importieren"):
        lines = text_input.split("\n")
        for line in lines:
            line = line.strip()
            if "\t" in line:
                try:
                    parts = line.split("\t")
                    if len(parts) >= 6:
                        position, name, club, _, age, value = parts[:6]
                        age = int(age.replace(" Jahre", "").strip())
                        value = int(value.replace(" EUR", "").replace(".", "").strip())
                        save_player(name, age, position, club, value)
                except:
                    st.warning(f"Fehler: {line}")
        st.success("Import fertig!")

    st.subheader("CSV Download / Upload")
    if os.path.exists("players.csv"):
        with open("players.csv", "rb") as file:
            st.download_button(
                label="Spieler CSV herunterladen",
                data=file,
                file_name="players.csv",
                mime="text/csv"
            )

    uploaded_file = st.file_uploader("CSV hochladen", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        df.to_csv("players.csv", index=False)
        st.success("CSV geladen!")
