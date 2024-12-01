$(function(){
    $('.transfer-button').on('click', function(e) {
        e.preventDefault();
        $("#transfer-character-response").empty();

        var button = $(this);
        var originalText = button.text();
        var data = $("#uw-transfer-character-form").serialize();

        button.text("Procesando pago...");
        button.prop("disabled", true);

        $.ajax({
            type: 'POST',
            url: '', // URL de transferencia
            data: data,
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    var stripe = Stripe(response.stripe_public_key);
                    stripe.redirectToCheckout({
                        sessionId: response.session_id
                    });
                } else {
                    $("#transfer-character-response").append(response.message).hide().slideDown();
                    button.text(originalText);
                    button.prop("disabled", false);
                }
            },
            error: function() {
                $("#transfer-character-response").append('<span class="red-form-response">Error inesperado. Intente más tarde.</span>').hide().slideDown();
                button.text(originalText);
                button.prop("disabled", false);
            }
        });
    });
});
