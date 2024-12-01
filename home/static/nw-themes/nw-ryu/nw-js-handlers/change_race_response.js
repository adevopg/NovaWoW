if (window.history.replaceState) {
    window.history.replaceState(null, null, window.location.href);
}

function doRefresh() {
    $("#nw-change-race-form").load(document.URL + " #nw-change-race-form>*", function () {
        $.getScript('nw-js-handlers/change_race_response.js');
    });
}

$(function () {
    $('select').on('change', function () {
        var select = $(this);
        select.css('color', select.children('option:selected').css('color'));
    });
});

$(function () {
    $('.change-race-button').on('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        $("#change-race-response").empty();

        var button = $(this);
        var buttonoriginal = button.html();
        var data = $("#nw-change-race-form").serialize();

        var conf = confirm("¿Estás seguro de cambiar de raza al personaje seleccionado?");
        if (conf === true) {
            changeButton(button, 'Procesando pago...');

            $.ajax({
                type: 'POST',
                url: '', // La URL para manejar la solicitud POST
                data: data,
                dataType: 'json',
                success: function (response) {
                    if (response.success) {
                        // Verificar si Stripe.js está disponible
                        if (typeof Stripe === 'undefined') {
                            console.error("Stripe.js no está cargado.");
                            $("#change-race-response").append('<span class="red-form-response">Error al cargar Stripe. Intente nuevamente más tarde.</span>').hide().slideDown();
                            restoreButton(button, buttonoriginal);
                            return;
                        }

                        // Inicializar Stripe con la clave pública
                        var stripe = Stripe(response.stripe_public_key);

                        // Redirigir al checkout de Stripe
                        stripe.redirectToCheckout({
                            sessionId: response.session_id
                        }).then(function (result) {
                            if (result.error) {
                                $("#change-race-response").append('<span class="red-form-response">' + result.error.message + '</span>').hide().slideDown();
                                restoreButton(button, buttonoriginal);
                            }
                        });
                    } else {
                        $("#change-race-response").append(response.message).hide().slideDown();
                        restoreButton(button, buttonoriginal);
                    }
                },
                error: function () {
                    setTimeout(function () {
                        alert("Algo ha salido mal. Por favor intente más tarde");
                        window.location.reload();
                    }, 2000);
                }
            });
        }
    });
});
