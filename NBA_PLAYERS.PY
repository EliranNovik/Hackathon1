import json
import psycopg2

# Database connection
conn = psycopg2.connect(
    dbname="nba_tool",
    user="postgres",
    password="",  # Replace with your PostgreSQL password
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Load JSON data
with open("NBAPLAYERS.txt", "r") as file:
    players_data = json.load(file)

# Insert data into the database
for player in players_data:
    try:
        cursor.execute("""
            INSERT INTO NBA_PLAYERS (
                api_id, player_name, position, age, games, games_started, minutes_pg, 
                field_goals, field_attempts, field_percent, three_fg, three_attempts, 
                three_percent, two_fg, two_attempts, two_percent, effect_fg_percent, 
                ft, ft_attempts, ft_percent, offensive_rb, defensive_rb, total_rb, 
                assists, steals, blocks, turnovers, personal_fouls, points, team, 
                season, player_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (api_id) DO NOTHING;
        """, (
            player["id"], player["playerName"], player["position"], player["age"], 
            player["games"], player["gamesStarted"], player["minutesPg"], 
            player["fieldGoals"], player["fieldAttempts"], player["fieldPercent"], 
            player["threeFg"], player["threeAttempts"], player["threePercent"], 
            player["twoFg"], player["twoAttempts"], player["twoPercent"], 
            player["effectFgPercent"], player["ft"], player["ftAttempts"], 
            player["ftPercent"], player["offensiveRb"], player["defensiveRb"], 
            player["totalRb"], player["assists"], player["steals"], player["blocks"], 
            player["turnovers"], player["personalFouls"], player["points"], 
            player["team"], player["season"], player["playerId"]
        ))
    except Exception as e:
        print(f"Error inserting player {player['playerName']}: {e}")

# Commit changes and close the connection
conn.commit()
cursor.close()
conn.close()

print("Data inserted successfully.")
