# YouTube Transcription and Summary Tool (YTS)

A command-line tool to transcribe YouTube videos and generate summaries using Mistral AI.

## Installation

1. Clone the repository
2. Install the package:
```bash
uv pip install -e .
```

3. Create a `.env` file in the root directory and add your Mistral API key:
```
MISTRAL_API_KEY=your_api_key_here
```

## Usage

```bash
# Get transcription only
yts -t "https://youtube.com/watch?v=VIDEO_ID"

# Get summary only
yts -s "https://youtube.com/watch?v=VIDEO_ID"

# Get both transcription and summary
yts -t -s "https://youtube.com/watch?v=VIDEO_ID"

# Save results to file (in current directory)
yts -t -s --save "https://youtube.com/watch?v=VIDEO_ID"

# Save results to specific directory
yts -t -s --save -o path/to/directory "https://youtube.com/watch?v=VIDEO_ID"
```

## Features

- Supports both regular YouTube URLs and YouTube Shorts
- Uses YouTube's official transcript API for fast and accurate transcriptions
- Generates concise summaries using Mistral AI's large language model
- Simple command-line interface
- Environment variable management for API keys
- Save results to JSON files with video title and timestamps
- Includes video metadata (title, channel, upload date)

## Output Format

When saving to file, the results are stored in JSON format with the following structure:
```json
{
  "video_id": "VIDEO_ID",
  "title": "Video Title",
  "channel": "Channel Name",
  "upload_date": "YYYYMMDD",
  "timestamp": "YYYYMMDD_HHMMSS",
  "transcript": "Video transcription...",
  "summary": "Video summary..."
}
```

The file is named in the format: `Video Title_TIMESTAMP.json`

The filename is sanitized to remove invalid characters and limited to a reasonable length.

## Requirements

- Python 3.13 or higher
- FFmpeg (for audio processing)
- Mistral AI API key