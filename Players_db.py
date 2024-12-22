import requests
import psycopg2

# API details
url = "https://nba-api-free-data.p.rapidapi.com/nba-player-listing/v1/data"
querystring = {"id": "22"}
headers = {
    "x-rapidapi-key": "ae0694e32amshc4b1e2887309c8bp19703fjsnd35e15ab28f1",
    "x-rapidapi-host": "nba-api-free-data.p.rapidapi.com"
}

# Fetch data from the API
print("Fetching data from the API...")
response = requests.get(url, headers=headers, params=querystring)

if response.status_code != 200:
    print(f"Failed to fetch API data: {response.status_code} - {response.text}")
    exit()

players_data = response.json().get("athletes", [])
print(f"Number of players fetched: {len(players_data)}")

if not players_data:
    print("No player data found in API response.")
    exit()

# Database connection
try:
    conn = psycopg2.connect(
        dbname="nba_tool",
        user="postgres",
        password="",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()
    print("Database connection successful!")
except Exception as e:
    print(f"Database connection failed: {e}")
    exit()

# Insert players into the database
for player in players_data:
    try:
        api_id = player.get("id")
        full_name = player.get("fullName")
        first_name = player.get("firstName")
        last_name = player.get("lastName")
        display_name = player.get("displayName")
        height = player.get("displayHeight")
        weight = player.get("displayWeight")
        age = player.get("age")
        date_of_birth = player.get("dateOfBirth")[:10] if player.get("dateOfBirth") else None

        print(f"Inserting player: {full_name}")

        cursor.execute("""
            INSERT INTO Players (api_id, full_name, first_name, last_name, display_name, height, weight, age, date_of_birth)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (api_id) DO NOTHING;
        """, (api_id, full_name, first_name, last_name, display_name, height, weight, age, date_of_birth))
    except Exception as e:
        print(f"Error inserting player {full_name}: {e}")

# Commit and close
conn.commit()
print("Data committed to the database.")
cursor.close()
conn.close()
print("Database connection closed.")
