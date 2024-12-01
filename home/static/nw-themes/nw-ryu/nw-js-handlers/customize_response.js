if (window.history.replaceState) {
    window.history.replaceState(null, null, window.location.href);
}

$(function(){
    $('.customize-button').on('click', function(e) {
        e.preventDefault();
        $("#customize-response").empty();

        var button = $(this);
        var buttonoriginal = button.html();
        var data = $("#nw-customize-form").serialize();

        var conf = confirm("¿Estás seguro de personalizar al personaje seleccionado?");

        if (conf === true) {
            button.html("Procesando pago...");
            button.prop("disabled", true);

            $.ajax({
                type: 'POST',
                url: '', // Endpoint para manejar el POST
                data: data,
                dataType: 'json',
                success: function(response) {
                    if (response.success) {
                        var stripe = Stripe(response.stripe_public_key);

                        stripe.redirectToCheckout({
                            sessionId: response.session_id
                        }).then(function(result) {
                            if (result.error) {
                                $("#customize-response").html('<span class="red-form-response">' + result.error.message + '</span>');
                                button.html(buttonoriginal);
                                button.prop("disabled", false);
                            }
                        });
                    } else {
                        $("#customize-response").html(response.message);
                        button.html(buttonoriginal);
                        button.prop("disabled", false);
                    }
                },
                error: function() {
                    $("#customize-response").html('<span class="red-form-response">Algo salió mal. Intenta de nuevo.</span>');
                    button.html(buttonoriginal);
                    button.prop("disabled", false);
                }
            });
        }
    });
});
