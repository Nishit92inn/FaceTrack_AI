// src/Face_Detection/static/js/feature_extraction.js

document.addEventListener('DOMContentLoaded', function () {
    console.log("DOM fully loaded and parsed for feature extraction");
    const startButton = document.getElementById('start-feature-extraction');
    const progressBar = document.getElementById('progress-bar');
    const progressContainer = document.getElementById('feature-extraction-progress');
    const logContainer = document.getElementById('log');
    const backButton = document.getElementById('back-to-face-detection');

    if (startButton) {
        startButton.addEventListener('click', function () {
            console.log("Start feature extraction button clicked");
            fetch('/face_detection/start_feature_extraction', {
                method: 'POST',
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'started') {
                    console.log("Feature extraction started on server");
                    progressContainer.style.display = 'block';
                    startButton.disabled = true;
                    let progressInterval = setInterval(() => {
                        fetch('/face_detection/feature_extraction_progress')
                            .then(response => response.json())
                            .then(data => {
                                console.log("Feature extraction progress data received", data);
                                progressBar.style.width = data.progress + '%';
                                progressBar.setAttribute('aria-valuenow', data.progress);
                                progressBar.textContent = data.progress + '%';
                                logContainer.innerHTML = data.log;
                                if (data.progress >= 100) {
                                    clearInterval(progressInterval);
                                    startButton.disabled = false;
                                }
                            });
                    }, 1000);
                } else {
                    console.error("Failed to start feature extraction on server", data);
                }
            })
            .catch(error => {
                console.error("Error in starting feature extraction", error);
            });
        });
    }

    if (backButton) {
        backButton.addEventListener('click', function () {
            console.log("Back button clicked");
            window.location.href = "/face_detection";
        });
    }
});