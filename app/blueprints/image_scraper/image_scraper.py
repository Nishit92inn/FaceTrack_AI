import os
import json
import requests
from bs4 import BeautifulSoup
import random
import base64

RAW_DATASET_DIR = 'Raw_DataSet'
METADATA_DIR = 'Metadata'
METADATA_FILE = os.path.join(METADATA_DIR, 'image_mappings.json')

# Global variable for progress tracking
scraping_progress = 0

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
]

def create_folder_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")
    else:
        print(f"Directory already exists: {path}")

def load_metadata():
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'r') as f:
            return json.load(f)
    else:
        return {}

def save_metadata(metadata):
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=4)

def download_image(url, folder_path, image_name):
    if url.startswith('data:image/'):
        # Handle base64 encoded images
        header, encoded = url.split(',', 1)
        data = base64.b64decode(encoded)
        with open(os.path.join(folder_path, image_name), 'wb') as f:
            f.write(data)
        print(f"Downloaded base64 image: {image_name}")
    else:
        response = requests.get(url)
        if response.status_code == 200:
            with open(os.path.join(folder_path, image_name), 'wb') as f:
                f.write(response.content)
            print(f"Downloaded image: {image_name}")
        else:
            print(f"Failed to download image: {url}")

def scrape_images(celebrity_name, num_images):
    global scraping_progress
    scraping_progress = 0
    metadata = load_metadata()
    query = celebrity_name + " celebrity"
    headers = {"User-Agent": random.choice(user_agents)}
    image_urls = []
    page = 1

    while len(image_urls) < num_images:
        search_url = f"https://www.bing.com/images/search?q={query}&first={page * 10}"
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        for a in soup.find_all("a", {"class": "iusc"}):
            try:
                img_json = eval(a["m"])
                image_urls.append(img_json["murl"])
                if len(image_urls) >= num_images:
                    break
            except Exception as e:
                print(f"Skipping image due to error: {e}")
                continue
        page += 1

    create_folder_if_not_exists(RAW_DATASET_DIR)
    create_folder_if_not_exists(METADATA_DIR)
    celebrity_folder = os.path.join(RAW_DATASET_DIR, celebrity_name.replace(" ", "_").lower())
    create_folder_if_not_exists(celebrity_folder)

    if celebrity_name not in metadata:
        metadata[celebrity_name] = []

    valid_images_downloaded = 0
    for i, img_url in enumerate(image_urls):
        try:
            image_name = f"Raw_{valid_images_downloaded + 1}.jpg"
            file_path = os.path.join(celebrity_folder, image_name)
            download_image(img_url, celebrity_folder, image_name)
            if file_path not in metadata[celebrity_name]:
                metadata[celebrity_name].append(file_path)
            valid_images_downloaded += 1
            scraping_progress = int((valid_images_downloaded / num_images) * 100)
            print(f"Progress: {scraping_progress}%")
        except Exception as e:
            print(f"Skipping image {i + 1} due to error: {e}")

    scraping_progress = 100
    print("Scraping complete")
    save_metadata(metadata)

def get_scraping_progress():
    global scraping_progress
    return scraping_progress

def rebuild_metadata():
    metadata = {}
    for celeb_folder in os.listdir(RAW_DATASET_DIR):
        celeb_path = os.path.join(RAW_DATASET_DIR, celeb_folder)
        if os.path.isdir(celeb_path):
            image_files = [os.path.join(celeb_path, f) for f in os.listdir(celeb_path) if f.endswith('.jpg')]
            metadata[celeb_folder] = image_files
    save_metadata(metadata)
    print("Metadata rebuilt successfully.")
