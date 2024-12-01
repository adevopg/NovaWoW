$(document).ready(function() {
    $('.revive-button').on('click', function(e) {
        e.preventDefault();
        $("#revive-response").empty();

        var button = $(this);
        var originalText = button.html();
        var data = $("#nw-revive-form").serialize();

        button.html("Reviviendo...");
        button.prop("disabled", true);

        $.ajax({
            type: 'POST',
            url: '',
            data: data,
            dataType: 'json',
            success: function(response) {
                $("#revive-response").html(response.message).hide().slideDown();
                if (response.success) {
                    button.html("Revivido");
                    setTimeout(function() {
                        location.reload(); // Refrescar para actualizar el formulario
                    }, 5000);
                } else {
                    button.html(originalText);
                    button.prop("disabled", false);
                }
            },
            error: function(xhr, status, error) {
                $("#revive-response").html('<span class="red-form-response">Algo salió mal. Intente nuevamente.</span>');
                button.html(originalText);
                button.prop("disabled", false);
            }
        });
    });
});
