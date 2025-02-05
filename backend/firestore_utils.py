import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import secretmanager
import string
import json
import hashlib
import time
import random
from google.api_core import retry, exceptions

def generate_doc_id(input_str):
    timestamp = str(int(time.time()))  # Current timestamp
    random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=6))  # Random 6-char string
    return f"{timestamp}-{random_str}"

def setup_firestore():
    cred = credentials.Certificate("path/to/serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
    
def get_secret(secret_name):
    
    client = secretmanager.SecretManagerServiceClient()
    secret_path = f"projects/cloud-hackathon-venky/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(request={"name": secret_path})

    return response.payload.data.decode("UTF-8")

def add_document(db, collection_name, doc_id, data):

    doc_ref = db.collection(collection_name).document(doc_id)
    doc_ref.set(data)

    print("Doc added successfully!")


def update_document(db, collection_name, doc_id, updates):
    """
    Updates specific fields in an existing document.
    """
    doc_ref = db.collection(collection_name).document(doc_id)
    doc_ref.update(updates)
    print(f"Document '{doc_id}' in collection '{collection_name}' updated successfully.")

# Delete an Existing Document
def delete_document(db, collection_name, doc_id):
    """
    Deletes an existing document from a collection.
    """
    doc_ref = db.collection(collection_name).document(doc_id)
    doc_ref.delete()
    print(f"Document '{doc_id}' in collection '{collection_name}' deleted successfully.")

# List All Documents Based on a Matching Query
def list_documents_with_query(db, collection_name, field_name, operator, value):
    """
    Lists all documents in a collection that match a query.
    """
    query = db.collection(collection_name).where(field_name, operator, value)
    results = query.get()

    print(f"Documents in collection '{collection_name}' matching '{field_name} {operator} {value}':")
    for doc in results:
        print(f"{doc.id}: {doc.to_dict()}")


def update_conversation(db, convo_id, message):
    """Finds an existing conversation or creates a new one, then appends messages."""

    doc_ref = db.collection("conversations").document(convo_id)

    doc = doc_ref.get()

    print('heyyyy')
    if doc.exists:
        conversation = doc.to_dict().get("conversation", [])
        doc_ref.update({"conversation": conversation + [message]})  # 🔄 Update existing doc
    else:
        doc_ref.set({"conversation": [message]})  # 🆕 Create new doc if it doesn't exist

    return convo_id  # ✅ Return the same conversation ID
