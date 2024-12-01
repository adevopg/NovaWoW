$(function(){
    $('.gold-button').on('click', function(e) {
        e.preventDefault();
        $("#gold-response").empty();

        var button = $(this);
        var originalText = button.html();
        var data = $("#uw-gold-form").serialize();

        button.html('Procesando pago...');
        button.prop('disabled', true);

        $.ajax({
            type: 'POST',
            url: '',
            data: data,
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    var stripe = Stripe(response.stripe_public_key);
                    stripe.redirectToCheckout({ sessionId: response.session_id });
                } else {
                    $("#gold-response").append(response.message).hide().slideDown();
                    button.html(originalText);
                    button.prop('disabled', false);
                }
            },
            error: function() {
                $("#gold-response").append('<span class="red-form-response">Error inesperado. Por favor, intente más tarde.</span>').hide().slideDown();
                button.html(originalText);
                button.prop('disabled', false);
            }
        });
    });
});
