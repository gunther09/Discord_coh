import os
import requests
import pandas as pd
from io import StringIO
import time
from firebase.fetch_player_ids import fetch_player_ids
from players import PLAYER_PROFILE_IDS
import messages  # Import the messages module

async def fetch_all_data(ctx):
    player_ids = fetch_player_ids()
    if player_ids:
        await ctx.send(messages.FETCHED_PLAYER_IDS_SUCCESS)
    else:
        player_ids = PLAYER_PROFILE_IDS

    # URLs for the CSV export
    url_2v2 = f"https://coh3stats.com/api/playerExport?types=[\"2v2\"]&profileIDs={player_ids}"
    url_3v3 = f"https://coh3stats.com/api/playerExport?types=[\"3v3\"]&profileIDs={player_ids}"
    url_4v4 = f"https://coh3stats.com/api/playerExport?types=[\"4v4\"]&profileIDs={player_ids}"

    # Function to get data from the given URL
    async def fetch_csv_data(url, label, success_message):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/csv,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,text/plain',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Referer': 'https://coh3stats.com/',
            'Origin': 'https://coh3stats.com/'
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            await ctx.send(f"Failed to fetch {label} data: {response.status_code}")
            raise Exception(f"Failed to fetch {label} data: {response.status_code}")
        csv_data = response.content.decode('utf-8')
        await ctx.send(success_message)
        return pd.read_csv(StringIO(csv_data))

    # Fetch data for 2v2, 3v3, and 4v4
    try:
        data_2v2 = await fetch_csv_data(url_2v2, "2v2", messages.FETCHED_2V2_DATA_SUCCESS)
    except Exception as e:
        print(f"Error fetching 2v2 data: {e}")
        data_2v2 = pd.DataFrame()

    time.sleep(0.1)  # Pause 

    try:
        data_3v3 = await fetch_csv_data(url_3v3, "3v3", messages.FETCHED_3V3_DATA_SUCCESS)
    except Exception as e:
        print(f"Error fetching 3v3 data: {e}")
        data_3v3 = pd.DataFrame()

    time.sleep(0.1)  # Pause

    try:
        data_4v4 = await fetch_csv_data(url_4v4, "4v4", messages.FETCHED_4V4_DATA_SUCCESS)
    except Exception as e:
        print(f"Error fetching 4v4 data: {e}")
        data_4v4 = pd.DataFrame()  # Create an empty DataFrame if fetching fails

    return data_2v2, data_3v3, data_4v4
