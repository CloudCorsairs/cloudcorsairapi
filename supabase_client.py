from supabase import create_client, Client

SUPABASE_URL = "https://nsoghqqtwvbssfeqjrtf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5zb2docXF0d3Zic3NmZXFqcnRmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjUwMzUxNDAsImV4cCI6MjA0MDYxMTE0MH0.POytBQ0lSHpaWY0QMB8aPBPWGf9o0Ao7bjiyITteav0"

import base64
import io
from PIL import Image
from supabase import create_client, Client

# Initialize Supabase client
url = SUPABASE_URL
api_key = SUPABASE_KEY
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def base64_to_image(base64_string):
    """Convert base64 string to image."""
    image_data = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(image_data))
    return image


def upload_image_to_supabase(image, image_name):
    """Upload image to Supabase storage and return the URL."""
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    response = supabase.storage().from_("claims").upload(image_name, buffer)

    if response.status_code == 200:
        return f"{url}/storage/v1/object/CloudCorsairs/claims/ai_uploads/{image_name}"
    else:
        print("Failed to upload image:", response.json())
        return None


def update_image_url(old_url, base64_string):
    """Find the record by old URL, convert base64 to image, upload it, and update the record with the new URL."""
    table_name = "your_table_name"

    # Convert base64 to image
    image = base64_to_image(base64_string)

    # Generate a new image name (e.g., new_image.png)
    image_name = "new_image.png"

    # Upload image to Supabase
    new_url = upload_image_to_supabase(image, image_name)

    if new_url:
        # Find the record ID based on the old image URL
        response = supabase.table(table_name).select("id").eq("image_url", old_url).execute()

        if response.status_code == 200:
            data = response.data
            if data and len(data) > 0:
                record_id = data[0]['id']

                # Update the record with the new image URL
                update_response = supabase.table(table_name).update({"image_url": new_url}).eq("id",
                                                                                               record_id).execute()

                if update_response.status_code == 200:
                    print("Record updated successfully with new URL.")
                else:
                    print("Failed to update the record:", update_response.json())
            else:
                print("No record found with the given old URL.")
        else:
            print("Query failed:", response.json())
