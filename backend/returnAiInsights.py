import argparse
import time
import google.generativeai as genai
import glob
import numpy as np
import os
import json
from google.cloud import storage

def get_ai_insights(video_path, csv_paths, language, is_team):
    genai.configure(api_key="AIzaSyAxlDjY7RTAfjWrzlEdnpuEFUiOUj9Pe54")
    video_file = genai.upload_file(video_path)

    while video_file.state.name == "PROCESSING":
        print('.', end='')
        time.sleep(5)
        video_file = genai.get_file(video_file.name)

    if video_file.state.name == "FAILED":
        raise ValueError(video_file.state.name)

    csv_files = [genai.upload_file(csv) for csv in csv_paths]

    prompt = f"""
    Using the data in the csv files and video, generate AI insights about {'the team' if is_team else 'the player'}.
    Provide strengths, weaknesses, and notable statistics in {language}.
    """
    print('Generating Insights.....')
    model = genai.GenerativeModel("gemini-1.5-flash")
    generated_response = model.generate_content([video_file, *csv_files, prompt])

    print(f'AI Insights: {generated_response.candidates[0].content.parts[0].text}')

    insights_obj = {
        'response': generated_response.candidates[0].content.parts[0].text 
    }

    with open("/tmp/insights.json", "w", encoding="utf-8") as file:
        json.dump(insights_obj, file, indent=4)

def upload_file_to_gcs(bucket_name, source_file_path, destination_blob_name):
    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_path)

    print(f"✅ Uploaded {source_file_path} to gs://{bucket_name}/{destination_blob_name}")
    blob.make_public() 
    return blob.public_url
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate AI Insights for MLB Highlights.")
    parser.add_argument("--player", type=str, help="Player name (if applicable)")
    parser.add_argument("--play", type=str, help="Type of play (e.g., defensive_plays, homeruns)")
    parser.add_argument("--language", type=str,required= True, default="english", help="Language for AI insights")
    parser.add_argument("--team", type=str, help="Team name (if applicable)")

    args = parser.parse_args()

    video_path = glob.glob("/tmp/*.mp4")
    choice = np.random.randint(0, len(video_path))
    
    csv_paths = glob.glob("/tmp/*.csv")

    get_ai_insights(video_path[choice], csv_paths, args.language, not args.player)

    bucket_name = 'homeruns-top-players'
    output_path = '/tmp/insights.json'
    destination_blob = "output/insights.json"

    insights_url = upload_file_to_gcs(bucket_name, output_path, destination_blob) 

    print(insights_url)
