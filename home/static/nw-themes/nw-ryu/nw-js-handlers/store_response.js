$(document).ready(function() {
    $('.add-to-cart').on('click', function() {
        var itemId = $(this).data('item-id');
        $.post('/store/add_to_cart/', {item_id: itemId}, function(response) {
            alert(response.message);
            location.reload();
        });
    });

    $('.remove-from-cart').on('click', function() {
        var cartId = $(this).data('cart-id');
        $.post('/store/remove_from_cart/', {cart_id: cartId}, function(response) {
            alert(response.message);
            location.reload();
        });
    });

    $('#checkout-button').on('click', function() {
        $.post('/store/checkout/', {}, function(response) {
            if (response.success) {
                var stripe = Stripe(response.stripe_public_key);
                stripe.redirectToCheckout({ sessionId: response.session_id });
            } else {
                alert(response.message);
            }
        });
    });
});
