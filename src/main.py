from fastapi import FastAPI, UploadFile, File
import shutil
import uuid
from src.transcriber import transcribe_audio

app = FastAPI()

@app.post("/transcribe/")
async def transcribe(file: UploadFile = File(...)):
    temp_filename = f"/tmp/{uuid.uuid4()}_{file.filename}"

    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = transcribe_audio(temp_filename)

    return {"text": text}
