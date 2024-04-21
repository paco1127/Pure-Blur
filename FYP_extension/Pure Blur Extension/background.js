  // background.js
chrome.runtime.onInstalled.addListener(function() {
    console.log('Extension installed');
  });
  
  chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.message === 'processImages') {
      // Inject content script to process images in the active tab
      chrome.scripting.executeScript({
        target: { tabId: request.tabId },
        files: ['content.js']
      });
    }
  });



// background.js

chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.message === 'fetchImage') {
      // Handle the message and fetch the image data
      getImageData(request.url)
        .then(imageData => {
          sendResponse({ image: imageData });
        })
        .catch(error => {
          console.error('Error fetching image data:', error);
          sendResponse({ error: 'Failed to fetch image data' });
        });
  
      // Ensure the response is sent asynchronously
      return true;
    }
  });
  
  function getImageData(imageUrl) {
    // Implement your logic to fetch the image data based on the provided imageUrl
    // This could involve using the Fetch API, XMLHttpRequest, or any other method
    // Return a Promise that resolves with the image data
    return new Promise((resolve, reject) => {
      // Example using Fetch API
      fetch(imageUrl)
        .then(response => response.blob())
        .then(blob => {
          // Process the image data as needed
          // For example, you can create a FileReader to read the image data
          const reader = new FileReader();
          reader.onloadend = function() {
            resolve(reader.result);
          };
          reader.onerror = function() {
            reject(new Error('Error reading image data'));
          };
          reader.readAsDataURL(blob);
        })
        .catch(error => {
          reject(error);
        });
    });
  }

  