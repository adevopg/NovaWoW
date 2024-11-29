$(document).ready(function() {
    function handleResponse(response, button, originalText) {
        $("#change-email-response").html(response.message).hide().slideDown();

        if (response.redirect_url) {
            setTimeout(function() {
                window.location.href = response.redirect_url;
            }, 2000);
            return;
        }

        if (response.success) {
            button.html("Proceso completado");
        } else {
            setTimeout(function() {
                $("#change-email-response").slideUp(function() {
                    $("#change-email-response").empty();
                    button.html(originalText);
                    button.prop("disabled", false);
                });
            }, 5000);
        }
    }

    // Manejar los enlaces de confirmación
    $('.confirm-link').on('click', function(e) {
        e.preventDefault();
        $("#change-email-response").empty();

        var button = $(this);
        var url = button.attr('href');
        var originalText = button.html();

        button.html("Verificando...");
        button.prop("disabled", true);

        $.ajax({
            type: 'GET',
            url: url,
            dataType: 'json',
            success: function(response) {
                handleResponse(response, button, originalText);
            },
            error: function(xhr, status, error) {
                console.error("Error:", error);
                console.error("Detalles:", xhr.responseText);
                $("#change-email-response").html('<span class="red-form-response">Algo ha salido mal. Inténtelo de nuevo.</span>');
                button.html(originalText);
                button.prop("disabled", false);
            }
        });
    });
});
