import requests
import pandas as pd
import time

def call_endpoint(url, max_level=3, include_new_player_attributes=False, retries=5, delay=2):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    for attempt in range(retries):
        resp = requests.get(url, headers=headers)

        # Print the response text for debugging
        print(f"Status Code: {resp.status_code}")
        print(f"Response Text: {resp.text[:500]}...")  # Show only first 500 chars

        # If rate-limited, wait and retry
        if resp.status_code == 429:
            print(f"Rate limit reached, retrying in {delay} seconds...")
            time.sleep(delay)
            delay *= 2  # Exponential backoff
            continue

        if resp.status_code != 200:
            print(f"Error: Received status code {resp.status_code}")
            return None

        try:
            data_json = resp.json()  # Convert response to JSON
        except requests.exceptions.JSONDecodeError:
            print("Error: Response is not valid JSON.")
            return None

        # Ensure 'data' and 'included' exist in JSON before accessing
        if 'data' not in data_json or 'included' not in data_json:
            print("Error: Expected keys ('data', 'included') not found in response.")
            return None

        data = pd.json_normalize(data_json['data'], max_level=max_level)
        included = pd.json_normalize(data_json['included'], max_level=max_level)

        if include_new_player_attributes:
            inc_cop = included[included['type'] == 'new_player'].copy().dropna(axis=1)
            data = pd.merge(
                data, inc_cop, how='left',
                left_on=['relationships.new_player.data.id', 'relationships.new_player.data.type'],
                right_on=['id', 'type'], suffixes=('', '_new_player')
            )

        return data

    print("Error: Failed to get a successful response after multiple retries.")
    return None


# Call the NFL endpoint with rate limiting and retries
nfl_url = 'https://partner-api.prizepicks.com/projections?league_id=9&per_page=1000'
nfl = call_endpoint(nfl_url, include_new_player_attributes=True)

if nfl is None:
    print("NFL_Failed")

if nfl is not None:
    nfl.to_csv("NFL_Prize_picks.csv")

# Call the NBA endpoint with rate limiting and retries
nba_url = 'https://partner-api.prizepicks.com/projections?league_id=7&per_page=1000'
nba = call_endpoint(nba_url, include_new_player_attributes=True)

if nba is None:
    print("NBA_Failed")

if nba is not None:
    nba.to_csv("NBA_Prize_picks.csv")
