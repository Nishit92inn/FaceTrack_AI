from flask import current_app
import os
import json

def create_label_map():
    label_map_dir = current_app.config['LABEL_MAP_DIR']
    processed_dataset_dir = current_app.config['PROCESSED_DATASET_PATH']
    
    os.makedirs(label_map_dir, exist_ok=True)

    label_map = {}
    current_label = 0

    for filename in os.listdir(processed_dataset_dir):
        if filename.endswith('_features.json'):
            celebrity_name = filename.replace('_features.json', '')
            label_map[current_label] = celebrity_name
            current_label += 1

    label_map_file = os.path.join(label_map_dir, 'label_map.json')
    with open(label_map_file, 'w') as f:
        json.dump(label_map, f, indent=4)

    current_app.logger.info(f"Label map created with {current_label} entries.")