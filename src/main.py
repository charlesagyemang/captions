import logging
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
import shutil
import uuid
import os
from src.transcriber import transcribe_audio  # Assuming this is your transcription function

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set the log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()  # Logs will be printed to the console
    ]
)

app = FastAPI()

# Folder to store uploaded and generated files
UPLOAD_FOLDER = "/tmp/"

@app.post("/transcribe/")
async def transcribe(file: UploadFile = File(...)):
    """
    Uploads an audio file, transcribes it, and returns the SRT file as a downloadable response.
    """
    logging.info("Transcription process started.")

    # Save the uploaded file temporarily
    temp_filename = f"{UPLOAD_FOLDER}{uuid.uuid4()}_{file.filename}"
    logging.info(f"Saving uploaded file to: {temp_filename}")

    try:
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logging.info("Uploaded file saved successfully.")
    except Exception as e:
        logging.error(f"Failed to save uploaded file: {str(e)}")
        return JSONResponse(content={"error": "Failed to save uploaded file", "details": str(e)}, status_code=500)

    # Transcribe the audio and generate the SRT file
    logging.info("Starting transcription process...")
    try:
        result = transcribe_audio(temp_filename)  # Your transcription function
        logging.info("Transcription completed successfully.")
    except Exception as e:
        logging.error(f"Transcription failed: {str(e)}")
        return JSONResponse(content={"error": "Transcription failed", "details": str(e)}, status_code=500)

    # Ensure the SRT file exists
    srt_file_path = result.get("srt_file")
    if not srt_file_path or not os.path.exists(srt_file_path):
        logging.error("SRT file generation failed or file does not exist.")
        return JSONResponse(content={"error": "SRT file generation failed"}, status_code=500)

    logging.info(f"SRT file generated at: {srt_file_path}")

    # Return the SRT file as a downloadable response
    logging.info("Returning SRT file as a downloadable response.")
    return FileResponse(
        path=srt_file_path,
        media_type="application/x-subrip",  # Correct MIME type for SRT files
        filename=os.path.basename(srt_file_path),  # Suggests a filename for the download
        headers={
            "Content-Disposition": f"attachment; filename={os.path.basename(srt_file_path)}"
        }
    )

@app.get("/download/{filename}")
async def download_srt(filename: str):
    """
    Serve the generated SRT file with forced download.
    """
    logging.info(f"Download request received for file: {filename}")

    file_path = f"{UPLOAD_FOLDER}{filename}"
    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        return JSONResponse(content={"error": "File not found"}, status_code=404)

    logging.info(f"Returning file for download: {file_path}")
    return FileResponse(
        path=file_path,
        media_type="application/x-subrip",  # Correct MIME type for SRT files
        filename=os.path.basename(file_path),  # Suggests a filename for the download
        headers={
            "Content-Disposition": f"attachment; filename={os.path.basename(file_path)}"
        }
    )
