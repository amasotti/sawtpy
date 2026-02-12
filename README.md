# S2T Experiment

A local tool to download, transcribe, and search YouTube videos using `yt-dlp`, `faster-whisper`, and `ChromaDB`.
The language can be configured in `src/transcriber.py` (default is Italian).

This is a learning project to experiment with these technologies, especially the whisper model, yt-dlp and the 
chroma vector database.

## Features

- **Download**: Extracts audio from YouTube videos (WAV format).
- **Transcribe**: Uses `faster-whisper` (large-v3 model) with Metal (MPS) support on macOS.
- **Search**: Stores transcripts in a local vector database (`ChromaDB`) for semantic search.

### Install FFmpeg

```bash
brew install ffmpeg
```

## Installation

1. Install `uv` ([python package manager](https://github.com/astral-sh/uv)) if you haven't already:
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2. Sync dependencies:
    ```bash
    uv sync
    ```

## Usage

### Downloader (Test)

```bash
uv run src/downloader.py <video_url> <output_path>
```

## Project Structure

- `src/downloader.py`: Handles media downloading.
- `src/transcriber.py`: Handles audio transcription.
- `src/vector_store.py`: Handles vector storage and search (TODO).
