if (window.history.replaceState) {
    window.history.replaceState(null, null, window.location.href);
};

$(function(){
    $('.change-faction-button').on('click', function(e) {
        e.preventDefault();
        $("#change-faction-response").empty();

        var button = $(this);
        var buttonoriginal = button.html();
        var data = $("#nw-change-faction-form").serialize();

        var conf = confirm("¿Estás seguro de cambiar de facción al personaje seleccionado?");

        if (conf === true) {
            changeButton(button, 'Procesando pago...');

            $.ajax({
                type: 'POST',
                url: '', // URL actual
                data: data,
                dataType: 'json',
                success: function(response) {
                    if (response.success) {
                        var stripe = Stripe(response.stripe_public_key);
                        stripe.redirectToCheckout({ sessionId: response.session_id }).then(function(result) {
                            if (result.error) {
                                $("#change-faction-response").append('<span class="red-form-response">' + result.error.message + '</span>').hide().slideDown();
                                restoreButton(button, buttonoriginal);
                            }
                        });
                    } else {
                        $("#change-faction-response").append(response.message).hide().slideDown();
                        restoreButton(button, buttonoriginal);
                    }
                },
                error: function() {
                    $("#change-faction-response").append('<span class="red-form-response">Error inesperado. Por favor, intente más tarde.</span>').hide().slideDown();
                    restoreButton(button, buttonoriginal);
                }
            });
        }
    });
});
