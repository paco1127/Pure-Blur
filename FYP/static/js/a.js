$(document).ready(function () {

    var censorshipInProgress = false; // Flag to track if censorship is in progress
    $('.p2').css('display','none');
    $('.p3').css('display','none');
    $('.p4').css('display','none');

    $('.process').on('click', function () {
        $('.p1').css('display','none');
        $('.p2').css('display','block');
    });




    $('form').on('submit', function (event) {
        event.preventDefault();

        // Check if censorship is already in progress
        if (censorshipInProgress) {
            return; // Exit the function if censorship is already in progress
        }

        censorshipInProgress = true; // Set the flag to indicate censorship is in progress

        var formData = new FormData($(this)[0]);
        $('.p2').css('display','none');
        $('.p3').css('display','block');

        $.ajax({
            url: '/A_censor',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {

                var audio = $("#result")[0]
                Fname = response
                var audioUrl = "/getaudio?name=" + Fname;
                $('.p3').css('display','none');
                $('.p4').css('display','block');
                $('#down').attr('href', audioUrl);
                $('#result').attr('src', audioUrl);
                audio.innerHTML = '<source src="' + audioUrl + '" type="audio/mpeg">';
                $('#result').css('display', 'block');
                audio.load();
            },
            error: function () {
                censorshipInProgress = false; // Reset the flag in case of an error
                alert('An error occurred during audio censorship.');
            }
        });

        return false;
    });
});
function sendWords() {
    var words = document.getElementById("wordsInput").value;
    var xhr = new XMLHttpRequest();
    var url = "/addfoul?word=" + encodeURIComponent(words);
    xhr.open("GET", url, true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
            var response = JSON.parse(xhr.responseText);
            alert(" " + response.message);
            $('.next').click();
        }
    };
    xhr.send();
}
