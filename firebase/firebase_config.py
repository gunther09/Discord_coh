import firebase_admin
from firebase_admin import credentials, firestore

# Path to your service account key file
cred = credentials.Certificate("firebase/firebase_key.json")

# Initialize the Firebase app with the service account
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()
