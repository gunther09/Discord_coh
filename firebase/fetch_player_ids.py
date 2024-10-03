from . import firebase_config

def fetch_player_ids():
    try:
        db = firebase_config.db
        player_ids_ref = db.collection('players')
        docs = player_ids_ref.stream()
        player_ids = [int(doc.to_dict().get('relic_id')) for doc in docs if 'relic_id' in doc.to_dict()]
        return player_ids
    except Exception as e:
        print(f"Error fetching player IDs from Firebase: {e}")
        return None
