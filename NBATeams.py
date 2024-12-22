import json
import psycopg2

# File path
file_path = "NBATeams.json"

# Database connection
try:
    connection = psycopg2.connect(
        database="nba_tool",
        user="postgres",
        password="",
        host="localhost",
        port="5432"
    )
    cursor = connection.cursor()
    print("Connected to the database successfully.")

    # Read the JSON file
    with open(file_path, 'r') as file:
        teams_data = json.load(file)

    # Insert data into the NBATeams table
    for team in teams_data:
        try:
            cursor.execute("""
                INSERT INTO NBATeams (
                    team_id, abbreviation, nickname, year_founded, city, 
                    full_name, state, championship_years
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (team_id) DO NOTHING;
            """, (
                team['team_id'],
                team['abbreviation'],
                team['nickname'],
                team['year_founded'],
                team['city'],
                team['full_name'],
                team['state'],
                json.dumps(team['championship_years'])  # Convert list to JSON string
            ))
        except Exception as e:
            print(f"Skipping invalid team data: {team}")
            print(f"Error: {e}")

    connection.commit()
    print("All teams have been inserted into the database.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    if connection:
        cursor.close()
        connection.close()
        print("Database connection closed.")
