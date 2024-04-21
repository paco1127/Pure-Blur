$(document).ready(function () {
    var censorshipInProgress = false; // Flag to track if censorship is in progress
    $('.p2').css('display','none');
    $('.p3').css('display','none');
    
    $('.next').click(function(){
        $('.p1').css('display','none');
        $('.p2').css('display','block');
    })

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
            url: '/I_censor',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                $('.p2').css('display','none');
                $('.p3').css('display','block');
                censorshipInProgress = false; // Reset the flag after censorship is completed
                Fname = response
                    var imageUrl = "/getimage?name=" + Fname;
                    $("#censored-image").attr("src", imageUrl);
                    $("#censored-image").attr("style", "display: block; width: 300px; height: 300px; object-fit: cover;");
                    $('#down').attr('href', imageUrl);
                
            },
            error: function () {
                censorshipInProgress = false; // Reset the flag in case of an error
                alert('An error occurred during image censorship.');
            }
        });

        return false;
    });
});