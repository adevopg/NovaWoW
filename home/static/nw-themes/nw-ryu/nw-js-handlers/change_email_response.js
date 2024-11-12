if (window.history.replaceState) {
    window.history.replaceState(null, null, window.location.href);
};

$(function(){
    $(".toggle-password").click(function() {
        $(this).toggleClass("fa-eye fa-eye-slash");
        var type = $(this).hasClass("fa-eye-slash") ? "text" : "password";
         $("#password").attr("type", type);
    });
});

$(function(){
    $(".toggle-token").click(function() {
        $(this).toggleClass("fa-eye fa-eye-slash");
        var type = $(this).hasClass("fa-eye-slash") ? "text" : "password";
         $("#security-token").attr("type", type);
    });
});

$(function(){
    $('#conf-new-email').on("cut copy paste",function(e) {
      e.preventDefault();
    });
});

$(function(){
    $('.change-email-button').on('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        $("#change-email-response").empty();

        var button = $(this);
        var buttonoriginal = button.html();
        var bValue = button.data('id');
        var data = {changeemail: bValue};
        data = $("#uw-change-email-form").serialize() + '&' + $.param(data);

        changeButton(button, 'Cambiando correo');

        $.ajax({
            type: 'POST',
            url: '',
            data: data,
            dataType: 'json',
            success: function(data) {
                $("#change-email-response").append(data.message).hide().slideDown();

                if (data.success === true) {
                    button.html("Correo cambiado");
                    button.css("color","#d79602");
                }
                else {
                    setTimeout(function() {
                        $("#change-email-response").slideUp( function() {
                        $("#change-email-response").empty();
                        restoreButton(button, buttonoriginal);
                        });
                    }, 5000);
                }
            },
            error: function() {
                setTimeout(function() {
                    alert("Algo ha salido mal. Por favor intente más tarde");
                    window.location.reload();
                }, 2000);
            }
        });
    });
});