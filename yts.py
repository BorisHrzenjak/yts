#!/usr/bin/env python3
import argparse
import os
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp
from mistralai.client import MistralClient
import re

def load_environment():
    load_dotenv()
    return {
        'MISTRAL_API_KEY': os.getenv('MISTRAL_API_KEY')
    }

def extract_video_id(url):
    """Extract YouTube video ID from URL."""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?]*)',
        r'(?:youtube\.com\/shorts\/)([^&\n?]*)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_transcript(video_id):
    """Get transcript using youtube_transcript_api."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return ' '.join([entry['text'] for entry in transcript])
    except Exception as e:
        print(f"Could not get transcript: {e}")
        return None

def get_summary(text):
    """Get summary using Mistral AI."""
    try:
        client = MistralClient(api_key=os.getenv('MISTRAL_API_KEY'))
        messages = [
            {"role": "system", "content": "You are a helpful assistant that creates concise summaries."},
            {"role": "user", "content": f"Please provide a concise summary of the following text: {text}"}
        ]
        
        chat_response = client.chat(
            model="mistral-large-latest",
            messages=messages,
        )
        
        return chat_response.choices[0].message.content
    except Exception as e:
        print(f"Error in getting summary: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='YouTube Transcription and Summary Tool')
    parser.add_argument('url', help='YouTube video URL')
    parser.add_argument('-t', '--transcribe', action='store_true', help='Get video transcription')
    parser.add_argument('-s', '--summary', action='store_true', help='Get video summary')
    
    args = parser.parse_args()
    
    # Load environment variables
    env_vars = load_environment()
    if not env_vars['MISTRAL_API_KEY'] and args.summary:
        print("Error: MISTRAL_API_KEY not found in .env file")
        return

    # Extract video ID
    video_id = extract_video_id(args.url)
    if not video_id:
        print("Error: Invalid YouTube URL")
        return

    # Get transcript
    transcript = get_transcript(video_id)
    if not transcript:
        print("Failed to get transcript")
        return

    # Handle commands
    if args.transcribe:
        print("\nTranscription:")
        print("-" * 50)
        print(transcript)
        
    if args.summary:
        print("\nSummary:")
        print("-" * 50)
        summary = get_summary(transcript)
        if summary:
            print(summary)
        else:
            print("Failed to generate summary")

if __name__ == "__main__":
    main()
