import whisper

model = whisper.load_model("base")

def transcribe_audio(file_path: str) -> str:
    """ Transcribe audio to text """
    result = model.transcribe(file_path)
    return result["text"]
