from flask import Flask, render_template
from flask_cors import CORS

# Import your blueprints
from app.blueprints.image_scraper.routes import image_scraper_bp
from app.blueprints.face_detection.routes import face_detection_bp
from app.blueprints.model_training.routes import model_training_bp
from app.blueprints.model_testing.routes import model_testing_bp

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Register blueprints
    app.register_blueprint(image_scraper_bp, url_prefix='/image_scraper')
    app.register_blueprint(face_detection_bp, url_prefix='/face_detection')
    app.register_blueprint(model_training_bp, url_prefix='/model_training')
    app.register_blueprint(model_testing_bp, url_prefix='/model_testing')

    @app.route('/')
    def home():
        return render_template('index.html')

    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)