document.addEventListener('DOMContentLoaded', function() {
    const useOurDatasetBtn = document.getElementById('useOurDatasetBtn');
    const useOpenSourceDatasetBtn = document.getElementById('useOpenSourceDatasetBtn');
    const ourDatasetOptions = document.getElementById('ourDatasetOptions');
    const faceDetectionSection = document.getElementById('faceDetectionSection');
    const overallProgressBar = document.getElementById('overall-progress-bar');
    const overallProgressText = document.getElementById('overall-message');

    useOurDatasetBtn.addEventListener('click', function() {
        ourDatasetOptions.style.display = 'block';
        useOurDatasetBtn.classList.add('btn-success');
        useOurDatasetBtn.classList.remove('btn-primary');
        useOpenSourceDatasetBtn.classList.add('btn-outline-light');
        useOpenSourceDatasetBtn.classList.remove('btn-primary');
    });

    useOpenSourceDatasetBtn.addEventListener('click', function() {
        window.location.href = '/face_detection/use_opensource_dataset';
    });

    document.getElementById('extractFacesBtn').addEventListener('click', function() {
        faceDetectionSection.style.display = 'block';
        loadCelebrityFolders();
    });

    document.getElementById('startFaceDetectionAllBtn').addEventListener('click', function() {
        startFaceDetectionAll();
    });

    function loadCelebrityFolders() {
        fetch('/face_detection/get_celebrity_folders')
            .then(response => response.json())
            .then(data => {
                const celebrityFoldersList = document.getElementById('celebrityFoldersList');
                celebrityFoldersList.innerHTML = '';
                data.folders.forEach(function(name) {
                    const li = document.createElement('li');
                    li.className = 'list-group-item bg-dark text-light';
                    li.dataset.celebrity = name;
                    li.innerHTML = `
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="celebrity-name">${name}</span>
                            <button class="btn btn-primary btn-sm start-face-detection">
                                <i class="fas fa-play-circle me-2"></i>Start
                            </button>
                        </div>
                        <div class="folder-actions mt-2" style="display: none;">
                            <div class="progress" style="height: 20px;">
                                <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: 0%;" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">0%</div>
                            </div>
                            <div class="reprocess-options mt-2" style="display: none;">
                                <p>Processed images already exist. Do you wish to re-extract the faces?</p>
                                <button class="btn btn-warning btn-sm reprocess-yes">Yes</button>
                                <button class="btn btn-secondary btn-sm reprocess-skip">Skip</button>
                            </div>
                        </div>`;
                    celebrityFoldersList.appendChild(li);
                });
            });
    }

    document.getElementById('celebrityFoldersList').addEventListener('click', function(event) {
        const target = event.target;

        if (target.classList.contains('start-face-detection')) {
            const celebrityFolder = target.closest('li').dataset.celebrity;
            checkProcessed(celebrityFolder, target);
        }

        if (target.classList.contains('reprocess-yes')) {
            const celebrityFolder = target.closest('li').dataset.celebrity;
            startFaceDetection(celebrityFolder, true);
        }

        if (target.classList.contains('reprocess-skip')) {
            const reprocessOptions = target.closest('.reprocess-options');
            if (reprocessOptions) {
                reprocessOptions.style.display = 'none';
            }
        }
    });

    function checkProcessed(celebrityFolder, target) {
        fetch(`/face_detection/check_processed?celebrity=${celebrityFolder}`)
            .then(response => response.json())
            .then(data => {
                const folderActions = target.closest('li').querySelector('.folder-actions');
                const reprocessOptions = folderActions.querySelector('.reprocess-options');
                if (data.processed) {
                    reprocessOptions.style.display = 'block';
                } else {
                    startFaceDetection(celebrityFolder);
                }
                folderActions.style.display = 'block';
            });
    }

    function startFaceDetection(celebrityFolder, reprocess = false) {
        const progressBar = document.querySelector(`[data-celebrity="${celebrityFolder}"] .progress-bar`);
        
        fetch('/face_detection/start_face_detection', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ celebrity_name: celebrityFolder, reprocess: reprocess }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'started') {
                updateProgress(celebrityFolder);
            }
        });
    }

    function startFaceDetectionAll() {
        overallProgressBar.style.display = 'block';

        fetch('/face_detection/start_face_detection_all', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'started') {
                updateProgress();
            }
        });
    }

    function updateProgress(celebrityFolder = null) {
        const interval = setInterval(function() {
            fetch('/face_detection/progress_data')
                .then(response => response.json())
                .then(data => {
                    const progress = data.progress;
                    if (celebrityFolder) {
                        const progressBar = document.querySelector(`[data-celebrity="${celebrityFolder}"] .progress-bar`);
                        if (progressBar) {
                            progressBar.style.width = `${progress}%`;
                            progressBar.innerText = `${progress}%`;
                        }
                    } else {
                        overallProgressBar.style.width = `${progress}%`;
                        overallProgressBar.innerText = `${progress}%`;
                        overallProgressText.innerText = `Overall Progress: ${progress}%`;
                    }
                    if (progress >= 100) {
                        clearInterval(interval);
                    }
                });
        }, 1000);
    }
});