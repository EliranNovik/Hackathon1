import requests
import psycopg2

def populate_teams_table():
    try:
        # Connect to the database
        connection = psycopg2.connect(
            database="nba_tool",
            user="postgres",
            password="",
            host="localhost",
            port="5432"
        )
        cursor = connection.cursor()
        print("Connected to the database successfully.")

        # Create the updated Teams table
        cursor.execute("""
            DROP TABLE IF EXISTS NBATeams;

            CREATE TABLE NBATeams (
                team_index_id INT PRIMARY KEY,
                team_index_abbreviation VARCHAR(10),
                team_index_nickname VARCHAR(50),
                team_index_year_founded INT,
                team_index_city VARCHAR(50),
                team_index_full_name VARCHAR(100),
                team_index_state VARCHAR(50),
                team_index_championship_year JSONB
            );
        """)
        connection.commit()
        print("Teams table updated successfully.")

        # API Request to fetch team data
        url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams"
        response = requests.get(url)
        data = response.json()

        # Extract and insert team data
        teams = data.get('sports', [])[0].get('leagues', [])[0].get('teams', [])
        if not teams:
            print("No teams data found in the response.")
        else:
            for team_data in teams:
                team = team_data.get('team', {})
                team_id = team.get('id')
                abbreviation = team.get('abbreviation')
                nickname = team.get('nickname')
                year_founded = team.get('yearFounded')
                city = team.get('location')
                full_name = team.get('displayName')
                state = team.get('state')
                championships = team.get('championships', [])

                # Insert data into the database
                cursor.execute("""
                    INSERT INTO Teams (
                        team_index_id, team_index_abbreviation, team_index_nickname, 
                        team_index_year_founded, team_index_city, team_index_full_name, 
                        team_index_state, team_index_championship_year
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (team_index_id) DO NOTHING;
                """, (
                    team_id, abbreviation, nickname, year_founded, city, 
                    full_name, state, championships
                ))

            connection.commit()
            print("Teams data inserted successfully.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Database connection closed.")

if __name__ == "__main__":
    populate_teams_table()
