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
            video_url: The URL of the YouTube video.
            
        Returns:
            The path to the downloaded audio file, or None if download failed.
        """
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(self.output_dir, '%(id)s.%(ext)s'),
            'quiet': False,
            'no_warnings': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info(f"Downloading audio from {video_url}...")
                info = ydl.extract_info(video_url, download=True)
                video_id = info['id']
                filename = os.path.join(self.output_dir, f"{video_id}.wav")
                logger.info(f"Successfully downloaded audio to {filename}")
                return filename
        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            return None

if __name__ == "__main__":
    # Simple test
    import sys
    if len(sys.argv) > 1:
        downloader = MediaDownloader()
        downloader.download_audio(sys.argv[1])
    else:
        print("Usage: python src/downloader.py <video_url>")
