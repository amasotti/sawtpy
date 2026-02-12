import argparse
import logging
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()
logger = logging.getLogger("s2t")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="s2t",
        description="Download, transcribe, and search YouTube videos locally.",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")
    sub = parser.add_subparsers(dest="command")

    # download
    d = sub.add_parser("download", help="Download audio from a YouTube video")
    d.add_argument("url", help="YouTube URL or video ID")
    d.add_argument("-o", "--output-dir", default="downloads", help="Output directory (default: downloads)")

    # transcribe
    t = sub.add_parser("transcribe", help="Transcribe an audio file")
    t.add_argument("file", help="Path to WAV audio file")
    t.add_argument("--language", default=None, help="Language code (e.g. en, ar, it). Omit for auto-detection")

    # search
    q = sub.add_parser("search", help="Search stored transcripts")
    q.add_argument("query", help="Search query")
    q.add_argument("-n", "--n-results", type=int, default=5, help="Number of results (default: 5)")
    q.add_argument("--video-id", default=None, help="Filter by video ID")

    # pipeline
    p = sub.add_parser("pipeline", help="Full pipeline: download → transcribe → store")
    p.add_argument("url", help="YouTube URL or video ID")
    p.add_argument("--language", default=None, help="Language code. Omit for auto-detection")
    p.add_argument("-o", "--output-dir", default="downloads", help="Output directory (default: downloads)")

    return parser


def cmd_download(args: argparse.Namespace) -> None:
    from src.downloader import MediaDownloader

    downloader = MediaDownloader(output_dir=args.output_dir)
    path = downloader.download_audio(args.url)
    if path:
        console.print(f"[green]Downloaded:[/green] {path}")
    else:
        console.print("[red]Download failed.[/red]")
        sys.exit(1)


def cmd_transcribe(args: argparse.Namespace) -> None:
    from src.transcriber import Transcriber

    transcriber = Transcriber()
    segments = transcriber.transcribe(args.file, language=args.language)

    table = Table(title="Transcription")
    table.add_column("Start", style="cyan", width=8)
    table.add_column("End", style="cyan", width=8)
    table.add_column("Text")
    for seg in segments:
        table.add_row(f"{seg['start']:.2f}", f"{seg['end']:.2f}", seg["text"])
    console.print(table)
    console.print(f"[green]{len(segments)} segments transcribed.[/green]")


def cmd_search(args: argparse.Namespace) -> None:
    from src.vector_store import VectorStore

    store = VectorStore()
    results = store.search(args.query, n_results=args.n_results, video_id=args.video_id)
    if not results:
        console.print("[yellow]No results found.[/yellow]")
        return

    table = Table(title=f"Search results for: {args.query}")
    table.add_column("Video", style="cyan", width=14)
    table.add_column("Time", style="green", width=16)
    table.add_column("Text")
    table.add_column("Dist", style="dim", width=6)
    for r in results:
        table.add_row(
            r["video_id"],
            f"{r['start']:.2f} – {r['end']:.2f}",
            r["text"],
            f"{r['distance']:.3f}",
        )
    console.print(table)


def cmd_pipeline(args: argparse.Namespace) -> None:
    from src.downloader import MediaDownloader
    from src.transcriber import Transcriber
    from src.vector_store import VectorStore

    # 1. Download
    console.print("[bold]Step 1/3:[/bold] Downloading audio...")
    downloader = MediaDownloader(output_dir=args.output_dir)
    audio_path = downloader.download_audio(args.url)
    if not audio_path:
        console.print("[red]Download failed.[/red]")
        sys.exit(1)
    console.print(f"[green]Downloaded:[/green] {audio_path}")

    # 2. Transcribe
    console.print("[bold]Step 2/3:[/bold] Transcribing...")
    transcriber = Transcriber()
    segments = transcriber.transcribe(audio_path, language=args.language)
    console.print(f"[green]Transcribed {len(segments)} segments.[/green]")

    # 3. Store
    console.print("[bold]Step 3/3:[/bold] Storing in vector database...")
    video_id = Path(audio_path).stem
    store = VectorStore()
    count = store.store_transcript(video_id, segments)
    console.print(f"[green]Stored {count} segments for video '{video_id}'.[/green]")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(name)s | %(levelname)s | %(message)s",
    )

    commands = {
        "download": cmd_download,
        "transcribe": cmd_transcribe,
        "search": cmd_search,
        "pipeline": cmd_pipeline,
    }

    handler = commands.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
