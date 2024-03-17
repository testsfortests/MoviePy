import os 
from typing import List
import requests
from fastapi import FastAPI, Request,Response
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from utils.videomaker import create_final_video
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow CORS for all origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE","HEAD"],
    allow_headers=["*"],
)

@app.get("/")
@app.head("/")  # Enable HEAD method
async def read_root():
    html_content = """
    <html>
    <head>
        <title>Hello World</title>
        <style>
            /* Define CSS styles */
            .blue-text {
                color: blue;
            }
        </style>
    </head>
    <body>
        <h1>Hello World, Welcome !!!</h1>
        <footer>
            <marquee behavior="scroll" direction="left" class="blue-text">Developed by Pawan Kumar</marquee>
        </footer>
    </body>
    </html>
    """
    return Response(content=html_content, media_type="text/html")


# Define the directory where files will be saved
UPLOAD_DIRECTORY = "uploads"
TELE_ENDPOINT_URL = "https://tft-backend.onrender.com/tele/send-file"  # URL of the tele endpoint

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

def meets_conditions(filenames: List[str]) -> bool:
    required_filenames = {"image_que.png", "image_ans.png", "music_que.mp3", "music_ans.mp3"}
    return set(filenames) == required_filenames

def clean_upload_folder():
    """Function to delete all files from the upload folder."""
    files = os.listdir(UPLOAD_DIRECTORY)
    for file_name in files:
        file_path = os.path.join(UPLOAD_DIRECTORY, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
    print("Deleted files successfully")

@app.post("/upload/")
async def upload_files(files: List[UploadFile] = File(...)):

    print("UPLOAD FUNC CALLED ..")
    try:
        clean_upload_folder()

        # Check if files were uploaded 
        if not files:
            raise HTTPException(status_code=400, detail="No files were uploaded.")

        uploaded_files = []

        # Iterate through each file and save it in the upload directory
        for file in files:
            file_location = os.path.join(UPLOAD_DIRECTORY, file.filename)
            with open(file_location, "wb") as file_object:
                file_object.write(file.file.read())

            uploaded_files.append(file_location)

            # Check if conditions are met to call create_final_video
            if len(uploaded_files) == 4 and meets_conditions([file.filename for file in files]):
                print("condition meet successfully")
                create_final_video()

        print("start sending files to tele")
        # Call the tele endpoint with all files present in the upload folder
        for file_location in uploaded_files:
            with open(file_location, 'rb') as file_content:
                files_data = {'file': (os.path.basename(file_location), file_content)}
                response = requests.post(TELE_ENDPOINT_URL, files=files_data)

                # Check the response status
                if response.status_code != 200:
                    return {"success": False, "message": "Failed to send file to Telegram.", "error": response.text}

            # Remove the file from the server after sending
            # os.remove(file_location)

        return {"success": True, "message": "All files sent successfully to Telegram."}

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error: " + str(e))


