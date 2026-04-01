import streamlit as st
import sqlite3
import re

st.set_page_config(page_title="Football Tool", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #0e1a2b; }
h1, h2, h3, h4, h5, h6, p, div { color: white; }
button[data-baseweb="tab"] {
    background-color: #1c2b3a;
    color: white;
    border-radius: 10px;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background-color: #0099FF;
}
.stButton>button {
    background-color: #0099FF;
    color: white;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

conn = sqlite3.connect("football.db", check_same_thread=False)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    position TEXT,
    club TEXT,
    market_value TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_a TEXT,
    team_b TEXT,
    formation_a TEXT,
    formation_b TEXT,
    market_value_a TEXT,
    market_value_b TEXT
)
''')

conn.commit()

tabs = st.tabs([
    "Team",
    "Datenbank Spieler",
    "Datenbank Spielberichte",
    "Leistung",
    "Import"
])

with tabs[0]:
    if "selected_player" not in st.session_state:
        st.session_state.selected_player = None

    squad = c.execute(
        "SELECT name, age, position, market_value FROM players WHERE club = 'SSC Neapel'"
    ).fetchall()

    if st.session_state.selected_player:
        player = st.session_state.selected_player
        st.header(f"👤 {player[0]}")
        st.write(f"Position: {player[2]}")
        st.write(f"Alter: {player[1]}")
        st.write(f"Marktwert: {int(player[3]):,} €")

        if st.button("⬅ Zurück"):
            st.session_state.selected_player = None
    else:
        st.subheader("Kader")
        cols = st.columns(4)

        for i, p in enumerate(squad):
            name, age, position, value = p

            with cols[i % 4]:
                st.markdown(f"""
                <div style="
                    background-color:#1c2b3a;
                    padding:15px;
                    border-radius:15px;
                    text-align:center;
                    margin-bottom:15px;
                ">
                    <h4>{name}</h4>
                    <p>{position}</p>
                    <p>{age} Jahre</p>
                    <p><b>{int(value):,} €</b></p>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"Profil {name}", key=name):
                    st.session_state.selected_player = p

with tabs[1]:
    st.header("Spieler-Datenbank")

    clubs = [row[0] for row in c.execute("SELECT DISTINCT club FROM players")]
    positions = [row[0] for row in c.execute("SELECT DISTINCT position FROM players")]

    selected_club = st.selectbox("Verein", ["Alle"] + clubs)
    selected_position = st.selectbox("Position", ["Alle"] + positions)

    query = "SELECT name, age, position, club, market_value FROM players WHERE 1=1"
    params = []

    if selected_club != "Alle":
        query += " AND club = ?"
        params.append(selected_club)

    if selected_position != "Alle":
        query += " AND position = ?"
        params.append(selected_position)

    players = c.execute(query, params).fetchall()

    grouped = {}

    for p in players:
        club = p[3]
        grouped.setdefault(club, []).append(p)

    for club, squad in grouped.items():
        st.subheader(f"🏟️ {club}")

        total_value = 0
        ages = []

        squad_sorted = sorted(squad, key=lambda x: int(x[4]), reverse=True)

        for p in squad_sorted:
            name, age, position, club, value = p
            total_value += int(value)
            ages.append(int(age))

            st.write(f"{name} | {age} | {position} | {int(value):,} €")

        avg_age = sum(ages) / len(ages) if ages else 0

        st.write(f"Spieler: {len(squad)}")
        st.write(f"Gesamtwert: {total_value:,} €")
        st.write(f"Ø Alter: {avg_age:.1f}")

        st.divider()

with tabs[2]:
    st.header("Spielberichte")

    matches = c.execute("SELECT team_a, team_b, formation_a, formation_b, market_value_a, market_value_b FROM matches").fetchall()

    for m in matches:
        st.write(f"{m[0]} vs {m[1]} | {m[2]} vs {m[3]} | MW: {m[4]} - {m[5]}")

with tabs[3]:
    st.header("Leistung")
    st.write("Coming soon...")

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

                    position = parts[0]
                    name = parts[1]
                    club = parts[2]
                    age = parts[4].replace(" Jahre", "")
                    value = parts[5].replace(" EUR", "").replace(".", "")

                    c.execute(
                        "INSERT INTO players (name, age, position, club, market_value) VALUES (?, ?, ?, ?, ?)",
                        (name, age, position, club, value)
                    )
                except:
                    st.warning(f"Fehler: {line}")

                continue

            if "," in line:
                parts = line.split(",")

                if len(parts) == 5:
                    c.execute("INSERT INTO players (name, age, position, club, market_value) VALUES (?, ?, ?, ?, ?)", parts)

                elif len(parts) == 6:
                    c.execute("INSERT INTO matches (team_a, team_b, formation_a, formation_b, market_value_a, market_value_b) VALUES (?, ?, ?, ?, ?, ?)", parts)

        conn.commit()
        st.success("Import fertig!")
