from gevent import monkey, spawn, sleep, joinall
monkey.patch_all()

# Add this before creating the Flask app
import grpc.experimental.gevent
grpc.experimental.gevent.init_gevent()
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from genai_utils import get_llm_response, is_convo_done, get_params
from content_delivery import on_demand, schedule_delivery, process_content
from firestore_utils import update_conversation
from flask_socketio import SocketIO
import threading
import base64
import json
from google.cloud import firestore
from google.cloud import firestore
from google.api_core import retry
from notify import send_email
import os
#
app = Flask(__name__)
#CORS(app, origins="*", supports_credentials=True)
CORS(app, origins=["https://cloud-hackathon-venky.web.app","http://localhost:5173"], supports_credentials=True)
# socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet', logger=True, engineio_logger=True, transports=["websocket", "polling"], ping_timeout=600,  # Increase ping timeout
#     ping_interval=60)

socketio = SocketIO(
    app, 
    cors_allowed_origins=["https://cloud-hackathon-venky.web.app", "http://localhost:5173"], 
    async_mode='gevent',
    logger=True, 
    engineio_logger=True,
    transports=["websocket", "polling"],
    ping_timeout=600,
    ping_interval=60,
    message_queue='redis://' if os.environ.get('GAE_ENV', '').startswith('standard') else None
)

#load_dotenv()
class FirestoreClient:
    _instance = None
    
    @classmethod
    def get_client(cls):
        if cls._instance is None:
            cls._instance = firestore.Client()
        return cls._instance

    @staticmethod
    @retry.Retry(predicate=retry.if_exception_type(Exception))
    def retry_operation(operation, *args, **kwargs):
        return operation(*args, **kwargs)

@app.route("/")
def home():
    return "Flask App is Running!"

# Chat endpoint
@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        db = FirestoreClient.get_client()
        user_message = request.json.get("message", "")

        convo_id = request.json.get("convo_id", None)

        convo_id = update_conversation(db, convo_id, user_message)

        conversation_history = db.collection("conversations").document(convo_id).get().to_dict()["conversation"]

        print(f"🔥 Conversation ID {convo_id}: {conversation_history}")

        is_convo_done_flag = 'no'; 
        response = get_llm_response(conversation_history)

        print(f' Convo history \n \n {conversation_history} \n \n ')
        if "confirm" in user_message.lower():
            val = is_convo_done(conversation_history)
            is_convo_done_flag = val.split(' ')[0].lower()

        if is_convo_done_flag == 'yes':
            delivery_type = val.split(' ')[1].lower()

            # Store the greenlet so we can track it
            joinall([spawn(kickstart_job, convo_id, delivery_type)])


            # ✅ Immediately return response to the user
            return jsonify({"message": "Thanks for the info! Your request is being processed..."})

        return jsonify({
            "message": response
        })
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500


def kickstart_job(convo_id, delivery_type):
    sleep(0)
    db = FirestoreClient.get_client()
    doc_ref = db.collection("conversations").document(convo_id)
    doc = doc_ref.get()

    if not doc.exists:
        print(f"❌ Conversation ID {convo_id} not found in Firestore!")
        return

    params = get_params(doc.to_dict()["conversation"])

    if delivery_type == 'scheduled':
        schedule_delivery(params)
        socketio.emit("notification", {"message": "Scheduled Job has been created!!"})
    else:
        video_url, insights_url = on_demand(params)

        global_ref = db.collection("content-temp-store").document("0")
        global_ref.set({
            "video_url": video_url,
            "insights_url": insights_url
        })

        send_email(params['email'])
        socketio.emit("content_ready", {
            "videoUrl": video_url,
            "insightsUrl": insights_url
        })



# Content Theatre endpoint
@app.route("/api/content-theatre", methods=["GET"])
def content_theatre():
    db = FirestoreClient.get_client()
    doc_ref = db.collection("content-temp-store").document("0")
    doc = doc_ref.get()

    print(f'************ CONTENT THEATRE INVOKED ******* {doc}')
    if not doc.exists:
        return jsonify({"error": "No content available yet"}), 404

    data = doc.to_dict()
    video_url = data.get("video_url", "")
    insights_url = data.get("insights_url", "")

    if not video_url or not insights_url:
        return jsonify({"error": "Content not ready yet"}), 404

    return jsonify({"videoUrl": video_url, "insightsUrl": insights_url})

# Content Subscriptions endpoint
# @app.route("/api/subscriptions", methods=["GET"])
# def subscriptions():
#     # List all of user's current subscriptions;
#     # Clicking on 1 should have the ability to view it (in content theatre), disable , delete it
#     subscriptions = [
#         "Shohei Ohtani Home Runs",
#         "Top MLB Moments 2023",
#         "Dodgers vs. Yankees Highlights"
#     ]
#     return jsonify(subscriptions)

# @app.route("/api/subscriptions", methods=["GET"])
# def get_subscriptions():
#     # Mock data (replace with Firestore fetch)
#     subscriptions = [
#         {"id": "1", "name": "Shohei Ohtani Home Runs", "disabled": False},
#         {"id": "2", "name": "Top MLB Moments 2023", "disabled": False},
#         {"id": "3", "name": "Dodgers vs. Yankees Highlights", "disabled": True},
#     ]
#     return jsonify(subscriptions)

# @app.route("/api/subscriptions/<subscription_id>", methods=["DELETE"])
# def delete_subscription(subscription_id):
#     # Delete the subscription from Firestore
#     # Example: firestore.collection("subscriptions").document(subscription_id).delete()
#     return jsonify({"message": f"Subscription {subscription_id} deleted"})

# @app.route("/api/subscriptions/<subscription_id>/disable", methods=["POST"])
# def disable_subscription(subscription_id):
#     # Update the subscription to disable in Firestore
#     # Example: firestore.collection("subscriptions").document(subscription_id).update({"disabled": True})
#     return jsonify({"message": f"Subscription {subscription_id} disabled"})

@app.route("/pubsub", methods=["POST"])
def pubsub_listener():
    
    db = FirestoreClient.get_client()
    envelope = request.get_json()
    
    if not envelope:
        return "No Pub/Sub message received", 400

    pubsub_message = envelope.get("message", {})
    message_data = pubsub_message.get("data")

    if message_data:
        try:
            # Decode Base64-encoded message
            decoded_data = base64.b64decode(message_data).decode("utf-8")
            params = json.loads(decoded_data)  # Convert JSON string back to dictionary
            print(f"📩 Received Pub/Sub message: {params}")  # Debugging

            # Process the content
            video_url, insights_url = process_content(params, True)

            global_ref = db.collection("content-temp-store").document("0")
            global_ref.set({
                "video_url": video_url,
                "insights_url": insights_url
            })

            send_email(params['email'])
            # Emit content_ready event
            socketio.emit("content_ready", {
                "videoUrl": video_url,
                "insightsUrl": insights_url
            })

            return jsonify({"message": "Job executed successfully"}), 200
        except Exception as e:
            print(f"❌ Error decoding message: {str(e)}")
            return jsonify({"error": "Failed to decode message", "details": str(e)}), 500

    return jsonify({"error": "No valid data received"}), 400

@socketio.on("connect")
def handle_connect():
    print("✅ Client connected")

@socketio.on("disconnect")
def handle_disconnect():
    print("🔴 Client disconnected")

@socketio.on("content_ready")
def handle_content_ready(data):
    print(f"📩 Received content_ready event: {data}")


if __name__ == "__main__":
    print("🚀 Starting Flask server on port 8080")
    socketio.run(app, debug=True, host="0.0.0.0", port=8080)