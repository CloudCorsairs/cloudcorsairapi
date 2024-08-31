from fastapi import FastAPI, File, UploadFile, HTTPException
import base64
from pathlib import Path
from supabase_client import supabase

app = FastAPI()

@app.get("/get")
async def get_image_base64(image_path: str):
    # Validate if the image file exists
    file_path = Path(image_path)
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    # Read the file content
    with open(file_path, "rb") as image_file:
        content = image_file.read()
    
    # Convert the binary data to base64 encoded string
    encoded_string = base64.b64encode(content).decode('utf-8')
    
    return {"image_path": image_path, "base64": encoded_string}

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    # Read the file content
    content = await file.read()
    
    # Convert the binary data to base64 encoded string
    encoded_string = base64.b64encode(content).decode('utf-8')
    
    # Save the image to Supabase
    try:
        response = supabase.table("images").insert({"filename": file.filename, "base64": encoded_string}).execute()
        if response.status_code == 201:
            return {"filename": file.filename, "base64": encoded_string, "message": "Image successfully uploaded to Supabase."}
        else:
            raise HTTPException(status_code=500, detail="Failed to upload image to Supabase.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading image to Supabase: {str(e)}")

@app.get("/fetch-image")
async def fetch_image_from_supabase(filename: str):
    # Fetch the image from Supabase
    try:
        # Query the Supabase table for the image with the specified filename
        response = supabase.table("images").select("*").eq("filename", filename).execute()

        # Check if the image exists
        if response.data and len(response.data) > 0:
            image_data = response.data[0]
            return {"filename": image_data["filename"], "base64": image_data["base64"]}
        else:
            raise HTTPException(status_code=404, detail="Image not found in Supabase.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching image from Supabase: {str(e)}")