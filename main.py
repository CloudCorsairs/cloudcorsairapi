from fastapi import FastAPI, File, UploadFile, HTTPException, Query
import base64
import requests
from pathlib import Path
import supabase_client
from SentialCorsair import DamageDetector
from pydantic import BaseModel
from io import BytesIO

app = FastAPI()

class ImageRequest(BaseModel):
    url: str


model_path = "v8.15.pt"  # Replace with your actual model path
parts_model = "Partv820.pt"  # Replace with your actual parts model path
damage_detector = DamageDetector(model_path, parts_model)

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


@app.post("/sentinel-corsair")
async def sentinel_corsair(request: ImageRequest):
    try:
        response = requests.get(request.url)
        if response.status_code == 200:

            image_data = response.content
            base64_encoded = base64.b64encode(image_data).decode('utf-8')

        else:
            raise Exception(f"Failed to fetch image. Status code: {response.status_code}")

        result = damage_detector.predict_and_draw(base64_encoded)

        if result is None:
            raise HTTPException(status_code=400, detail="No damage detected in the image.")

        image_base64 = result.get('image')
        parts_detections = result.get('parts_detections')

        item = supabase_client.update_image_url(request.url,image_base64)
        print(item)
        return item
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")