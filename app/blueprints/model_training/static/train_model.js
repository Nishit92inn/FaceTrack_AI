document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('training-form');
    const progressBar = document.getElementById('progress-bar');
    const statusDiv = document.getElementById('training-status');
    const logDiv = document.getElementById('training-log');

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        startTraining();
    });

    function startTraining() {
        const formData = new FormData(form);
        const num_epochs = formData.get('num_epochs');
        const batch_size = formData.get('batch_size');

        // Disable the form
        form.querySelectorAll('input, button').forEach(el => el.disabled = true);

        fetch('/model_training/start_training', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ num_epochs, batch_size })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'started') {
                statusDiv.innerHTML = '<p class="text-info"><i class="fas fa-spinner fa-spin me-2"></i>Training started...</p>';
                updateProgress(num_epochs);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            statusDiv.innerHTML = '<p class="text-danger"><i class="fas fa-exclamation-triangle me-2"></i>Error starting training. Please try again.</p>';
            // Re-enable the form
            form.querySelectorAll('input, button').forEach(el => el.disabled = false);
        });
    }

    function updateProgress(num_epochs) {
        let progressInterval = setInterval(() => {
            fetch('/model_training/training_progress')
                .then(response => response.json())
                .then(data => {
                    const progress = (data.epoch / num_epochs) * 100;
                    progressBar.style.width = `${progress}%`;
                    progressBar.setAttribute('aria-valuenow', progress);
                    progressBar.textContent = `${Math.round(progress)}%`;

                    statusDiv.innerHTML = `
                        <p><strong>Epoch:</strong> ${data.epoch} / ${num_epochs}</p>
                        <p><strong>Accuracy:</strong> ${data.accuracy}</p>
                        <p><strong>Loss:</strong> ${data.loss}</p>
                        <p><strong>Validation Accuracy:</strong> ${data.val_accuracy}</p>
                        <p><strong>Validation Loss:</strong> ${data.val_loss}</p>
                    `;

                    logDiv.innerHTML += `<p>Epoch ${data.epoch}: Accuracy: ${data.accuracy}, Loss: ${data.loss}, Validation Accuracy: ${data.val_accuracy}, Validation Loss: ${data.val_loss}</p>`;
                    logDiv.scrollTop = logDiv.scrollHeight;

                    if (data.status === 'completed') {
                        clearInterval(progressInterval);
                        statusDiv.innerHTML += `
                            <p class="text-success"><i class="fas fa-check-circle me-2"></i>Training completed.</p>
                            <p><strong>Model saved as:</strong> ${data.model_path}</p>
                            <p><strong>Training history saved as:</strong> ${data.history_path}</p>
                        `;
                        // Re-enable the form
                        form.querySelectorAll('input, button').forEach(el => el.disabled = false);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    clearInterval(progressInterval);
                    statusDiv.innerHTML += '<p class="text-danger"><i class="fas fa-exclamation-triangle me-2"></i>Error during training. Please check the logs.</p>';
                    // Re-enable the form
                    form.querySelectorAll('input, button').forEach(el => el.disabled = false);
                });
        }, 1000);
    }
});