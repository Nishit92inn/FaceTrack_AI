import os
import json
import numpy as np
import datetime
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Input
from tensorflow.keras.utils import to_categorical
import tensorflow as tf
from flask import current_app

training_progress = {'status': 'not started', 'epoch': 0, 'accuracy': 'N/A', 'loss': 'N/A', 'val_accuracy': 'N/A', 'val_loss': 'N/A'}

def load_data(data_dir):
    X, y, label_map = [], [], {}
    current_label = 0

    for filename in os.listdir(data_dir):
        if filename.startswith('.') or not filename.endswith('_features.json'):
            continue

        with open(os.path.join(data_dir, filename), 'r') as f:
            data = json.load(f)
        for item in data:
            X.append(item['features'])
            y.append(current_label)
        label_map[current_label] = filename.replace('_features.json', '')
        current_label += 1

    X = np.array(X)
    y = np.array(y)
    
    X = X.reshape((X.shape[0], -1))

    return X, y, label_map

def prepare_data(data_dir):
    X, y, label_map = load_data(data_dir)
    y = to_categorical(y)
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    return X_train, X_val, y_train, y_val, label_map

def create_model(input_shape, num_classes):
    model = Sequential([
        Input(shape=input_shape),
        Dense(512, activation='relu'),
        Dropout(0.5),
        Dense(512, activation='relu'),
        Dropout(0.5),
        Dense(num_classes, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def train_model(data_dir, num_epochs, batch_size):
    global training_progress
    training_progress = {'status': 'in progress', 'epoch': 0, 'accuracy': 'N/A', 'loss': 'N/A', 'val_accuracy': 'N/A', 'val_loss': 'N/A'}

    X_train, X_val, y_train, y_val, label_map = prepare_data(data_dir)
    
    input_shape = (X_train.shape[1],)
    num_classes = len(label_map)

    model = create_model(input_shape, num_classes)
    
    def on_epoch_end(epoch, logs):
        training_progress['epoch'] = epoch + 1
        training_progress['accuracy'] = f"{logs['accuracy']:.4f}"
        training_progress['loss'] = f"{logs['loss']:.4f}"
        training_progress['val_accuracy'] = f"{logs['val_accuracy']:.4f}"
        training_progress['val_loss'] = f"{logs['val_loss']:.4f}"
    
    history = model.fit(
        X_train, y_train, 
        epochs=num_epochs, 
        validation_data=(X_val, y_val), 
        batch_size=batch_size,
        callbacks=[tf.keras.callbacks.LambdaCallback(on_epoch_end=on_epoch_end)]
    )

    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    model_save_path = os.path.join(current_app.config['TRAINED_MODELS_PATH'], f'trained_model_{timestamp}.h5')
    history_save_path = os.path.join(current_app.config['TRAINING_HISTORY_PATH'], f'training_history_{timestamp}.json')

    model.save(model_save_path)
    with open(history_save_path, 'w') as f:
        json.dump(history.history, f)

    training_progress['status'] = 'completed'
    training_progress['model_path'] = model_save_path
    training_progress['history_path'] = history_save_path
    current_app.logger.info(f"Training completed. Model saved as {model_save_path}")

def get_training_progress():
    return training_progress