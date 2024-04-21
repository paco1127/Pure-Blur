// content.js
let classes; // Declare classes at a higher scope

chrome.storage.local.get('selectedClasses', function(data) {
    const images = document.getElementsByTagName('img');

    // Placeholder image URL from the Chrome extension's assets
    const placeholderImageURL = chrome.runtime.getURL('wait.png');

    // Set all images to the placeholder and store the original src
    Array.prototype.forEach.call(images, img => {
        img.dataset.originalSrc = img.src; // Store the original source in a data attribute
        img.src = placeholderImageURL; // Set to placeholder
    });

    if (data.selectedClasses) {
        classes = data.selectedClasses; // Set classes
        initiateImageProcessing(images); // Start processing images after classes are set
    } else {
        alert('No classes selected or stored');
        // Even if no classes are stored, images remain with placeholder.
    }
});

function initiateImageProcessing(images) {
    let currentIndex = 0;

    function processImage() {
        if (currentIndex >= images.length) {
            console.log("All images have been processed.");
            return; // All images have been processed
        }

        const img = images[currentIndex];
        const originalSrc = img.dataset.originalSrc; // Use the original src stored in a data attribute

        console.log('Processing image:', originalSrc);

        // Fetch the original image source, process it, and update the image src
        fetch(originalSrc)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Network response was not ok for ${originalSrc}`);
                }
                return response.blob();
            })
            .then(blob => {
                const url = new URL(originalSrc);
                const path = url.pathname;
                const filename = path.substring(path.lastIndexOf('/') + 1);
                const fileExtension = filename.substring(filename.lastIndexOf('.') + 1);

                const formData = new FormData();
                formData.append('image', blob, filename);
                classes.forEach(className => formData.append('classes[]', className));

                return fetch('http://127.0.0.1:5000/I_censor4extension', {
                    method: 'POST',
                    body: formData
                });
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Server error when processing image');
                }
                return response.json();
            })
            .then(data => {
                if (data.filename) {
                    img.src = 'http://127.0.0.1:5000/getimage?name=' + data.filename;
                } else {
                    throw new Error('No filename returned from server');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                //alert(`Error processing image: ${error.message}`);
                img.src = originalSrc; // Revert to original if there's an error
            })
            .finally(() => {
                currentIndex++;
                processImage(); // Process next image
            });
    }

    processImage(); // Start processing the first image
}