import argparse
import glob
import re
import os
import numpy as np
from google.cloud import storage
import json
from google.cloud import speech, translate_v2 as translate, texttospeech
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import concatenate_audioclips, AudioClip, CompositeAudioClip

def extract_audio(video_file, audio_file):
    video = VideoFileClip(video_file)
    audio = video.audio
    audio.write_audiofile(audio_file, codec="pcm_s16le")

def transcribe_audio(audio_uri):
    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(uri=audio_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="en-US",
        audio_channel_count=2
    )

    response = client.long_running_recognize(config=config, audio=audio).result(timeout=240)

    return " ".join([result.alternatives[0].transcript for result in response.results])

def translate_text(text, target_language_code):
    clientTranslate = translate.Client()
    return clientTranslate.translate(text, target_language=target_language_code)["translatedText"]

def convert_text_to_speech(text, target_language, output_audio):
    clientT2S = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(language_code=target_language, ssml_gender=texttospeech.SsmlVoiceGender.MALE)
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    response = clientT2S.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
    with open(output_audio, "wb") as out:
        out.write(response.audio_content)

def replace_audio(video_path, audio_path, output_path, offset):
    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path).with_start(offset)

    if audio_clip.duration > video_clip.duration:
        audio_clip = audio_clip.subclip(0, video_clip.duration)
    elif audio_clip.duration < video_clip.duration:
        silence = AudioClip(lambda t: [0], duration=(video_clip.duration - audio_clip.duration))
        audio_clip = concatenate_audioclips([audio_clip, silence])

    new_video = video_clip.with_audio(CompositeAudioClip([audio_clip]))
    temp_output_path = f"/tmp/{os.path.basename(output_path)}"  

    new_video.write_videofile(temp_output_path, temp_audiofile=audio_path, remove_temp=True)

def upload_file_to_gcs(bucket_name, source_file_path, destination_blob_name):
    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_path)
    
    print(f"✅ Uploaded {source_file_path} to gs://{bucket_name}/{destination_blob_name}")
    
    return blob.public_url

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Translate MLB video audio.")
    parser.add_argument("--player", type=str, help="Player name (if applicable)")
    parser.add_argument("--team", type=str, help="Team name (if applicable)")
    parser.add_argument("--play", type=str, help="Type of play")
    parser.add_argument("--language", type=str, required=True, help="Target language (e.g., es-ES)")

    args = parser.parse_args()

    with open("/tmp/target_language.json", "r", encoding="utf-8") as file:
        languages = json.load(file)
    
    with open("/tmp/target_language_code.json", "r", encoding="utf-8") as file:
        language_codes = json.load(file)

    if  args.player != None:
        video_path = glob.glob(f"/tmp/{args.player}*.mp4")
    else:
       video_path = glob.glob(f"/tmp/{args.team}*.mp4")
       print(video_path) 

    choice = np.random.randint(0, len(video_path))
    video_file = video_path[choice]
    match = re.search(r'/([^/]+)\.mp4$', video_file)

    if match:
        video_name = match.group(1)
    audio_file =f'/tmp/{video_name}_audio.wav'

    extract_audio(video_file, audio_file)

    bucket_name = 'homeruns-top-players'
    if args.play:
        destination_blob_name = f'{args.play}/{video_name}_audio.wav'
    else:
        destination_blob_name = f'team_highlights/{audio_file}'

    upload_file_to_gcs(bucket_name, audio_file, destination_blob_name)

    audio_uri = f'gs://{bucket_name}/{destination_blob_name}'
    transcript = transcribe_audio(audio_uri)
    target_language_code = language_codes[f'{args.language.lower()}']
    
    translated_text = translate_text(transcript, target_language_code)

    output_audio = f'/tmp/{video_name}_audio_{args.language.lower()}.mp3'
    target_language = languages[f'{args.language.lower()}']

    convert_text_to_speech(translated_text, target_language, output_audio)

    audio_path = f'{output_audio}'
    output_video_path = f'/tmp/{video_name}_{args.language.lower()}.mp4'
    offset = 4

    replace_audio(video_file, audio_path, output_video_path, offset)


    destination_video_blob = f"output/{video_name}_{args.language.lower()}.mp4"
    video_url = upload_file_to_gcs(bucket_name, output_video_path, destination_video_blob) 

    print(video_url)


