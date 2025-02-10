import logging
import whisper
import os
import textwrap

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set the log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()  # Logs will be printed to the console
    ]
)

# Load Whisper Model
model = whisper.load_model("large-v2")
logging.info("Whisper model loaded successfully.")

def transcribe_audio(file_path: str) -> dict:
    """
    Transcribes audio and returns:
    - Full text split into max 3-word lines
    - Detected language
    - Word-level timestamps
    - SRT file path
    """
    logging.info(f"Transcription started for file: {file_path}")

    try:
        # Transcribe the audio file
        logging.info("Running Whisper transcription...")
        result = model.transcribe(file_path, word_timestamps=True)
        logging.info("Whisper transcription completed successfully.")
    except Exception as e:
        logging.error(f"Whisper transcription failed: {str(e)}")
        raise

    # Process transcription text into 3-word segments
    logging.info("Processing transcription text into 3-word chunks...")
    processed_segments = split_text_into_chunks(result["segments"], max_words=3)
    logging.info("Text processing completed successfully.")

    # Generate SRT file
    srt_path = file_path.rsplit(".", 1)[0] + ".srt"
    logging.info(f"Generating SRT file at: {srt_path}")
    generate_srt(processed_segments, srt_path)
    logging.info("SRT file generation completed successfully.")

    return {
        "text": " ".join([seg["text"] for seg in processed_segments]),
        "language": result["language"],
        "segments": processed_segments,
        "srt_file": srt_path
    }

def split_text_into_chunks(segments, max_words=3):
    """ Splits subtitle text into chunks with a max of `max_words` per line. """
    logging.info("Splitting text into chunks...")
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
    logging.info("Text splitting completed successfully.")
    return new_segments

def generate_srt(segments, srt_path):
    """ Generate an SRT subtitle file from 3-word segments """
    logging.info(f"Writing SRT content to file: {srt_path}")
    try:
        with open(srt_path, "w", encoding="utf-8") as srt_file:
            for i, segment in enumerate(segments, start=1):
                start_time = format_srt_timestamp(segment["start"])
                end_time = format_srt_timestamp(segment["end"])
                srt_file.write(f"{i}\n{start_time} --> {end_time}\n{segment['text']}\n\n")
        logging.info("SRT file written successfully.")
    except Exception as e:
        logging.error(f"Failed to write SRT file: {str(e)}")
        raise

def format_srt_timestamp(seconds):
    """ Convert seconds to SRT timestamp format (HH:MM:SS,ms) """
    millis = int((seconds % 1) * 1000)
    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"
