import whisper
import os
import textwrap

# Load Whisper Model
model = whisper.load_model("large-v2")

def transcribe_audio(file_path: str) -> dict:
    """
    Transcribes audio and returns:
    - Full text split into max 3-word lines
    - Detected language
    - Word-level timestamps
    - SRT file path
    """
    result = model.transcribe(file_path, word_timestamps=True)

    # Process transcription text into 3-word segments
    processed_segments = split_text_into_chunks(result["segments"], max_words=3)

    # Generate SRT file
    srt_path = file_path.rsplit(".", 1)[0] + ".srt"
    generate_srt(processed_segments, srt_path)

    return {
        "text": " ".join([seg["text"] for seg in processed_segments]),
        "language": result["language"],
        "segments": processed_segments,
        "srt_file": srt_path
    }


def split_text_into_chunks(segments, max_words=3):
    """ Splits subtitle text into chunks with a max of `max_words` per line. """
    new_segments = []

    for segment in segments:
        words = segment["text"].split()
        chunked_texts = textwrap.wrap(segment["text"], width=max_words * 10)  # Wrap text with word limit

        start_time = segment["start"]
        duration_per_chunk = (segment["end"] - segment["start"]) / len(chunked_texts)

        for i, chunk in enumerate(chunked_texts):
            new_segments.append({
                "start": round(start_time + (i * duration_per_chunk), 2),
                "end": round(start_time + ((i + 1) * duration_per_chunk), 2),
                "text": chunk
            })

    return new_segments


def generate_srt(segments, srt_path):
    """ Generate an SRT subtitle file from 3-word segments """
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
