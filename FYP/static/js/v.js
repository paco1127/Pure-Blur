function getVideoDuration() {
    var fileInput = document.getElementById('videoFile');
    var file = fileInput.files[0];

    var video = document.createElement('video');
    video.preload = 'metadata';
    var duration=0;
    var framePSec = 0.16;//process time for each frame

    video.onloadedmetadata = function () {
        window.URL.revokeObjectURL(video.src);
        duration = video.duration;
        totaltime = 30 * framePSec * duration
        document.getElementById('time').innerHTML = "Estimated Time: " + Math.floor(totaltime*100)/100 + " seconds";
    };
    video.src = URL.createObjectURL(file);
}

$(document).ready(function () {
    $('.p2').css('display', 'none');
    $('.p3').css('display', 'none');
    $('.p4').css('display', 'none');
    $('.next').click(function () {
        $('.p1').css('display', 'none');
        $('.p2').css('display', 'block');
    })
    var censorshipInProgress = false; // Flag to track if censorship is in progress

    $('#form').on('submit', function (event) {
        event.preventDefault();
        var formData = new FormData($(this)[0]);

        $('.p2').css('display', 'none');
        $('.p3').css('display', 'block');

        getVideoDuration();





        // Check if censorship is already in progress
        if (censorshipInProgress) {
            return; // Exit the function if censorship is already in progress
        }

        censorshipInProgress = true; // Set the flag to indicate censorship is in progress

        $.ajax({
            url: '/V_censor',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                censorshipInProgress = false; // Reset the flag after censorship is completed

                
                    alert('Video censorship completed.');
                    $('.p3').css('display', 'none');
                    $('.p4').css('display', 'block');
                    Fname = response
                    var videoUrl = "/getvideo?name=" + Fname;
                    $("#video").attr("src", videoUrl);

                    //$("#video").attr("src", videoUrl);

                    $('#down').attr('href', videoUrl);
                
            },
            error: function () {
                censorshipInProgress = false; // Reset the flag in case of an error
                alert('An error occurred during video censorship.');
            }
        });

        return false;
    });
});