document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('uploadImageForm');
    const resultDiv = document.getElementById('predictionResult');
    const modelSelect = document.getElementById('modelSelect');
    const modelDetails = document.getElementById('modelDetails');
    const loadingIndicator = document.getElementById('loadingIndicator');

    fetch('/model_testing/get_models')
        .then(response => response.json())
        .then(data => {
            data.models.forEach(model => {
                const option = document.createElement('option');
                option.value = model;
                option.textContent = model;
                modelSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error fetching models:', error);
            resultDiv.innerHTML = '<div class="alert alert-danger">Error fetching models. Please try again later.</div>';
        });

    modelSelect.addEventListener('change', function() {
        modelDetails.style.display = this.value ? 'block' : 'none';
    });

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        resultDiv.innerHTML = '';
        loadingIndicator.style.display = 'block';

        const formData = new FormData(form);
        formData.append('model', modelSelect.value);

        fetch('/model_testing/upload_image', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            loadingIndicator.style.display = 'none';
            if (data.error) {
                resultDiv.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
            } else {
                displayResults(data);
            }
        })
        .catch(error => {
            loadingIndicator.style.display = 'none';
            console.error('Error:', error);
            resultDiv.innerHTML = '<div class="alert alert-danger">An error occurred while processing the image.</div>';
        });
    });

    function displayResults(data) {
        const { label, confidence, processing_time, top_predictions } = data;
        
        let resultsHTML = `
            <div class="card bg-dark text-light mb-4">
                <div class="card-body">
                    <h3 class="card-title">Results</h3>
                    <p><strong>Predicted Celebrity:</strong> ${label}</p>
                    <p><strong>Confidence:</strong> ${(confidence * 100).toFixed(2)}%</p>
                    <p><strong>Processing Time:</strong> ${processing_time.toFixed(3)} seconds</p>
                </div>
            </div>

            <div class="card bg-dark text-light">
                <div class="card-body">
                    <h3 class="card-title">Top 5 Predictions</h3>
                    <canvas id="predictionsChart"></canvas>
                </div>
            </div>
        `;

        resultDiv.innerHTML = resultsHTML;

        // Create chart
        const ctx = document.getElementById('predictionsChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: top_predictions.map(p => p.label),
                datasets: [{
                    label: 'Confidence',
                    data: top_predictions.map(p => p.confidence * 100),
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Confidence (%)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Top 5 Predictions'
                    }
                }
            }
        });
    }
});