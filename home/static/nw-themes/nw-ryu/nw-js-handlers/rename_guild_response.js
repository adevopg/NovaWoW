if (window.history.replaceState) {
    window.history.replaceState(null, null, window.location.href);
};

$(function(){
    $(".toggle-token").click(function() {
        $(this).toggleClass("fa-eye fa-eye-slash");
        var type = $(this).hasClass("fa-eye-slash") ? "text" : "password";
         $("#security-token").attr("type", type);
    });
});

function doRefresh() {
    $("#nw-rename-guild-form").load(document.URL + " #nw-rename-guild-form>*", function(){
        $.getScript('nw-js-handlers/rename_guild_response.js');
    });
}

$(function(){
    $('select').on('change', function(){
        var select = $(this);

        select.css('color', select.children('option:selected').css('color'));
    });
});

$(function(){
    $('.rename-guild-button').on('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        $("#rename-guild-response").empty();

        var button = $(this);
        var buttonoriginal = button.html();
        var bValue = button.data('id');
        var data = {renameguild : bValue};
        data = $("#nw-rename-guild-form").serialize() + '&' + $.param(data);

        var conf = confirm("¿Estás seguro de renombrar la hermandad seleccionada?");

        if (conf === true) {
            changeButton(button, 'Renombrando hermandad');

            $.ajax({
                type: 'POST',
                url: '',
                data: data,
                dataType: 'json',
                success: function(data) {
                    $("#rename-guild-response").append(data.message).hide().slideDown();

                    if (data.success === true) {
                        button.html("Hermandad renombrada");
                        button.css("color","#d79602");
                        setTimeout(function() {
                            $("#nw-rename-guild-form")[0].reset();
                            restoreButton(button, buttonoriginal);
                            doRefresh();
                        }, 5000);
                    }
                    else {
                        setTimeout(function() {
                            $("#rename-guild-response").slideUp( function() {
                            $("#rename-guild-response").empty();
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
        };
    });
});
