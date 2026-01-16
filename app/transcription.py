import os
import shutil
from faster_whisper import WhisperModel

# Global model instance
_model = None

def get_model():
    """Lazy load the Whisper model with optimized settings"""
    global _model
    if _model is None:
        print("Loading Faster Whisper Model (Tiny - CPU)...")
        try:
            # 'int8' is faster on CPU. 
            # If you have errors, try 'float32' (slower but more compatible)
            _model = WhisperModel("tiny", device="cpu", compute_type="int8")
        except Exception as e:
            print(f"Error loading model: {e}")
            return None
    return _model

def transcribe_audio_chunk(file_path: str) -> str:
    """
    Transcribes audio with strict filtering for silence and hallucinations.
    """
    model = get_model()
    if not model:
        return ""
    
    try:
        # 1. language="en": Force English
        # 2. vad_filter=True: Ignore silence (Crucial for reducing hallucinations)
        # 3. condition_on_previous_text=False: Treat chunk as standalone (prevents loop hallucinations)
        segments, info = model.transcribe(
            file_path, 
            beam_size=5, 
            language="en", 
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
            condition_on_previous_text=False
        )
        
        valid_texts = []
        for segment in segments:
            # 4. Filter out low confidence segments or common hallucinations
            if segment.avg_logprob < -1.0: # Threshold for "unsure" transcription
                continue
                
            text = segment.text.strip()
            
            # 5. Block common Whisper hallucinations on empty audio
            hallucinations = ["you", "thank you", "thanks", "subtitle by", "watching", "."]
            if text.lower() in hallucinations:
                continue
                
            if len(text) > 0:
                valid_texts.append(text)
                
        return " ".join(valid_texts)

    except Exception as e:
        print(f"Transcription error: {e}")
        return ""
    finally:
        # Cleanup temp file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass