import argparse
from google.cloud import storage
import fnmatch
import os

def list_files_in_gcs(bucket_name, prefix=None, pattern=None):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=prefix)
    return [blob.name for blob in blobs if not pattern or fnmatch.fnmatch(blob.name, pattern)]

def download_file_from_gcs(bucket_name, source_blob_name, local_destination):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(local_destination)
    print(f"Downloaded {source_blob_name} to {local_destination}.")

def download_multiple_files(bucket_name, blobs_list, local_directory):
    os.makedirs(local_directory, exist_ok=True)
    for blob_name in blobs_list:
        local_destination = os.path.join(local_directory, os.path.basename(blob_name))
        try:
            download_file_from_gcs(bucket_name, blob_name, local_destination)
        except Exception as e:
            print(f"Failed to download {blob_name}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download media from GCS for MLB Highlights.")
    parser.add_argument("--player", type=str, help="Player name (if applicable)")
    parser.add_argument("--play", type=str, help="Type of play (e.g., defensive_plays, homeruns)")
    parser.add_argument("--team", type=str, help="Team name (if applicable)")

    args = parser.parse_args()

    bucket_name = 'homeruns-top-players'
    files_to_download = []

    path_supported_language = list_files_in_gcs(bucket_name, pattern="*.json")
    if args.player:
        path_play = list_files_in_gcs(bucket_name, prefix=f"{args.play}/{args.player}_", pattern="*.mp4")
        path_player_stats = list_files_in_gcs(bucket_name, prefix=f"{args.player}/", pattern="*.csv")
        files_to_download = path_play + path_player_stats + path_supported_language
    elif args.team:
        path_team_data = list_files_in_gcs(bucket_name, prefix='team_data/', pattern='*.csv')
        path_video = list_files_in_gcs(bucket_name, prefix=f"team_highlights/{args.team}_", pattern="*.mp4")
        files_to_download = path_team_data + path_video + path_supported_language

    download_multiple_files(bucket_name, files_to_download, "/tmp")
