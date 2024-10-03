import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred = credentials.Certificate("firebase/firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Fetch and print structure of a collection
def fetch_collection_structure(collection_ref, indent=0):
    docs = collection_ref.stream()
    structure = {}
    for doc in docs:
        structure[doc.id] = {
            'fields': list(doc.to_dict().keys()),
            'subcollections': {}
        }
        subcollections = doc.reference.collections()
        for subcollection in subcollections:
            structure[doc.id]['subcollections'][subcollection.id] = fetch_collection_structure(subcollection, indent + 2)
    return structure

# Print structure in a readable format
def print_structure(structure, indent=0):
    indent_str = ' ' * indent
    for doc_id, content in structure.items():
        print(f"{indent_str}Document ID: {doc_id}")
        print(f"{indent_str}  Fields: {', '.join(content['fields'])}")
        if content['subcollections']:
            print(f"{indent_str}  Subcollections:")
            print_structure(content['subcollections'], indent + 2)

# Fetch and print structure of the entire Firestore database
def fetch_database_structure():
    collections = db.collections()
    db_structure = {}
    for collection in collections:
        db_structure[collection.id] = fetch_collection_structure(collection)
    return db_structure

def print_database_structure():
    db_structure = fetch_database_structure()
    for collection_id, structure in db_structure.items():
        print(f"Collection: {collection_id}")
        print_structure(structure, 2)
        print("\n")

# Run the function to print the database structure
print_database_structure()
