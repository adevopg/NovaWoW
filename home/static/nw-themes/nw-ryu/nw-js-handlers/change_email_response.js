$(document).ready(function() {
    $('#nw-change-email-form').on('submit', function(e) {
        e.preventDefault(); // Evitar el envío por defecto del formulario
        $("#change-email-response").empty();

        var form = $(this);
        var button = $('.change-email-button');
        var originalText = button.html();

        button.html("Cambiando correo...");
        button.prop("disabled", true);

        $.ajax({
            type: 'POST',
            url: form.attr('action'),
            data: form.serialize(), // Serializar los datos correctamente
            dataType: 'json',
            success: function(response) {
                $("#change-email-response").html(response.message).hide().slideDown();

                if (response.success) {
                    button.html("Correo cambiado");
                } else {
                    setTimeout(function() {
                        $("#change-email-response").slideUp(function() {
                            $("#change-email-response").empty();
                            button.html(originalText);
                            button.prop("disabled", false);
                        });
                    }, 5000);
                }
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
