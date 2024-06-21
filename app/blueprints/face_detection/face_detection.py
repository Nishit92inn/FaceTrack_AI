from flask import current_app
import os
from .face_detection_methods import process_image_file

face_detection_progress = {"progress": 0}

def process_celebrity_folder(celebrity_name, reprocess=False):
    global face_detection_progress
    face_detection_progress["progress"] = 0

    raw_dir = os.path.join(current_app.config['RAW_DATASET_PATH'], celebrity_name)
    processed_dir = os.path.join(current_app.config['PROCESSED_IMAGES_PATH'], celebrity_name)
    
    if not os.path.exists(raw_dir):
        current_app.logger.error(f"Raw directory does not exist: {raw_dir}")
        return

    if not reprocess and os.path.exists(processed_dir) and len(os.listdir(processed_dir)) > 0:
        current_app.logger.info(f"Skipping processing for {celebrity_name} as images are already processed.")
        face_detection_progress["progress"] = 100
        return

    image_files = [os.path.join(raw_dir, f) for f in os.listdir(raw_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    total_images = len(image_files)

    for img_path in image_files:
        process_image_file(img_path, celebrity_name, total_images, face_detection_progress)

def process_all_folders():
    global face_detection_progress
    face_detection_progress["progress"] = 0

    raw_dataset_path = current_app.config['RAW_DATASET_PATH']
    celebrities = [f for f in os.listdir(raw_dataset_path) if not f.startswith('.')]
    total_folders = len(celebrities)

    for idx, celebrity in enumerate(celebrities):
        process_celebrity_folder(celebrity)
        face_detection_progress["progress"] = int(((idx + 1) / total_folders) * 100)

def get_face_detection_progress():
    global face_detection_progress
    return face_detection_progress