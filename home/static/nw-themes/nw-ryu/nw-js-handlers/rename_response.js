if (window.history.replaceState) {
    window.history.replaceState(null, null, window.location.href);
}

$(document).ready(function () {
    // Mostrar mensaje de cancelación si está presente en el backend
    const cancelMessage = $("#rename-response").data("cancel-message");
    if (cancelMessage) {
        $("#rename-response").html(cancelMessage).hide().slideDown();
    }

    // Manejar clics en el botón de renombrar
    $('.rename-button').on('click', function (e) {
        e.preventDefault();
        $("#rename-response").empty();

        const button = $(this);
        const originalText = button.html();
        const data = $("#nw-rename-form").serialize();

        // Confirmar antes de proceder con el pago
        const conf = confirm("¿Estás seguro de renombrar al personaje seleccionado?");
        if (!conf) return;

        // Cambiar texto del botón mientras procesa
        changeButton(button, 'Procesando pago...');

        $.ajax({
            type: 'POST',
            url: '', // URL para manejar el POST
            data: data,
            dataType: 'json',
            success: function (response) {
                if (response.success) {
                    // Verificar que Stripe está cargado
                    if (typeof Stripe === 'undefined') {
                        console.error("Stripe.js no está cargado.");
                        $("#rename-response").append('<span class="red-form-response">Error al cargar Stripe. Intente nuevamente más tarde.</span>').hide().slideDown();
                        restoreButton(button, originalText);
                        return;
                    }

                    // Redirigir a Stripe Checkout
                    const stripe = Stripe(response.stripe_public_key);
                    stripe.redirectToCheckout({ sessionId: response.session_id }).then(function (result) {
                        if (result.error) {
                            $("#rename-response").append('<span class="red-form-response">' + result.error.message + '</span>').hide().slideDown();
                            restoreButton(button, originalText);
                        }
                    });
                } else {
                    // Mostrar mensaje de error del backend
                    $("#rename-response").append(response.message).hide().slideDown();
                    restoreButton(button, originalText);
                }
            },
            error: function () {
                $("#rename-response").append('<span class="red-form-response">Error inesperado. Por favor, intente más tarde.</span>').hide().slideDown();
                restoreButton(button, originalText);
            }
        });
    });
});

// Función para cambiar el texto del botón y desactivarlo
function changeButton(button, text) {
    button.html(text);
    button.prop("disabled", true);
}

// Función para restaurar el texto y habilitar el botón
function restoreButton(button, originalText) {
    button.html(originalText);
    button.prop("disabled", false);
}
