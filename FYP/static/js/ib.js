$(document).ready(function () {
    var censorshipInProgress = false; // Flag to track if censorship is in progress
    $('.p2').css('display','none');
    

    $('form').on('submit', function (event) {
        event.preventDefault();

        // Check if censorship is already in progress
        if (censorshipInProgress) {
            return; // Exit the function if censorship is already in progress
        }

        censorshipInProgress = true; // Set the flag to indicate censorship is in progress

        var formData = new FormData($(this)[0]);
        $("#censored-image").attr("src", "");

        $.ajax({
            url: '/B_censor',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {

                censorshipInProgress = false; // Reset the flag after censorship is completed
                if (response == "No blood detected in the image.") {
                    alert('No blood detected in the image.');
                    location.reload();
                }else{
                Fname = response
                    $('.p1').css('display','none');
                    $('.p2').css('display','block');
                    var imageUrl = "/getbimage?name=" + Fname;
                    $("#censored-image").attr("src", imageUrl);
                    $("#censored-image").attr("style", "display: block; width: 300px; height: 300px; object-fit: cover;");
                    $('#down').attr('href', imageUrl);
                }
                
            },
            error: function () {
                censorshipInProgress = false; // Reset the flag in case of an error
                alert('An error occurred during image censorship.');
            }
        });

        return false;
    });
});