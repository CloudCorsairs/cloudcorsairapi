import base64
import cv2
import numpy as np
from PIL import Image
import io
from ultralytics import YOLO
import tempfile
import os

class_mapping = {
    0: 'Back Bumper',
    1: 'Back Glass',
    2: 'Back Left Door',
    3: 'Back Left Light',
    4: 'Back Right Door',
    5: 'Back Right Light',
    6: 'Front Bumper',
    7: 'Front Glass',
    8: 'Front Left Door',
    9: 'Front Left Light',
    10: 'Front Right Door',
    11: 'Front Right Light',
    12: 'Hood',
    13: 'Left Mirror',
    14: 'Right Mirror',
    15: 'Tailgate',
    16: 'Trunk',
    17: 'Wheel'
}

class DamageDetector:
    def __init__(self, model_path, parts_model):
        self.model = YOLO(model_path)
        self.parts = YOLO(parts_model)
        self.class_names = {0: "Damage"}

    def base64_to_image(self, base64_str):
        img_data = base64.b64decode(base64_str)
        image = Image.open(io.BytesIO(img_data)).convert('RGB')
        return np.array(image)

    def image_to_base64(self, image):
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)

        _, buffer = cv2.imencode('.jpg', image)
        base64_str = base64.b64encode(buffer).decode('utf-8')
        return base64_str

    def predict_and_draw(self, base64_str):

        image = self.base64_to_image(base64_str)

        # Run the models on the input image
        results_damage = self.model.predict(image)

        if isinstance(results_damage, list):
            results_damage = results_damage[0]

        # Extract bounding boxes, labels, and scores from results_damage
        boxes_damage = results_damage.boxes
        num_damage_detections = 0
        if boxes_damage is not None:
            num_damage_detections = len(boxes_damage)
            for box in boxes_damage:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                label = box.cls[0].item()
                cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.putText(image, self.class_names.get(int(label), 'Unknown'), (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Save the annotated image
        temp_dir = tempfile.mkdtemp()
        annotated_img_path = os.path.join(temp_dir, "annotated_image.png")
        cv2.imwrite(annotated_img_path, image)

        num_parts_detections = 0
        parts_detections = ""
        if num_damage_detections > 0:
            # Run the parts detection model on the annotated image
            results_parts = self.parts.predict(annotated_img_path)

            if isinstance(results_parts, list):
                results_parts = results_parts[0]

            boxes_parts = results_parts.boxes
            if boxes_parts is not None:
                num_parts_detections = len(boxes_parts)
                parts_detections = []
                for box in boxes_parts:
                    label = box.cls[0].item()
                    class_name = class_mapping.get(int(label), 'Unknown')
                    parts_detections.append(class_name)
                parts_detections = ", ".join(parts_detections)  # Convert list to a comma-separated string

        # Remove the temporary files
        try:
            os.remove(annotated_img_path)
            os.rmdir(temp_dir)
        except Exception as e:
            print(f"Error removing temporary files: {e}")

        # Convert the annotated image to base64
        image_base64 = self.image_to_base64(image)

        return {
            'image': image_base64,
            'parts_detections': parts_detections if num_damage_detections > 0 else ""
        }
