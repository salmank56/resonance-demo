import os
import subprocess
from pathlib import Path
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

# Define the upload directory
#upload_dir = Path("uploads")
#upload_dir.mkdir(parents=True, exist_ok=True)


@app.post("/upload-csv/")
async def upload_csv(file: UploadFile = File(...)):
    try:
        # Define the file path
        #file_path = upload_dir / file.filename
        file_path = file.filename
        # Save the file
        with open(file_path, "wb") as f:
            f.write(await file.read())

        return JSONResponse(content={"message": "File uploaded successfully", "filename": file.filename})
    except Exception as e:
        return JSONResponse(content={"message": f"An error occurred: {e}"}, status_code=500)

@app.post("/run-main/")
async def run_main():
    def stream_logs():
        process = subprocess.Popen(
            ["python", "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        for line in iter(process.stdout.readline, ''):
            yield line

        process.stdout.close()
        process.stderr.close()

    return StreamingResponse(stream_logs(), media_type="text/plain")