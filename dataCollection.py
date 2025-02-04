import os
import json
import time
import random
import requests
import pandas as pd
from datetime import datetime, timedelta
from nba_api.stats.endpoints import ScoreboardV2, BoxScoreAdvancedV3, BoxScoreTraditionalV3
from requests.exceptions import Timeout

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json',
    'Connection': 'keep-alive',
}

CACHE_FILE = "game_ids_cache.json"

def save_game_ids_to_cache(game_ids):
    """Append the new game IDs to a local cache file."""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r") as file:
                cached_data = json.load(file)
            # Append new game IDs to the existing list
            cached_data["game_ids"].extend(game_ids)
        else:
            cached_data = {"game_ids": game_ids}

        # Save updated data back to the file
        with open(CACHE_FILE, "w") as file:
            json.dump(cached_data, file, indent=4)

        print(f"Game IDs saved to {CACHE_FILE}. Total games: {len(cached_data['game_ids'])}")

    except Exception as e:
        print(f"❌ Error saving game IDs to cache: {e}")


def fetch_with_retry(scoreboard, retries=5, delay=10):
    """Fetch data from the scoreboard endpoint with retry logic and increased delay."""
    for attempt in range(retries):
        try:
            # Fetch data from the API (this returns a list of DataFrames)
            games_df = scoreboard.get_data_frames()[0]  # Get the first DataFrame

            # Check if the response data is empty
            if games_df.empty:
                print("⚠️ Received empty response from the API.")
                return pd.DataFrame()

            return games_df  # Return the DataFrame with the games data
        except Timeout:
            print(f"❌ Timeout error fetching data (Attempt {attempt + 1}). Retrying...")
            if attempt < retries - 1:
                delay = random.uniform(10, 15)  # Randomized delay between retries
                print(f"Retrying in {delay:.2f} seconds...")
                time.sleep(delay)
            else:
                print("Max retries reached. Skipping this request.")
                return pd.DataFrame()
        except Exception as e:
            print(f"❌ Error fetching data (Attempt {attempt + 1}): {e}")
            if attempt < retries - 1:
                delay = random.uniform(10, 15)  # Randomized delay between retries
                print(f"Retrying in {delay:.2f} seconds...")
                time.sleep(delay)
            else:
                print("Max retries reached. Skipping this request.")
                return pd.DataFrame()  # Return empty dataframe if all retries fail

def get_games(start_date, end_date):
    try:
        # Convert start and end dates to datetime objects for iteration
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        # List to hold the game IDs
        all_game_ids = []

        # Iterate over the days between start and end date
        current_date = start_date
        while current_date <= end_date:
            current_date_str = current_date.strftime("%Y-%m-%d")
            print(f"Fetching games for {current_date_str}...")

            # Fetch games for the current date
            scoreboard = ScoreboardV2(game_date=current_date_str)
            games_df = fetch_with_retry(scoreboard)

            if not games_df.empty:
                # Filter and extract game IDs
                games_df['GAME_DATE_EST'] = pd.to_datetime(games_df['GAME_DATE_EST']).dt.date
                games_on_this_day = games_df[games_df['GAME_DATE_EST'] == current_date.date()]

                if not games_on_this_day.empty:
                    all_game_ids.extend(games_on_this_day["GAME_ID"].tolist())
                else:
                    print(f"⚠️ No games found for {current_date_str}.")
            else:
                print(f"❌ No valid data for {current_date_str}.")

            # Increment to the next day
            current_date += timedelta(days=1)

            # Add a delay between requests to avoid rate limiting
            time.sleep(random.uniform(3, 6))  # Randomized delay between 3 to 6 seconds

        # Save updated game IDs to the cache
        if all_game_ids:
            save_game_ids_to_cache(all_game_ids)

        # Return the collected game IDs
        return all_game_ids

    except Exception as e:
        print(f"❌ Error fetching scoreboard data: {e}")
        return []


#Calling the get Games Function
#games = get_games("2022-12-01", "2023-04-09")

