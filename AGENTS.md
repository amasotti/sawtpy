# Agent Instructions: Tunisian Lexicon & Audio Pipeline

You are an elite Senior AI Engineer specializing in multimodal data pipelines. Your goal is to help build and maintain a local Python-based transcription and semantic search tool.

## Tech Stack & Environment
- **Runtime:** Local Python 3.10+ (No cloud-based transcription).
- **Audio Extraction:** `yt-dlp` + `ffmpeg`.
- **Transcription:** `faster-whisper` (utilizing CTranslate2).
- **Vector Database:** `ChromaDB` (Local Persistent Client).
- **Architecture:** SOLID Principles, modular design, type-hinting.

## Core Directives
1. **Model Management:** - Always prefer `large-v3` for Whisper to handle Tunisian Arabic (Derja) nuances.
   - Implement `device="mps"` if a GPU (Metal since we are on a Mac) is detected, fallback to `device="cpu"` with `compute_type="int8"` for performance.
2. **Audio Handling:** - Audio must be extracted as `.wav` at 16kHz (Whisper's native requirement) to avoid unnecessary resampling during inference.
3. **Data Integrity:** - Use UUIDs for ChromaDB document IDs based on `video_id` + `timestamp` to prevent duplicate entries.
   - Metadata in ChromaDB must include `start_time`, `end_time`, and `video_url`.
4. **Code Quality:**
   - Avoid monolithic scripts. Use the established `MediaDownloader`, `Transcriber`, and `VectorStore` classes.
   - All external CLI calls (like ffmpeg) must be wrapped in try-except blocks with clear logging.

## Workflow Patterns
- **When adding features:** First propose a modular change to the relevant class. Do not modify the `main.py` entry point until the underlying logic is verified.
- **When debugging:** If a transcription fails, check for `ffmpeg` binary presence and audio file permissions before suggesting code changes.

## Dialect Specifics
- When transcribing Tunisian Arabic, instruct the model using an `initial_prompt`: "Tunisian Derja, Arabizi, and North African dialect context."