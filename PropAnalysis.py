import random

from nba_api.stats.endpoints import ScoreboardV2, BoxScoreAdvancedV3, BoxScoreTraditionalV3
from datetime import datetime, timedelta
import pandas as pd
import time
import json


# NBA API requires specific headers to work
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://www.nba.com/",
    "Origin": "https://www.nba.com/",
}

# Get yesterday's date in NBA API format
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# Fetch games from yesterday
def get_games():
    try:
        print(f"Fetching games for {yesterday}...")
        scoreboard = ScoreboardV2(game_date=yesterday)
        games_df = scoreboard.get_data_frames()[0]

        if games_df.empty:
            print("⚠️ No games found for yesterday.")
            return []

        return games_df["GAME_ID"].tolist()

    except Exception as e:
        print(f"❌ Error fetching scoreboard data: {e}")
        return []

# Fetch box scores and merge advanced and traditional stats
def fetch_combined_stats(game_ids):
    all_games_df = []
    for game_id in game_ids:
        print(f"Fetching stats for game {game_id}...")

        # Fetch the Advanced stats
        box_score_advanced = BoxScoreAdvancedV3(game_id, headers=HEADERS)
        player_stats_advanced = box_score_advanced.player_stats
        player_stats_data_advanced = player_stats_advanced.data

        # Fetch the Traditional stats
        box_score_traditional = BoxScoreTraditionalV3(game_id, headers=HEADERS)
        player_stats_traditional = box_score_traditional.player_stats
        player_stats_data_traditional = player_stats_traditional.data

        # Check if advanced stats have 'headers' and 'data'
        if 'headers' in player_stats_data_advanced and 'data' in player_stats_data_advanced:
            headers_advanced = player_stats_data_advanced['headers']  # Advanced stat categories
            data_advanced = player_stats_data_advanced['data']  # Advanced player data
            df_advanced = pd.DataFrame(data_advanced, columns=headers_advanced)
        else:
            print(f"Error: Missing advanced stats for game {game_id}")
            continue

        # Check if traditional stats have 'headers' and 'data'
        if 'headers' in player_stats_data_traditional and 'data' in player_stats_data_traditional:
            headers_traditional = player_stats_data_traditional['headers']  # Traditional stat categories
            data_traditional = player_stats_data_traditional['data']  # Traditional player data
            df_traditional = pd.DataFrame(data_traditional, columns=headers_traditional)
        else:
            print(f"Error: Missing traditional stats for game {game_id}")
            continue

        # Merge Advanced and Traditional stats on 'personId' (or other unique player identifier)
        combined_df = pd.merge(df_advanced, df_traditional, how='left', on='personId', suffixes=('_advanced', '_traditional'))
        combined_df["GAME_ID"] = game_id  # Add game_id to the DataFrame for tracking purposes
        all_games_df.append(combined_df)

        time.sleep(random.uniform(1,5))  # Prevent rate limiting (adjust based on API limits)

    # Concatenate all game DataFrames into one large DataFrame
    final_combined_df = pd.concat(all_games_df, ignore_index=True)
    return final_combined_df


def process_player_team_stats_with_advanced(df):
    """
    Process the given DataFrame to extract and combine traditional and advanced stats.
    Keeps traditional team and player IDs, and all stats from both traditional and advanced stats.

    Args:
    df (pd.DataFrame): Input DataFrame containing both advanced and traditional box score data.

    Returns:
    pd.DataFrame: Processed DataFrame with relevant team and player information and all stats.
    """
    # Keep only the traditional stats for player and team IDs
    relevant_columns_traditional = [
        'gameId_traditional', 'teamId_traditional', 'teamCity_traditional', 'teamName_traditional',
        'personId', 'firstName_traditional', 'familyName_traditional', 'minutes_traditional',
        'fieldGoalsMade', 'fieldGoalsAttempted', 'fieldGoalsPercentage', 'threePointersMade',
        'threePointersAttempted', 'threePointersPercentage', 'freeThrowsMade', 'freeThrowsAttempted',
        'freeThrowsPercentage', 'reboundsOffensive', 'reboundsDefensive', 'reboundsTotal', 'assists',
        'steals', 'blocks', 'turnovers', 'points', 'plusMinusPoints'
    ]

    # Keep the advanced stats columns
    relevant_columns_advanced = [
        'estimatedOffensiveRating', 'offensiveRating', 'estimatedDefensiveRating', 'defensiveRating',
        'estimatedNetRating', 'netRating', 'assistPercentage', 'assistToTurnover', 'assistRatio',
        'offensiveReboundPercentage', 'defensiveReboundPercentage', 'reboundPercentage', 'turnoverRatio',
        'effectiveFieldGoalPercentage', 'trueShootingPercentage', 'usagePercentage', 'estimatedUsagePercentage',
        'estimatedPace', 'pace', 'pacePer40', 'possessions', 'PIE'
    ]

    # Filter the DataFrame to keep only relevant columns (traditional stats + advanced stats)
    df_traditional = df[relevant_columns_traditional]
    df_advanced = df[relevant_columns_advanced]

    # Rename the traditional columns to make them clear (optional)
    df_traditional = df_traditional.rename(columns={
        'gameId_traditional': 'GAME_ID',
        'teamId_traditional': 'TEAM_ID',
        'teamCity_traditional': 'TEAM_CITY',
        'teamName_traditional': 'TEAM_NAME',
        'personId': 'PLAYER_ID',
        'firstName_traditional': 'FIRST_NAME',
        'familyName_traditional': 'LAST_NAME',
        'minutes_traditional': 'MINUTES',
        'fieldGoalsMade': 'FGM',
        'fieldGoalsAttempted': 'FGA',
        'fieldGoalsPercentage': 'FG%',
        'threePointersMade': '3PM',
        'threePointersAttempted': '3PA',
        'threePointersPercentage': '3P%',
        'freeThrowsMade': 'FTM',
        'freeThrowsAttempted': 'FTA',
        'freeThrowsPercentage': 'FT%',
        'reboundsOffensive': 'OREB',
        'reboundsDefensive': 'DREB',
        'reboundsTotal': 'TREB',
        'assists': 'AST',
        'steals': 'STL',
        'blocks': 'BLK',
        'turnovers': 'TO',
        'points': 'PTS',
        'plusMinusPoints': '+/-'
    })

    # Combine traditional and advanced stats by concatenating them
    final_df = pd.concat([df_traditional, df_advanced], axis=1)

    return final_df

# Get game IDs
#game_ids = get_games()

#if not game_ids:
 #   print("❌ No games found, exiting...")
  #  exit()

#print(f"✅ Found {len(game_ids)} games.")

#Fetch and combine stats for all games
#game_day_df = fetch_combined_stats(game_ids)
#new_df = process_player_team_stats_with_advanced(game_day_df)

# Save the combined stats to a CSV file
#new_df.to_csv(f"NBA_stats_{yesterday}.csv", index=False)
#print(f"✅ Stats saved to NBA_stats_{yesterday}.csv")

with open('game_ids_cache.json', "r") as file:
    cached_data = json.load(file)

all_game_ids = cached_data["game_ids"]

season_df = fetch_combined_stats(all_game_ids)
finished_season = process_player_team_stats_with_advanced(season_df)
finished_season.to_csv('NBA_2022Games.csv')
