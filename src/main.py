from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
import shutil
import uuid
import os
from src.transcriber import transcribe_audio

app = FastAPI()

UPLOAD_FOLDER = "/tmp/"

@app.post("/transcribe/")
async def transcribe(file: UploadFile = File(...)):
    """ Uploads file, transcribes it, and returns text + SRT file. """
    temp_filename = f"{UPLOAD_FOLDER}{uuid.uuid4()}_{file.filename}"

    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = transcribe_audio(temp_filename)

    # Provide both JSON response and downloadable SRT file
    return JSONResponse(
        content={
            "text": result["text"],
            "language": result["language"],
            "segments": result["segments"],
            "srt_file_url": f"/download/{os.path.basename(result['srt_file'])}"
        }
    )

@app.get("/download/{filename}")
async def download_srt(filename: str):
    """ Serve the generated SRT file """
    file_path = f"{UPLOAD_FOLDER}{filename}"
    return FileResponse(file_path, media_type="text/plain", filename=filename)
