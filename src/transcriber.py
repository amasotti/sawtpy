import os
import logging
from typing import List, Dict, Any
from faster_whisper import WhisperModel
import torch

logger = logging.getLogger(__name__)

class Transcriber:
    """
    Transcribes audio files using faster-whisper.
    """
    def __init__(self, model_size: str = "large-v3", device: str = "auto", compute_type: str = "float16"):
        """
        Initializes the Transcriber with the specified model and device.

        Args:
            model_size: Size of the Whisper model to use (e.g., "tiny", "base", "medium", "large-v3").
            device: Device to use for computation ("cpu", "cuda", "auto").
            compute_type: Type of quantization to use ("int8", "float16", "float32").
        """
        self.model_size = model_size
        
        # Check for MPS (Metal Performance Shaders) on macOS
        if device == "auto":
            if torch.backends.mps.is_available():
                logger.info("MPS (Metal) is available. optimizing for macOS.")
                # faster-whisper via CTranslate2 doesn't support "mps" device string directly in all versions yet, 
                # but "cpu" with specific compute types can be fast. 
                # However, let's try to infer best settings.
                # Examples suggest standard 'cpu' or 'cuda'. 
                # For now we stick to 'cpu' as safer default for Mac unless CTranslate2 supports MPS explicitly.
                # Actually, correct usage for CTranslate2 on Mac is typically CPU with acceleration or 'auto'.
                self.device = "cpu" 
                self.compute_type = "int8" # often faster on CPU
            elif torch.cuda.is_available():
                self.device = "cuda"
                self.compute_type = compute_type
            else:
                self.device = "cpu"
                self.compute_type = "int8"
        else:
            self.device = device
            self.compute_type = compute_type

        logger.info(f"Loading Whisper model '{self.model_size}' on device '{self.device}' with compute type '{self.compute_type}'...")
        try:
            self.model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)
            logger.info("Model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def transcribe(self, audio_path: str, beam_size: int = 5) -> List[Dict[str, Any]]:
        """
        Transcribes the given audio file.

        Args:
            audio_path: Path to the audio file.
            beam_size: Beam size for beam search decoding.

        Returns:
            A list of dictionary segments containing 'start', 'end', and 'text'.
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info(f"Starting transcription for {audio_path}...")
        try:
            segments, info = self.model.transcribe(audio_path, beam_size=beam_size, language="it") # Prioritize Arabic/Tunisian as requested
            
            logger.info(f"Detected language '{info.language}' with probability {info.language_probability}")

            result = []
            for segment in segments:
                # logger.debug(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
                result.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text
                })
            
            logger.info(f"Transcription complete. {len(result)} segments found.")
            return result
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
        transcriber = Transcriber()
        segments = transcriber.transcribe(audio_file)

        # Print first few segments
        for seg in segments[:5]:
            print(f"[{seg['start']:.2f} - {seg['end']:.2f}]: {seg['text']}")

        # save to file
        with open(audio_file + ".txt", "w", encoding="utf-8") as f:
            for seg in segments:
                f.write(f"[{seg['start']:.2f} - {seg['end']:.2f}]: {seg['text']}\n")
    else:
        print("Usage: python src/transcriber.py <audio_file_path>")
