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
```

## Features

- Supports both regular YouTube URLs and YouTube Shorts
- Uses YouTube's official transcript API for fast and accurate transcriptions
- Generates concise summaries using Mistral AI's large language model
- Simple command-line interface
- Environment variable management for API keys

## Requirements

- Python 3.13 or higher
- FFmpeg (for audio processing)
- Mistral AI API key