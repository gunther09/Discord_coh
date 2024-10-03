import firebase_admin
from firebase_admin import credentials, firestore
import firebase_config  # Importiert die Firebase-Konfiguration

# Funktion zum Abrufen und Anzeigen der Spielerdaten aus Firestore
def fetch_and_display_data():
    # Abrufen der Spielersammlung
    players_ref = firebase_config.db.collection('players')
    docs = players_ref.stream()

    # Anzeigen der Daten
    for doc in docs:
        print(f'{doc.id} => {doc.to_dict()}')

if __name__ == "__main__":
    fetch_and_display_data()
