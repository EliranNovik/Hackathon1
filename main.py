import psycopg2
from nba_api.stats.static import players
from nba_api.live.nba.endpoints import scoreboard
from difflib import get_close_matches
from datetime import timezone
from dateutil import parser
from tabulate import tabulate
from fuzzywuzzy import process

def connect_db():
    try:
        connection = psycopg2.connect(
            database="nba_tool",
            user="postgres",
            password="",
            host="localhost",
            port="5432"
        )
        print("Connected to the database successfully.")
        return connection
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

def get_team_stats():
    try:
        connection = connect_db()
        cursor = connection.cursor()
        print("Connected to the database successfully.")

        while True:
            cursor.execute("SELECT abbreviation, full_name FROM NBATeams;")
            teams = cursor.fetchall()

            print("Available NBA Teams:")
            for team in teams:
                print(f"{team[0]}: {team[1]}")

            abbreviation = input("Enter the abbreviation of the team to view stats: ").upper()

            cursor.execute(
                "SELECT * FROM NBATeams WHERE abbreviation = %s;",
                (abbreviation,)
            )
            team = cursor.fetchone()

            if team:
                print("\nTeam Stats:")
                print(f"Team ID: {team[0]}")
                print(f"Abbreviation: {team[1]}")
                print(f"Nickname: {team[2]}")
                print(f"Year Founded: {team[3]}")
                print(f"City: {team[4]}")
                print(f"Full Name: {team[5]}")
                print(f"State: {team[6]}")
                print(f"Championship Years: {', '.join(map(str, team[7])) if team[7] else 'None'}")
            else:
                print("\nTeam not found. Please try again.")

            another = input("\nWould you like to view another team? (yes/no): ").lower()
            if another != 'yes':
                break

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Database connection closed.")


def search_player():
    connection = connect_db()
    if not connection:
        return

    cursor = connection.cursor()
    player_name = input("Enter player name to search: ").strip()

    cursor.execute("SELECT player_name FROM all_nba_players;")
    all_player_names = [row[0] for row in cursor.fetchall()]

    matches = get_close_matches(player_name, all_player_names, n=5, cutoff=0.6)

    if matches:
        print("\nDid you mean:")
        for i, match in enumerate(matches, 1):
            print(f"{i}: {match}")

        try:
            choice = int(input("Enter the number of the player to view stats: "))
            selected_player = matches[choice - 1]

            cursor.execute(
                "SELECT * FROM all_nba_players WHERE player_name = %s;",
                (selected_player,)
            )
            player_stats = cursor.fetchall()

            if player_stats:
                print("\nPlayer Stats:")
                for stat in player_stats:
                    print(stat)
            else:
                print("No stats found for the selected player.")

        except (ValueError, IndexError):
            print("Invalid choice.")
    else:
        print("No players found matching that name.")

    cursor.close()
    connection.close()

def get_player_suggestions(cursor, player_name):
    cursor.execute("SELECT DISTINCT player_name FROM all_nba_players;")
    all_player_names = [row[0] for row in cursor.fetchall()]
    matches = process.extract(player_name, all_player_names, limit=5)
    return matches

def select_player_from_suggestions(suggestions):
    print("No exact match found. Here are some suggestions:")
    for idx, (match, score) in enumerate(suggestions, start=1):
        print(f"{idx}: {match} (match score: {score})")
    
    while True:
        try:
            choice = int(input("Enter the number of the player you want to select: "))
            if 1 <= choice <= len(suggestions):
                return suggestions[choice - 1][0]
            else:
                print("Invalid choice. Please select a valid number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def compare_players():
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

        player1_name = input("Enter the first player's name: ")
        player2_name = input("Enter the second player's name: ")

        cursor.execute(
            """
            SELECT * FROM all_nba_players
            WHERE player_name ILIKE %s
            ORDER BY season_id;
            """,
            (f"%{player1_name}%",)
        )
        player1_stats = cursor.fetchall()

        if not player1_stats:
            suggestions = get_player_suggestions(cursor, player1_name)
            player1_name = select_player_from_suggestions(suggestions)
            cursor.execute(
                """
                SELECT * FROM all_nba_players
                WHERE player_name ILIKE %s
                ORDER BY season_id;
                """,
                (f"%{player1_name}%",)
            )
            player1_stats = cursor.fetchall()

        cursor.execute(
            """
            SELECT * FROM all_nba_players
            WHERE player_name ILIKE %s
            ORDER BY season_id;
            """,
            (f"%{player2_name}%",)
        )
        player2_stats = cursor.fetchall()

        if not player2_stats:
            suggestions = get_player_suggestions(cursor, player2_name)
            player2_name = select_player_from_suggestions(suggestions)
            cursor.execute(
                """
                SELECT * FROM all_nba_players
                WHERE player_name ILIKE %s
                ORDER BY season_id;
                """,
                (f"%{player2_name}%",)
            )
            player2_stats = cursor.fetchall()

        headers = ["Category", player1_name, player2_name]
        comparison_data = []
        for p1, p2 in zip(player1_stats, player2_stats):
            comparison_data.append(["Season", p1[2], p2[2]])  # Season
            comparison_data.append(["Team", p1[4], p2[4]])  # Team Abbreviation
            comparison_data.append(["Games Played", p1[5], p2[5]])  # GP
            comparison_data.append(["Minutes Per Game", p1[6], p2[6]])  # MIN
            comparison_data.append(["Points Per Game", p1[7], p2[7]])  # PPG
            comparison_data.append(["Rebounds Per Game", p1[8], p2[8]])  # RPG
            comparison_data.append(["Assists Per Game", p1[9], p2[9]])  # APG
            comparison_data.append(["Field Goal %", p1[10], p2[10]])  # FG%
            comparison_data.append(["Free Throw %", p1[11], p2[11]])  # FT%
            comparison_data.append(["Three Point %", p1[12], p2[12]])  # 3P%

        comparison_table = tabulate(
            comparison_data,
            headers=headers,
            tablefmt="grid"
        )
        print(comparison_table)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Database connection closed.")

def live_scoreboard():
    print("\nLive Scoreboard:")
    board = scoreboard.ScoreBoard()
    games = board.games.get_dict()

    for game in games:
        game_time = parser.parse(game["gameTimeUTC"]).replace(tzinfo=timezone.utc).astimezone(tz=None)
        print(f"{game['gameId']}: {game['awayTeam']['teamName']} vs. {game['homeTeam']['teamName']} @ {game_time}")

def main():
    while True:
        print("\nWelcome to the NBA Stats Tool!")
        print("1: Team Stats")
        print("2: Player Stats")
        print("3: Compare Players")
        print("4: Live Scoreboard")
        print("5: Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            get_team_stats()
        elif choice == "2":
            search_player()
        elif choice == "3":
            compare_players()
        elif choice == "4":
            live_scoreboard()
        elif choice == "5":
            print("Exiting the NBA Stats Tool. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
