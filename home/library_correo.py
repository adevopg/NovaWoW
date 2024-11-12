import os
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def enviar_correo(subject, to_email, template, context):
    """
    Envía un correo electrónico utilizando una plantilla HTML.

    Args:
        subject (str): El asunto del correo.
        to_email (str): Dirección de correo del destinatario.
        template (str): Ruta de la plantilla HTML.
        context (dict): Contexto para renderizar la plantilla.
    """
    try:
        # Renderizar el contenido del correo desde una plantilla
        html_message = render_to_string(template, context)
        plain_message = strip_tags(html_message)
        from_email = settings.DEFAULT_FROM_EMAIL

        # Enviar el correo
        send_mail(
            subject,
            plain_message,
            from_email,
            [to_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
        return False
