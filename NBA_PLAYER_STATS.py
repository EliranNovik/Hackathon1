from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats
import psycopg2
import time

def populate_players_table():
    try:
        # Database connection
        conn = psycopg2.connect(
            dbname="nba_tool",
            user="postgres",
            password="",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        print("Connected to the database successfully.")

        # Create the table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS all_nba_players (
                player_id INT,
                player_name TEXT,
                season_id TEXT,
                team_id INT,
                team_abbreviation TEXT,
                gp INT,
                min_per_game FLOAT,
                pts_per_game FLOAT,
                reb_per_game FLOAT,
                ast_per_game FLOAT,
                fg_pct FLOAT,
                ft_pct FLOAT,
                three_pt_pct FLOAT,
                PRIMARY KEY (player_id, season_id)
            );
        """)
        conn.commit()

        # Get all players
        all_players = players.get_players()

        # Loop through all players and fetch career stats
        for player in all_players:
            player_id = player['id']
            player_name = player['full_name']

            try:
                # Fetch career stats
                career = playercareerstats.PlayerCareerStats(player_id=player_id)
                career_stats = career.get_dict()

                # Insert each season's stats into the database
                for stat in career_stats['resultSets'][0]['rowSet']:
                    try:
                        cursor.execute("""
                            INSERT INTO all_nba_players (
                                player_id, player_name, season_id, team_id, team_abbreviation, gp,
                                min_per_game, pts_per_game, reb_per_game, ast_per_game, fg_pct,
                                ft_pct, three_pt_pct
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT DO NOTHING;
                        """, (
                            stat[0],  # player_id
                            player_name,
                            stat[1],  # season_id
                            stat[3],  # team_id
                            stat[4],  # team_abbreviation
                            stat[5],  # gp (games played)
                            stat[8],  # min_per_game
                            stat[26],  # pts_per_game
                            stat[20],  # reb_per_game
                            stat[21],  # ast_per_game
                            stat[9],  # fg_pct
                            stat[11],  # ft_pct
                            stat[10],  # three_pt_pct
                        ))
                    except Exception as e:
                        print(f"Error inserting stats for {player_name} (season: {stat[1]}): {e}")

                print(f"Stats for {player_name} inserted into the database.")
                
                # Rate limit management
                time.sleep(1)  # Adjust the delay as needed based on API rate limits

            except Exception as e:
                print(f"Could not fetch stats for {player_name}: {e}")

        # Commit changes
        conn.commit()
        print("All player stats have been imported into the database.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()
            print("Database connection closed.")
