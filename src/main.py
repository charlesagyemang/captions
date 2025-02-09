from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
import shutil
import uuid
from src.transcriber import transcribe_audio

app = FastAPI()

@app.post("/transcribe/")
async def transcribe(file: UploadFile = File(...)):
    """ Upload file, transcribe it, and return JSON + SRT file for DaVinci Resolve """
    temp_filename = f"/tmp/{uuid.uuid4()}_{file.filename}"

    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = transcribe_audio(temp_filename)

    # Provide both JSON response and downloadable SRT file
    return JSONResponse(
        content={
            "text": result["text"],
            "language": result["language"],
            "segments": result["segments"],
            "srt_file_url": f"/download/{temp_filename.rsplit('.', 1)[0]}.srt"
        }
    )

@app.get("/download/{filename}")
async def download_srt(filename: str):
    """ Serve the generated SRT file """
    file_path = f"/tmp/{filename}.srt"
    return FileResponse(file_path, media_type="text/plain", filename=f"{filename}.srt")
