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

def add_document(db, collection_name, doc_id, data):

    doc_ref = db.collection(collection_name).document(doc_id)
    doc_ref.set(data)

    print("Doc added successfully!")

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

    doc_ref = db.collection("conversations").document(convo_id)

    doc = doc_ref.get()
    if doc.exists:
        conversation = doc.to_dict().get("conversation", [])
        doc_ref.update({"conversation": conversation + [message]})  # 🔄 Update existing doc
    else:
        doc_ref.set({"conversation": [message]})  # 🆕 Create new doc if it doesn't exist

    return convo_id  # ✅ Return the same conversation ID
