$(document).ready(function() {
    $('.vote-button').each(function() {
        var button = $(this);
        var remainingTime = button.data('remaining-time');
        
        if (remainingTime) {
            startCooldownTimer(button, remainingTime);
        }
    });

    $('.vote-button').on('click', function(e) {
        e.preventDefault();
        $("#voteResponse").empty();

        var button = $(this);
        var voteUrl = button.data('url').trim();
        var data = { vote: voteUrl };

        button.html("Votando...");
        button.prop("disabled", true);

        var otherWindow = window.open(voteUrl, "_blank");
        otherWindow.opener = null;

        $.ajax({
            type: 'POST',
            url: '',
            data: data,
            dataType: 'json',
            success: function(response) {
                $("#voteResponse").html(response.message).hide().slideDown();

                if (response.success) {
                    button.html("Votado");
                    button.prop("disabled", true);
                } else {
                    button.html("Votar");
                    button.prop("disabled", false);
                }

                // Ocultar el mensaje después de 5 segundos
                setTimeout(function() {
                    $("#voteResponse").slideUp(function() {
                        $("#voteResponse").empty();
                    });
                }, 5000);
            },
            error: function() {
                $("#voteResponse").html('<span class="red-form-response">Algo ha salido mal. Por favor, inténtalo más tarde.</span>');

                // Ocultar el mensaje después de 5 segundos en caso de error
                setTimeout(function() {
                    $("#voteResponse").slideUp(function() {
                        $("#voteResponse").empty();
                    });
                }, 5000);
            }
        });
    });
});

function startCooldownTimer(button, remainingTime) {
    var interval = setInterval(function() {
        if (remainingTime <= 0) {
            clearInterval(interval);
            button.html("Votar");
            button.prop("disabled", false);
        } else {
            var hours = Math.floor(remainingTime / 3600);
            var minutes = Math.floor((remainingTime % 3600) / 60);
            button.html(`Espera ${hours}h ${minutes}m`);
            remainingTime--;
        }
    }, 1000);
}
