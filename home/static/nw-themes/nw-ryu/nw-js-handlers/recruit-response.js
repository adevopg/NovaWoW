$(function() {
    if (window.history.replaceState) {
        window.history.replaceState(null, null, window.location.href);
    }

    $('.reward-form').on('submit', function(e) {
        e.preventDefault();
        const form = $(this);
        const button = form.find('button[type="submit"]');
        const originalButtonText = button.html();
        const recruitResponse = $("#recruit-response");
        const rewardRow = form.closest('tr');
        const rewardsCounter = $("#claimed-rewards-counter");

        // Serializar datos del formulario
        const data = form.serialize();

        changeButton(button, 'Reclamando...');

        $.ajax({
            type: 'POST',
            url: '',
            data: data,
            dataType: 'json',
            success: function(response) {
                recruitResponse.hide().empty();

                if (response.success) {
                    recruitResponse.html(`<span class="ok-form-response">${response.message}</span>`).slideDown();

                    // Actualizar la fila y deshabilitar el formulario
                    rewardRow.find('.reward-action').html(`<span class="ok-form-response">${response.message}</span>`);

                    // Actualizar el contador de recompensas
                    if (response.claimed_count !== undefined) {
                        rewardsCounter.text(`${response.claimed_count}/6`);
                    }
                } else {
                    recruitResponse.html(`<span class="red-form-response">${response.message}</span>`).slideDown();
                }

                setTimeout(function() {
                    restoreButton(button, originalButtonText);
                }, 3000);
            },
            error: function() {
                recruitResponse.html('<span class="red-form-response">Error en el servidor. Inténtalo de nuevo más tarde.</span>').slideDown();
                restoreButton(button, originalButtonText);
            }
        });
    });
});

function changeButton(button, text) {
    button.html(text);
    button.prop("disabled", true);
}

function restoreButton(button, originalText) {
    button.html(originalText);
    button.prop("disabled", false);
}
