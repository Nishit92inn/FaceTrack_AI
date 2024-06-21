from flask import current_app
import os
import json
import cv2
from .face_detection_methods import extract_features

feature_extraction_progress = {"progress": 0, "log": ""}

def log_message(message):
    global feature_extraction_progress
    feature_extraction_progress["log"] += f"{message}<br>"
    current_app.logger.info(message)

def extract_features_for_all_celebrities():
    global feature_extraction_progress
    feature_extraction_progress["progress"] = 0
    feature_extraction_progress["log"] = ""

    processed_images_path = current_app.config['PROCESSED_IMAGES_PATH']
    processed_dataset_path = current_app.config['PROCESSED_DATASET_PATH']
    os.makedirs(processed_dataset_path, exist_ok=True)

    celebrities = [f for f in os.listdir(processed_images_path) if not f.startswith('.')]
    total_folders = len(celebrities)

    for idx, celebrity in enumerate(celebrities):
        try:
            log_message(f"Starting feature extraction for {celebrity}")
            celebrity_images_path = os.path.join(processed_images_path, celebrity)
            feature_data = []

            for image_file in os.listdir(celebrity_images_path):
                if image_file.lower().endswith(('jpg', 'jpeg', 'png')):
                    img_path = os.path.join(celebrity_images_path, image_file)
                    img = cv2.imread(img_path)
                    if img is not None:
                        features = extract_features(img)
                        feature_data.append({'file': image_file, 'features': features.tolist()})
                    else:
                        log_message(f"Failed to read image: {img_path}")

            features_file = os.path.join(processed_dataset_path, f"{celebrity}_features.json")
            with open(features_file, 'w') as f:
                json.dump(feature_data, f, indent=4)

            feature_extraction_progress["progress"] = int(((idx + 1) / total_folders) * 100)
            log_message(f"Completed feature extraction for {celebrity}")
        except Exception as e:
            log_message(f"Error processing {celebrity}: {str(e)}")

    feature_extraction_progress["progress"] = 100
    log_message("Feature extraction for all celebrities completed.")

def get_feature_extraction_progress():
    global feature_extraction_progress
    return feature_extraction_progress