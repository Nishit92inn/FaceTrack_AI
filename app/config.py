import os

class Config:
    RAW_DATASET_PATH = os.path.join(os.getcwd(), 'data', 'raw_DataSet')
    PROCESSED_IMAGES_PATH = os.path.join(os.getcwd(), 'data', 'processed_images')

app.config.from_object(Config)