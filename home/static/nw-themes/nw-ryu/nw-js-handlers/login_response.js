// Evitar el reenvío del formulario si la página se recarga
if (window.history.replaceState) {
    window.history.replaceState(null, null, window.location.href);
}

// Mostrar/ocultar la contraseña
$(function() {
    $(".toggle-password").click(function() {
        $(this).toggleClass("fa-eye fa-eye-slash");
        const type = $(this).hasClass("fa-eye-slash") ? "text" : "password";
        $("#password").attr("type", type);
    });
});

// Manejar el envío del formulario de inicio de sesión
$(function() {
    $('.login-button').on('click', function(e) {
        e.preventDefault();
        e.stopPropagation();

        const button = $(this);
        const buttonOriginal = button.html();
        const username = $("#username").val().trim();
        const password = $("#password").val().trim();
        const loginResponse = $("#login-response");

        // Cambiar el texto del botón a "Conectando..."
        changeButton(button, 'Conectando');

        // Validar si los campos están vacíos
        if (username === "" || password === "") {
            loginResponse.html('<span class="red-form-response">Por favor rellene todos los campos.</span>');
            loginResponse.hide().slideDown();

            // Limpiar el mensaje y restaurar el botón después de 5 segundos
            setTimeout(function() {
                loginResponse.slideUp(function() {
                    loginResponse.empty();
                    restoreButton(button, buttonOriginal);
                });
            }, 5000);
            return;
        }

        // Serializar datos para el envío
        const bValue = button.data('id');
        let data = { login: bValue };
        data = $("#uw-login-form").serialize() + '&' + $.param(data);

        $.ajax({
            type: 'POST',
            url: '',
            data: data,
            dataType: 'json',
            success: function(response) {
                loginResponse.hide().empty();

                if (response.success === true) {
                    // Si el inicio de sesión es exitoso
                    button.html("Conectado");
                    button.css("color", "#d79602");

                    // Mostrar mensaje de conexión exitosa
                    loginResponse.html('<span class="ok-form-response">Conexión exitosa.<br />Redirigiendo...</span>');
                    loginResponse.hide().slideDown();

                    // Redirigir después de 3 segundos
                    setTimeout(function() {
                        window.location = "my-account";
                    }, 3000);
                } else if (response.alert === true) {
                    button.html("Sancionado");
                } else if (response.locked === true) {
                    button.html("Seguridad");
                } else {
                    // Mostrar mensaje para credenciales incorrectas
                    loginResponse.html('<span class="red-form-response">Nombre de usuario / Contraseña incorrectos.</span>');
                    loginResponse.hide().slideDown();

                    // Restaurar el botón y ocultar el mensaje después de 5 segundos
                    setTimeout(function() {
                        loginResponse.slideUp(function() {
                            loginResponse.empty();
                            restoreButton(button, buttonOriginal);
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

// Función para cambiar el estado del botón a "Conectando"
function changeButton(button, text) {
    button.html(text);
    button.prop("disabled", true);
    button.css({
        "color": "rgb(177, 153, 127)",
        "background-color": "rgba(255, 255, 255, 0.1)",
        "cursor": "default"
    });
}

// Función para restaurar el estado original del botón
function restoreButton(button, originalText) {
    button.html(originalText);
    button.prop("disabled", false);
    button.css({
        "color": "",
        "background-color": "",
        "cursor": ""
    });
}