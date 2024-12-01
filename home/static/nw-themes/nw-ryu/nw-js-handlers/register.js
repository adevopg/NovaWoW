$(function() {
    // Manejar el envío del formulario de creación de cuenta
    $('#nw-create-form').on('submit', function(e) {
        e.preventDefault();
        const data = $(this).serialize();
        const createResponse = $("#create-response");

        $.ajax({
            type: 'POST',
            url: '',
            data: data,
            dataType: 'json',
            success: function(response) {
                createResponse.hide().empty();
                if (response.success) {
                    createResponse.html(`<span class="ok-form-response">${response.message}</span>`).slideDown();
                } else {
                    createResponse.html(`<span class="red-form-response">${response.message}</span>`).slideDown();
                }
            },
            error: function() {
                createResponse.html('<span class="red-form-response">Error en el servidor. Inténtalo de nuevo más tarde.</span>').slideDown();
            }
        });
    });

    // Manejar el estado del botón según el checkbox
    $('#accept-terms-cookies').on('change', function() {
        $('#create-account-btn').prop('disabled', !this.checked);
    });
});

// Función para habilitar/deshabilitar el botón según el estado del checkbox (alternativa sin jQuery)
function click_checkbox() {
    const checkbox = document.getElementById('accept-terms-cookies');
    const createButton = document.getElementById('create-account-btn');
    createButton.disabled = !checkbox.checked;
}
