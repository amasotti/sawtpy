# S2T Experiment

A local tool to download, transcribe, and search YouTube videos using `yt-dlp`, `faster-whisper`, and `ChromaDB`.

## Features

- **Download**: Extracts audio from YouTube videos (WAV format).
- **Transcribe**: Uses `faster-whisper` (large-v3 model) with Metal (MPS) support on macOS.
- **Search**: Stores transcripts in a local vector database (`ChromaDB`) for semantic search.

## Requirements

- Python >= 3.10
- FFmpeg (must be installed and available in PATH)
- macOS (recommended for Metal support)

### Install FFmpeg

```bash
brew install ffmpeg
```

## Installation

1. Install `uv` if you haven't already:
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
uv run src/downloader.py <video_url>
```

## Project Structure

- `src/downloader.py`: Handles media downloading.
- `src/transcriber.py`: Handles audio transcription (TODO).
- `src/vector_store.py`: Handles vector storage and search (TODO).
