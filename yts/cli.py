#!/usr/bin/env python3
import argparse
import os
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import re
from datetime import datetime
import json
from enum import Enum

class OutputFormat(Enum):
    JSON = 'json'
    TEXT = 'txt'
    MARKDOWN = 'md'

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

def get_video_info(url):
    """Get video title and other metadata using yt-dlp."""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', ''),
                'channel': info.get('channel', ''),
                'upload_date': info.get('upload_date', '')
            }
    except Exception as e:
        print(f"Could not get video info: {e}")
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
            ChatMessage(role="system", content="You are a helpful assistant that creates concise summaries."),
            ChatMessage(role="user", content=f"Please provide a concise summary of the following text: {text}")
        ]
        
        chat_response = client.chat(
            model="mistral-large-latest",
            messages=messages,
        )
        
        return chat_response.choices[0].message.content
    except Exception as e:
        print(f"Error in getting summary: {e}")
        return None

def sanitize_filename(filename):
    """Remove invalid characters from filename."""
    # Remove or replace invalid characters
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)
    # Limit length to avoid too long filenames
    return sanitized[:100]

def format_text_output(video_info, transcript=None, summary=None):
    """Format output for text file."""
    lines = []
    lines.append("YouTube Video Transcription and Summary")
    lines.append("=" * 40)
    lines.append(f"Title: {video_info.get('title', 'N/A')}")
    lines.append(f"Channel: {video_info.get('channel', 'N/A')}")
    lines.append(f"Upload Date: {video_info.get('upload_date', 'N/A')}")
    lines.append(f"Video ID: {video_info.get('video_id', 'N/A')}")
    lines.append("=" * 40)
    
    if transcript:
        lines.append("\nTranscription:")
        lines.append("-" * 40)
        lines.append(transcript)
    
    if summary:
        lines.append("\nSummary:")
        lines.append("-" * 40)
        lines.append(summary)
    
    return '\n'.join(lines)

def format_markdown_output(video_info, transcript=None, summary=None):
    """Format output for markdown file."""
    lines = []
    lines.append(f"# {video_info.get('title', 'YouTube Video Transcription and Summary')}")
    lines.append("")
    lines.append("## Video Information")
    lines.append(f"- **Channel:** {video_info.get('channel', 'N/A')}")
    lines.append(f"- **Upload Date:** {video_info.get('upload_date', 'N/A')}")
    lines.append(f"- **Video ID:** {video_info.get('video_id', 'N/A')}")
    lines.append("")
    
    if transcript:
        lines.append("## Transcription")
        lines.append("```")
        lines.append(transcript)
        lines.append("```")
        lines.append("")
    
    if summary:
        lines.append("## Summary")
        lines.append(summary)
    
    return '\n'.join(lines)

def save_to_file(video_id, video_info, output_format, transcript=None, summary=None, output_dir=None):
    """Save transcript and/or summary to file."""
    if not output_dir:
        output_dir = os.getcwd()
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Add video_id to info for completeness
    video_info['video_id'] = video_id
    
    # Generate filename using video title
    title = video_info.get('title', video_id)
    safe_title = sanitize_filename(title)
    filename = f"{safe_title}_{timestamp}.{output_format.value}"
    filepath = os.path.join(output_dir, filename)
    
    # Prepare and save content based on format
    if output_format == OutputFormat.JSON:
        data = {
            "video_id": video_id,
            "title": video_info.get('title', ''),
            "channel": video_info.get('channel', ''),
            "upload_date": video_info.get('upload_date', ''),
            "timestamp": timestamp
        }
        if transcript:
            data["transcript"] = transcript
        if summary:
            data["summary"] = summary
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    elif output_format == OutputFormat.TEXT:
        content = format_text_output(video_info, transcript, summary)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    elif output_format == OutputFormat.MARKDOWN:
        content = format_markdown_output(video_info, transcript, summary)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return filepath

def main():
    parser = argparse.ArgumentParser(description='YouTube Transcription and Summary Tool')
    parser.add_argument('url', help='YouTube video URL')
    parser.add_argument('-t', '--transcribe', action='store_true', help='Get video transcription')
    parser.add_argument('-s', '--summary', action='store_true', help='Get video summary')
    parser.add_argument('-o', '--output', help='Output directory for saving results')
    parser.add_argument('--save', action='store_true', help='Save results to file')
    parser.add_argument('--format', choices=['json', 'txt', 'md'], default='json',
                      help='Output format (json, txt, or md)')
    
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

    # Get video info if saving is requested
    video_info = None
    if args.save:
        video_info = get_video_info(args.url)
        if not video_info:
            print("Warning: Could not get video info, using video ID in filename")
            video_info = {'title': video_id}

    # Get transcript
    transcript = None
    summary = None
    
    if args.transcribe or args.summary:
        transcript = get_transcript(video_id)
        if not transcript:
            print("Failed to get transcript")
            return
        
        if args.transcribe:
            print("\nTranscription:")
            print("-" * 50)
            print(transcript)
    
    # Get summary if requested
    if args.summary:
        summary = get_summary(transcript)
        print("\nSummary:")
        print("-" * 50)
        if summary:
            print(summary)
        else:
            print("Failed to generate summary")
    
    # Save to file if requested
    if args.save and (transcript or summary):
        output_format = OutputFormat(args.format)
        filepath = save_to_file(video_id, video_info, output_format, transcript, summary, args.output)
        print(f"\nResults saved to: {filepath}")

if __name__ == "__main__":
    main()
