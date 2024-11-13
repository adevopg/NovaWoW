$(function(){
    $('.change-password-button').on('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        $("#change-password-response").empty();

        var button = $(this);
        var originalText = button.html();
        var data = $("#nw-change-password-form").serialize();

        changeButton(button, 'Cambiando contraseña');

        $.ajax({
            type: 'POST',
            url: '',
            data: data,
            dataType: 'json',
            success: function(response) {
                $("#change-password-response").html(response.message).hide().slideDown();

                if (response.success) {
                    button.html("Contraseña cambiada").css("color", "#d79602");
                    if (response.redirect) {
                        setTimeout(function() {
                            window.location.href = '/es/log-in';
                        }, 3000);
                    }
                } else {
                    setTimeout(function() {
                        $("#change-password-response").slideUp(function() {
                            $("#change-password-response").empty();
                            restoreButton(button, originalText);
                        });
                    }, 5000);
                }
            },
            error: function() {
                alert("Algo ha salido mal. Por favor, intenta más tarde.");
                window.location.reload();
            }
        });
    });
});
