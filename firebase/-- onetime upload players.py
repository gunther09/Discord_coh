# upload_players_to_firestore.py

from firebase_config import db
from players import PLAYER_PROFILE_IDS

def upload_players():
    players_ref = db.collection('players')

    # Upload each player profile ID to Firestore
    for profile_id in PLAYER_PROFILE_IDS:
        player_data = {
            'steam_id': profile_id
        }
        players_ref.add(player_data)
        print(f"Uploaded player with Steam ID: {profile_id}")

if __name__ == "__main__":
    upload_players()
