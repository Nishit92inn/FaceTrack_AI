// src/Face_Detection/static/js/label_map.js

document.addEventListener('DOMContentLoaded', function () {
    const createLabelMapBtn = document.getElementById('createLabelMapBtn');

    createLabelMapBtn.addEventListener('click', function () {
        createLabelMap();
    });

    function createLabelMap() {
        fetch('/face_detection/create_label_map', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'Label map created') {
                console.log('Label map created');
                alert('Label map has been created successfully.');
            } else {
                console.error('Error creating label map:', data.message);
                alert('Error creating label map: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error creating label map: ' + error.message);
        });
    }
});