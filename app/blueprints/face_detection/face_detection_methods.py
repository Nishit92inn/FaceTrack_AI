from flask import current_app
import os
import cv2
import json
import numpy as np
from mtcnn import MTCNN
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing import image

detector = None
resnet_model = None

def initialize_models():
    global detector, resnet_model
    if detector is None:
        detector = MTCNN()
    if resnet_model is None:
        resnet_model = ResNet50(weights='imagenet', include_top=False, pooling='avg')

def detect_faces(img):
    initialize_models()
    faces = detector.detect_faces(img)
    return faces

def extract_features(img):
    initialize_models()
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    features = resnet_model.predict(img_array)
    return features

def process_image_file(img_path, celebrity_name, total_images, face_detection_progress):
    img = cv2.imread(img_path)
    if img is None:
        current_app.logger.error(f"Failed to read image from {img_path}")
        return [], []

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    faces = detect_faces(img_rgb)

    processed_dir = os.path.join(current_app.config['PROCESSED_IMAGES_PATH'], celebrity_name)
    os.makedirs(processed_dir, exist_ok=True)

    features = []
    for idx, face in enumerate(faces):
        x, y, width, height = face['box']
        face_region = img_rgb[y:y+height, x:x+width]
        face_image = cv2.resize(face_region, (224, 224))

        face_filename = os.path.join(processed_dir, f"{os.path.basename(img_path).split('.')[0]}_face_{idx}.jpg")
        cv2.imwrite(face_filename, cv2.cvtColor(face_image, cv2.COLOR_RGB2BGR))

        features.append(extract_features(face_image))

    processed_images = len(os.listdir(processed_dir))
    face_detection_progress["progress"] = int((processed_images / total_images) * 100)
    
    return features, faces

def extract_features_from_faces(celebrity_name):
    processed_dir = os.path.join(current_app.config['PROCESSED_IMAGES_PATH'], celebrity_name)
    processed_data = []
    metadata = {}

    image_files = [f for f in os.listdir(processed_dir) if os.path.isfile(os.path.join(processed_dir, f))]

    for image_file in image_files:
        img_path = os.path.join(processed_dir, image_file)
        img = cv2.imread(img_path)
        if img is None:
            current_app.logger.error(f"Failed to read image from {img_path}")
            continue
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        features = extract_features(img_rgb)
        processed_data.append({'file': image_file, 'features': features.tolist()})
        
        metadata[image_file] = {
            "features": features.tolist()
        }
    
    metadata_path = os.path.join(processed_dir, f"{celebrity_name}_features_metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=4)

    return processed_data