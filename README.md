# S2T Experiment

A local tool to download, transcribe, and search YouTube videos using `yt-dlp`, `faster-whisper`, and `ChromaDB`.
The transcription language is configurable per run (defaults to auto-detection if not specified).

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

All commands are run through `main.py`. Add `-v` before any subcommand for debug logging.

### Download audio from a YouTube video

```bash
uv run main.py download <url> [-o dir]
```

### Transcribe a WAV file

```bash
uv run main.py transcribe <file> [--language XX]
```

### Search stored transcripts

```bash
uv run main.py search "query" [-n N] [--video-id ID]
```

### Full pipeline (download → transcribe → store)

```bash
uv run main.py pipeline <url> [--language XX]
```

## Project Structure

- `main.py`: CLI entry point and orchestrator (argparse + rich).
- `src/downloader.py`: Handles media downloading via yt-dlp.
- `src/transcriber.py`: Handles audio transcription via faster-whisper.
- `src/vector_store.py`: Handles vector storage and semantic search via ChromaDB.
