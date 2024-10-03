import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred = credentials.Certificate("firebase/firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Fetch all documents from the 'game_results' collection
def fetch_all_game_results():
    try:
        game_results_ref = db.collection('game_results')
        docs = game_results_ref.stream()
        all_game_results = {doc.id: doc.to_dict() for doc in docs}
        return all_game_results
    except Exception as e:
        print(f"Error fetching game results: {e}")
        return None

def print_game_results(docs):
    if docs:
        for doc_id, data in docs.items():
            print(f"Document ID: {doc_id}")
            for key, value in data.items():
                print(f"  {key}: {value}")
            print("\n")
    else:
        print("No documents found or error occurred.")

# Fetch and print all documents from the 'game_results' collection
all_game_results = fetch_all_game_results()
print_game_results(all_game_results)
