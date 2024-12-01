$(function() {
    $('.sec-token-button').on('click', function(e) {
        e.preventDefault();

        var button = $(this);
        var originalText = button.html();
        var data = $("#nw-sec-token-form").serialize();

        // Cambiar el texto del botón a "Solicitando token"
        changeButton(button, 'Solicitando token');

        $.ajax({
            type: 'POST',
            url: '',
            data: data,
            dataType: 'json',
            success: function(response) {
                $("#sec-token-response").html(response.message).hide().slideDown();
                
                if (response.success) {
                    // Actualizar la fecha del token en la página si se ha generado correctamente
                    if (response.token_date) {
                        $("#token-date").text(response.token_date);
                    }

                    // Cambiar el texto del botón a "Token enviado"
                    button.html("Token enviado").css("color", "#d79602");
                    
                    // Restablecer el botón después de 5 segundos
                    setTimeout(function() {
                        restoreButton(button, originalText);
                        $("#sec-token-response").slideUp(function() {
                            $("#sec-token-response").empty();
                        });
                    }, 5000);
                } else {
                    // Restablecer el botón y ocultar el mensaje en caso de error
                    setTimeout(function() {
                        $("#sec-token-response").slideUp(function() {
                            $("#sec-token-response").empty();
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

function changeButton(button, text) {
    button.prop('disabled', true).html(text);
}

function restoreButton(button, originalText) {
    button.prop('disabled', false).html(originalText).css("color", "");
}
