document.getElementById('blur-form').addEventListener('submit', function(event) {
  event.preventDefault();  // Prevent actual form submission

  // Collect all checked checkboxes
  const selectedClasses = Array.from(document.querySelectorAll('input[name="classes[]"]:checked')).map(el => el.value);

  // Save the selected classes in local storage or send them to the content script
  chrome.storage.local.set({ 'selectedClasses': selectedClasses }, function() {
      alert('Successfully saved parameters.');
  });
});

document.addEventListener('DOMContentLoaded', function() {
  chrome.storage.local.get('selectedClasses', function(data) {
    if (data.selectedClasses) {
      data.selectedClasses.forEach(function(className) {
        let checkbox = document.querySelector(`input[name="classes[]"][value="${className}"]`);
        if (checkbox) {
          checkbox.checked = true;
        }
      });
    }
  });
});