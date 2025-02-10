from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import shutil
import uuid
import os
from src.transcriber import transcribe_audio

app = FastAPI()

UPLOAD_FOLDER = "/tmp/"

@app.post("/transcribe/")
async def transcribe(file: UploadFile = File(...)):
    """
    Uploads file, transcribes it, and directly returns the SRT file.
    """
    # Save the uploaded file temporarily
    temp_filename = f"{UPLOAD_FOLDER}{uuid.uuid4()}_{file.filename}"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Transcribe the audio and generate the SRT file
    result = transcribe_audio(temp_filename)

    # Ensure the SRT file exists
    srt_file_path = result["srt_file"]
    if not os.path.exists(srt_file_path):
        return {"error": "SRT file generation failed"}, 500

    # Return the SRT file directly as the response
    return FileResponse(
        path=srt_file_path,
        media_type="text/plain",  # MIME type for SRT files
        filename=os.path.basename(srt_file_path)  # Optional: Set the filename for download
    )

@app.get("/download/{filename}")
async def download_srt(filename: str):
    """
    Serve the generated SRT file (optional, if you still want to allow direct downloads).
    """
    file_path = f"{UPLOAD_FOLDER}{filename}"
    if not os.path.exists(file_path):
        return {"error": "File not found"}, 404
    return FileResponse(file_path, media_type="text/plain", filename=filename)
