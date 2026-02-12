import os
import logging
from typing import Optional
import yt_dlp

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class MediaDownloader:
    """
    Downloads audio from YouTube videos using yt-dlp.
    """
    def __init__(self, output_dir: str = "downloads"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def download_audio(self, video_url: str) -> Optional[str]:
        """
        Downloads audio from a YouTube video URL and returns the path to the downloaded file.
        
        Args:
            video_url: The URL of the YouTube video or a video ID.

        Returns:
            The path to the downloaded audio file, or None if download failed.

        Raises:
            ValueError: If video_url is empty or invalid format.
        """
        if not video_url or not video_url.strip():
            raise ValueError("video_url cannot be empty")

        # Normalize video URL/ID
        video_url = video_url.strip()
        if not video_url.startswith("http"):
            # Assume it's a video ID
            video_url = f"https://www.youtube.com/watch?v={video_url}"

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'outtmpl': str(self.output_dir + "/" + '%(id)s.%(ext)s'),
            'quiet': False,
            'no_warnings': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info(f"Downloading audio from {video_url}...")
                info = ydl.extract_info(video_url, download=True)
                video_id = info['id']
                filename = str(self.output_dir / f"{video_id}.wav")

                # Verify the file was actually created
                if not Path(filename).exists():
                    logger.error(f"Download completed but file not found: {filename}")
                    return None

                logger.info(f"Successfully downloaded audio to {filename}")
                return filename

        except yt_dlp.utils.DownloadError as e:
            logger.error(f"Download error: {e}")
            return None
        except yt_dlp.utils.ExtractorError as e:
            logger.error(f"Extractor error (invalid URL or video unavailable): {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading video: {e}")
            return None

    def is_downloaded(self, video_id: str) -> bool:
        """
        Check if a video has already been downloaded.

        Args:
            video_id: YouTube video ID.

        Returns:
            True if the audio file exists, False otherwise.
        """
        filename = self.output_dir / f"{video_id}.wav"
        return filename.exists()

if __name__ == "__main__":
    # Simple test
    import sys
    if len(sys.argv) > 1:
        downloader = MediaDownloader()
        downloader.download_audio(sys.argv[1])
    else:
        print("Usage: python src/downloader.py <video_url>")
