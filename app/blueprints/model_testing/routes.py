import os
import json
import logging
import numpy as np
import tensorflow as tf
import time
from flask import Blueprint, request, jsonify, render_template, current_app
from werkzeug.utils import secure_filename
from tensorflow.keras.preprocessing import image as keras_image
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.models import Model
from tensorflow.keras.applications import ResNet50

model_testing_bp = Blueprint('model_testing', __name__, template_folder='templates', static_folder='static')

def create_feature_extractor():
    base_model = ResNet50(weights='imagenet')
    model = Model(inputs=base_model.input, outputs=base_model.get_layer('avg_pool').output)
    return model

feature_extractor = create_feature_extractor()

@model_testing_bp.route('/')
def test_model_page():
    return render_template('test_model.html')

@model_testing_bp.route('/get_models', methods=['GET'])
def get_models():
    models = [f for f in os.listdir(current_app.config['TRAINED_MODELS_PATH']) if f.endswith('.h5')]
    return jsonify({'models': models})

@model_testing_bp.route('/upload_image', methods=['POST'])
def upload_image():
    try:
        if 'model' not in request.form or 'image' not in request.files:
            return jsonify({'error': 'Model and image are required fields'}), 400
        
        model_name = request.form['model']
        model_path = os.path.join(current_app.config['TRAINED_MODELS_PATH'], model_name)
        
        model = tf.keras.models.load_model(model_path)
        
        file = request.files['image']
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        img = keras_image.load_img(file_path, target_size=(224, 224))
        img_array = keras_image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        
        start_time = time.time()
        features = feature_extractor.predict(img_array)
        prediction = model.predict(features)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        predicted_label = np.argmax(prediction, axis=1)[0]
        confidence = prediction[0][predicted_label]
        
        with open(current_app.config['LABEL_MAP_PATH'], 'r') as f:
            label_map = json.load(f)
        
        celebrity_name = label_map.get(str(predicted_label), "Unknown")
        
        top_predictions = []
        for i in np.argsort(prediction[0])[-5:][::-1]:
            top_predictions.append({
                'label': label_map.get(str(i), "Unknown"),
                'confidence': float(prediction[0][i])
            })
        
        return jsonify({
            'label': celebrity_name,
            'confidence': float(confidence),
            'processing_time': processing_time,
            'top_predictions': top_predictions
        })
    
    except Exception as e:
        current_app.logger.error(f"An error occurred during image upload and prediction: {e}")
        return jsonify({'error': str(e)}), 500