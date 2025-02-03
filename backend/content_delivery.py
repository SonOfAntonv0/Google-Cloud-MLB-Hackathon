from genai_utils import get_params
import subprocess
from downloadMedia import *
from firestore_utils import add_document, generate_doc_id
from google.cloud import scheduler_v1, pubsub_v1
import json
import base64
from google.cloud import firestore 
import os

PROJECT_ID = "cloud-hackathon-venky"
TOPIC_NAME = "cron-topic"
REGION = "us-central1"

def process_content(params, pubsub_listener = False):

    db = firestore.Client()
    print(f'params received {params}')
    jobs_collection = 'jobs'
    data = {}
    video_url = ''
    insights_url = ''   

    if not pubsub_listener:
        data['username'] = params['name']
        data['email'] = params['email']
        data['delivery_type'] = params['delivery_type']
        doc_id = generate_doc_id(data['email'])

    try:
        if 'player' in params.keys():
            print('Downloading Player assets....')
            result = subprocess.run(
                ["python", "downloadMedia.py", "--player", f"{params['player']}", "--play", f"{params['play']}"],
                capture_output=True,
                text=True,
                check=True  # Raises an exception if the command fails
            )

            print('Translating video....')
            result = subprocess.run(
                ["python", "videoTranslation.py", "--player", f"{params['player']}", "--play", f"{params['play']}", "--language", f"{params['language']}"],
                capture_output=True,
                text=True,
                check=True  # Raises an exception if the command fails
            )

            output_lines = result.stdout.strip().split("\n")  # Split into lines
            video_url = output_lines[-1]  # Get the last printed line

            print('Generating Insights...')
            result = subprocess.run(
                ["python", "returnAiInsights.py", "--player", f"{params['player']}", "--play", f"{params['play']}", "--language", f"{params['language']}"],
                capture_output=True,
                text=True,
                check=True  # Raises an exception if the command fails
            )

            output_lines = result.stdout.strip().split("\n")  # Split into lines
            insights_url = output_lines[-1]  # Get the last printed line
        
        
        else:
            print('Downloading Team assets....')
            result = subprocess.run(
                ["python", "downloadMedia.py","--team", f"{params['team']}"],
                capture_output=True,
                text=True,
                check=True  # Raises an exception if the command fails
            )

            print('Translating video....')
            result = subprocess.run(
                ["python", "videoTranslation.py","--team", f"{params['team']}", "--language", f"{params['language']}"],
                capture_output=True,
                text=True,
                check=True  # Raises an exception if the command fails
            )

            output_lines = result.stdout.strip().split("\n")  # Split into lines
            video_url = output_lines[-1]  # Get the last printed line

            print('Generating Insights...')
            result = subprocess.run(
                ["python", "returnAiInsights.py","--team", f"{params['team']}", "--language", f"{params['language']}"],
                capture_output=True,
                text=True,
            )

            output_lines = result.stdout.strip().split("\n")  # Split into lines
            insights_url = output_lines[-1]  # Get the last printed line

        print(video_url)
        print(insights_url)
        
        data['video_url'] = video_url
        data['insights_url'] = insights_url

        if not pubsub_listener:
            add_document(db, jobs_collection, doc_id, data)
        return video_url, insights_url
    except subprocess.CalledProcessError as e:
        print("Error:", e.stderr)

def on_demand(params):
    video_url, insights_url = process_content(params)

    return video_url, insights_url 

def schedule_delivery(params):

    scheduler_client = scheduler_v1.CloudSchedulerClient()
    publisher = pubsub_v1.PublisherClient()

    # Pub/Sub Topic
    topic_path = publisher.topic_path(PROJECT_ID, TOPIC_NAME)

    # Generate a unique job name
    unique_id = generate_doc_id(params['name'])
    if 'player' in params.keys():
        job_name = f"projects/{PROJECT_ID}/locations/{REGION}/jobs/mlb-{params['player'].lower()}-{unique_id}"
    else:
       job_name = f"projects/{PROJECT_ID}/locations/{REGION}/jobs/mlb-{params['team'].lower()}-{unique_id}" 

    # Format schedule (convert "20:00" into cron format: "0 20 * * *")
    print(f'params in schedule {params}')
    time_parts = params["time"].split(":")
    cron_schedule = f"{time_parts[1]} {time_parts[0]} * * *"  # "MM HH * * *"
    if params["day of week"]:  # If weekly, add day of the week
        cron_schedule = f"{time_parts[1]} {time_parts[0]} * * {params['day of week']}"

    # Pub/Sub message payload
    payload = json.dumps(params).encode("utf-8")  # Convert JSON to bytes

    # Define the Cloud Scheduler job
    job = {
        "name": job_name,
        "pubsub_target": {
            "topic_name": topic_path,
            "data": base64.b64encode(payload).decode("utf-8"),  # Encode in base64
        },
        "schedule": cron_schedule,  # Cron schedule
        "time_zone": "America/Chicago",  # Timezone (e.g., "UTC-6")
    }
    print(job)

    try:
        # Check if job exists
        existing_job = scheduler_client.get_job(name=job_name)
        if existing_job:
            print(f"Job {job_name} already exists. Updating...")
            scheduler_client.update_job(job)
    except Exception as e:
        print(f"Creating a new job: {job_name}")
        scheduler_client.create_job(parent=f"projects/{PROJECT_ID}/locations/{REGION}", job=job)

    print(f"✅ Scheduled job for {params['player']} at {params['time']} {params['timezone']}!")


if __name__ == '__main__':
    params = {'player': 'Ohtani',
 'play': 'defensive_plays',
 'delivery_type': 'scheduled',
 'frequency': 'daily',
 'time': '20:00',
 'day of week': None,
 'timezone': 'UTC-6',
 'language': 'english'}
    
    schedule_delivery(params)
