from flask import Blueprint, render_template, request, jsonify
import threading
from .image_scraper import scrape_images, get_scraping_progress, rebuild_metadata

image_scraper_bp = Blueprint(
    'image_scraper', __name__,
    template_folder='templates',
    static_folder='static'
)

@image_scraper_bp.route('/')
def image_scraper():
    return render_template('image_scraper.html')

@image_scraper_bp.route('/start_scraping', methods=['POST'])
def start_scraping():
    celebrity_name = request.form['celebrity_name']
    num_images = int(request.form['num_images'])

    # Start the image scraping in a separate thread
    threading.Thread(target=scrape_images, args=(celebrity_name, num_images)).start()

    return jsonify({"status": "started"})

@image_scraper_bp.route('/progress_data')
def progress_data():
    return jsonify({"progress": get_scraping_progress()})

@image_scraper_bp.route('/rebuild_metadata', methods=['POST'])
def rebuild_metadata_route():
    rebuild_metadata()
    return jsonify({"message": "Metadata rebuilt successfully"})