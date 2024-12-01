$(function() {
    $('.unstuck-button').on('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        $("#unstuck-response").empty();

        var button = $(this);
        var originalText = button.html();
        var data = $("#nw-unstuck-form").serialize();

        button.html("Desbloqueando...");
        button.prop("disabled", true);

        $.ajax({
            type: 'POST',
            url: '',
            data: data,
            dataType: 'json',
            success: function(data) {
                $("#unstuck-response").html(data.message).hide().slideDown();

                if (data.success) {
                    button.html("Desbloqueado");
                    setTimeout(function() {
                        $("#nw-unstuck-form")[0].reset();
                        button.html(originalText);
                        button.prop("disabled", false);
                    }, 5000);
                } else {
                    button.html(originalText);
                    button.prop("disabled", false);
                }
            },
            error: function() {
                $("#unstuck-response").html('<span class="red-form-response">Algo ha salido mal. Inténtelo más tarde.</span>');
                button.html(originalText);
                button.prop("disabled", false);
            }
        });
    });
});
