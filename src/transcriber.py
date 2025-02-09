import whisper
import os

# Load Whisper Model (Choose 'base', 'medium', 'large-v2' based on accuracy vs speed)
model = whisper.load_model("large-v2")

def transcribe_audio(file_path: str) -> dict:
    """
    Transcribes audio and returns:
    - Full text
    - Detected language
    - Timestamps
    - SRT file path
    """
    result = model.transcribe(file_path, word_timestamps=True)

    # Extract key details
    transcription = {
        "text": result["text"],
        "language": result["language"],
        "segments": [
            {
                "start": round(segment["start"], 2),
                "end": round(segment["end"], 2),
                "text": segment["text"]
            }
            for segment in result["segments"]
        ]
    }

    # Generate SRT file
    srt_path = file_path.rsplit(".", 1)[0] + ".srt"
    generate_srt(transcription["segments"], srt_path)

    transcription["srt_file"] = srt_path
    return transcription


def generate_srt(segments, srt_path):
    """ Generate an SRT subtitle file from segments """
    with open(srt_path, "w", encoding="utf-8") as srt_file:
        for i, segment in enumerate(segments, start=1):
            start_time = format_srt_timestamp(segment["start"])
            end_time = format_srt_timestamp(segment["end"])
            srt_file.write(f"{i}\n{start_time} --> {end_time}\n{segment['text']}\n\n")


def format_srt_timestamp(seconds):
    """ Convert seconds to SRT timestamp format (HH:MM:SS,ms) """
    millis = int((seconds % 1) * 1000)
    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"
