#!/usr/bin/env python3
"""
transcribe.py - A simple script to transcribe audio files in Ugandan languages using Sunbird API.
"""

import os
import sys
import requests
import json
import time
from pydub import AudioSegment
import argparse

def check_audio_length(audio_path):
    """Check if the audio file is less than 5 minutes in length."""
    try:
        audio = AudioSegment.from_file(audio_path)
        duration_seconds = len(audio) / 1000  # Convert milliseconds to seconds
        duration_minutes = duration_seconds / 60
        
        if duration_minutes > 5:
            print(f"Error: Audio file is {duration_minutes:.2f} minutes long. Maximum allowed length is 5 minutes.")
            return False
        return True
    except Exception as e:
        print(f"Error checking audio length: {e}")
        return False

def transcribe_audio(audio_path, language, access_token):
    """
    Transcribe audio file using Sunbird API.
    
    Args:
        audio_path: Path to the audio file
        language: Target language for transcription
        access_token: API access token for Sunbird
        
    Returns:
        Transcribed text or error message
    """
    # Language code mapping according to Sunbird API requirements
    language_codes = {
        "English": "eng",
        "Luganda": "lug",
        "Runyankole": "nyn",
        "Ateso": "teo",
        "Lugbara": "lgg",
        "Acholi": "ach"
    }
    
    if language not in language_codes:
        return f"Error: Language '{language}' is not supported."
    
    lang_code = language_codes[language]
    
    # Sunbird API endpoint for transcription
    url = "https://api.sunbird.ai/v2/transcribe"
    
    # Prepare headers with authorization token
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        # Check if file exists
        if not os.path.exists(audio_path):
            return f"Error: File '{audio_path}' does not exist."
            
        # Prepare the file for upload
        with open(audio_path, "rb") as audio_file:
            files = {
                "audio": (os.path.basename(audio_path), audio_file, "audio/mpeg")
            }
            
            # Prepare form data with language
            data = {
                "task": "speech2text",
                "parameters": json.dumps({
                    "language": lang_code
                })
            }
            
            print(f"Uploading audio file and requesting transcription in {language}...")
            
            # Submit transcription job
            response = requests.post(url, headers=headers, data=data, files=files)
            
            if response.status_code != 200:
                return f"Error: API request failed with status code {response.status_code}: {response.text}"
            
            # Parse the response to get the job ID
            response_data = response.json()
            job_id = response_data.get("id")
            
            if not job_id:
                return "Error: Failed to get job ID from API response."
            
            print(f"Transcription job submitted successfully. Job ID: {job_id}")
            print("Processing audio (this may take a moment)...")
            
            # Poll for results
            result_url = f"https://api.sunbird.ai/v2/jobs/{job_id}"
            
            max_attempts = 30  # Maximum number of polling attempts
            attempt = 0
            
            while attempt < max_attempts:
                attempt += 1
                
                # Wait before polling again
                time.sleep(5)
                
                # Check job status
                status_response = requests.get(result_url, headers=headers)
                
                if status_response.status_code != 200:
                    return f"Error checking job status: {status_response.text}"
                
                status_data = status_response.json()
                status = status_data.get("status")
                
                if status == "completed":
                    results = status_data.get("results", {})
                    transcript = results.get("transcription", "No transcription available")
                    return transcript
                elif status == "failed":
                    return f"Error: Transcription job failed. Reason: {status_data.get('error', 'Unknown error')}"
                
                print(f"Job status: {status}. Waiting for completion...")
            
            return "Error: Transcription timed out. Please try again later."
            
    except Exception as e:
        return f"Error during transcription: {str(e)}"

def main():
    """Main function to run the transcription script."""
    # Check if access token is provided as environment variable
    access_token = os.environ.get("SUNBIRD_API_TOKEN")
    
    # If no token in environment, try to get it from command line
    if not access_token:
        parser = argparse.ArgumentParser(description="Audio transcription using Sunbird API")
        parser.add_argument("--token", help="Sunbird API access token")
        args = parser.parse_args()
        access_token = args.token
    
    # If still no token, prompt the user
    if not access_token:
        print("Warning: No API token found in environment variables or command line arguments.")
        print("You can set the token by running: export SUNBIRD_API_TOKEN='your_token'")
        print("Or provide it when prompted.")
        print("\nPlease enter your Sunbird API access token:")
        access_token = input().strip()
    
    if not access_token:
        print("Error: No API token provided. Cannot proceed without authentication.")
        sys.exit(1)
    
    # Available languages
    languages = ["English", "Luganda", "Runyankole", "Ateso", "Lugbara", "Acholi"]
    
    print("Welcome to the Audio Transcription Tool for Ugandan Languages!")
    
    # Ask for audio file path
    print("\nPlease provide path to the audio file (Audio length less than 5 minutes):")
    audio_path = input().strip()
    
    # Validate audio file
    if not os.path.exists(audio_path):
        print(f"Error: File '{audio_path}' does not exist.")
        sys.exit(1)
    
    # Check audio length
    if not check_audio_length(audio_path):
        sys.exit(1)
    
    # Ask for target language
    print("\nPlease choose the target language: (one of English, Luganda, Runyankole, Ateso, Lugbara or Acholi):")
    target_language = input().strip().title()
    
    if target_language not in languages:
        print(f"Error: Unsupported language. Please choose one of: {', '.join(languages)}")
        sys.exit(1)
    
    # Perform transcription
    transcription = transcribe_audio(audio_path, target_language, access_token)
    
    print(f"\nAudio transcription text in {target_language}:")
    print(transcription)

if __name__ == "__main__":
    main()