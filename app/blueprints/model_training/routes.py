from flask import render_template, jsonify, request, current_app
import threading
from .train_model import train_model, get_training_progress
from . import model_training_bp

@model_training_bp.route('/')
def train_model_page():
    return render_template('train_model.html')

@model_training_bp.route('/start_training', methods=['POST'])
def start_training():
    data = request.json
    num_epochs = int(data.get('num_epochs', 10))
    batch_size = int(data.get('batch_size', 32))
    
    current_app.logger.info(f"Starting model training with {num_epochs} epochs and batch size {batch_size}")
    
    threading.Thread(target=train_model, args=(current_app.config['PROCESSED_DATASET_PATH'], num_epochs, batch_size)).start()
    return jsonify({'status': 'started'})

@model_training_bp.route('/training_progress', methods=['GET'])
def training_progress():
    return jsonify(get_training_progress())