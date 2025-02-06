from nba_api.stats.endpoints import leaguedashteamstats

from nba_api.stats.endpoints import BoxScoreTraditionalV3, BoxScoreAdvancedV3
import pandas as pd
import time
import random

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://www.nba.com/",
    "Origin": "https://www.nba.com/",
}

def fetch_team_stats(game_ids):
    all_games_df = []
    for game_id in game_ids:
        print(f"Fetching stats for game {game_id}...")

        # Fetch the Advanced stats
        box_score_advanced = BoxScoreAdvancedV3(game_id, headers=HEADERS)
        team_stats_advanced = box_score_advanced.team_stats
        team_stats_data_advanced = team_stats_advanced.data

        # Fetch the Traditional stats
        box_score_traditional = BoxScoreTraditionalV3(game_id, headers=HEADERS)
        team_stats_traditional = box_score_traditional.team_stats
        team_stats_data_traditional = team_stats_traditional.data

        # Check if advanced stats have 'headers' and 'data'
        if 'headers' in team_stats_data_advanced and 'data' in team_stats_data_advanced:
            headers_advanced = team_stats_data_advanced['headers']  # Advanced stat categories
            data_advanced = team_stats_data_advanced['data']  # Advanced player data
            df_advanced = pd.DataFrame(data_advanced, columns=headers_advanced)
        else:
            print(f"Error: Missing advanced stats for game {game_id}")
            continue

        # Check if traditional stats have 'headers' and 'data'
        if 'headers' in team_stats_data_traditional and 'data' in team_stats_data_traditional:
            headers_traditional = team_stats_data_traditional['headers']  # Traditional stat categories
            data_traditional = team_stats_data_traditional['data']  # Traditional player data
            df_traditional = pd.DataFrame(data_traditional, columns=headers_traditional)
        else:
            print(f"Error: Missing traditional stats for game {game_id}")
            continue

        # Merge Advanced and Traditional stats on 'personId' (or other unique player identifier)
        combined_df = pd.merge(df_advanced, df_traditional, how='left', on=['gameId', 'teamId'],
                               suffixes=('_advanced', '_traditional'))
        combined_df["GAME_ID"] = game_id  # Add game_id to the DataFrame for tracking purposes

        relevant_columns_traditional = [
            'gameId', 'teamId', 'teamCity_advanced', 'teamName_advanced',
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
        df_traditional = combined_df[relevant_columns_traditional]
        df_advanced = combined_df[relevant_columns_advanced]

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
        all_games_df.append(final_df)
        pd.concat(all_games_df, ignore_index=True).to_csv("cached_nba_stats.csv")

        time.sleep(1)  # Prevent rate limiting (adjust based on API limits)

    # Concatenate all game DataFrames into one large DataFrame
    final_combined_df = pd.concat(all_games_df, ignore_index=True)
    return final_combined_df


# Example Usage
game_ids = [f"002240{str(i).zfill(4)}" for i in range(400)]
all_team_stats_df = fetch_team_stats(game_ids[185:])
all_team_stats_df.to_csv('Team_NBA_2024')





