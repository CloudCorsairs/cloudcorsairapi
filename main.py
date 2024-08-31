import json
from fastapi import FastAPI, File, UploadFile, HTTPException, Query
import base64
import requests
from SentialCorsair import DamageDetector
from pydantic import BaseModel


app = FastAPI()

class ImageRequest(BaseModel):
    url: str

model_path = "v8.15.pt"  # Replace with your actual model path
parts_model = "Partv820.pt"  # Replace with your actual parts model path
damage_detector = DamageDetector(model_path, parts_model)


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

        response_data = {
            'parts': parts_detections
        }

        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.post("/sentinel-corsair-image")
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

        response_data = {
            'image_base64': image_base64,
            'parts': parts_detections
        }

        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
