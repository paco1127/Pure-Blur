document.getElementById('registrationForm').onsubmit = function(event) {
    event.preventDefault(); // Prevent the default form submission
    var username = document.forms["registrationForm"]["username"].value;
    var password = document.getElementById('password').value;
    var confirmPassword = document.getElementById('confirm_password').value;

    if (password !== confirmPassword) {
        alert('Passwords do not match!');
        return; // Stop the function if passwords do not match
    }

    // Create an AJAX request
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/register", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            alert('Registration Successful');
            window.location.href = '/login'; // Redirect to the login page
        }
    };
    xhr.send("username=" + encodeURIComponent(username) + "&password=" + encodeURIComponent(password));
};