# ac_soap.py
import requests
import base64
from django.conf import settings

def execute_soap_command(command):
    """
    Ejecuta un comando en el servidor AzerothCore usando SOAP.

    Parameters:
    - command (str): El comando a ejecutar, por ejemplo, ".additem 3200"

    Returns:
    - str: La respuesta del servidor si el comando se ejecuta correctamente.
    - None: Si ocurre algún error durante la ejecución.
    """
    try:
        # Crear la carga SOAP
        soap_command = f'''<?xml version="1.0" encoding="utf-8"?>
        <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns1="{settings.AC_SOAP_URN}">
            <SOAP-ENV:Body>
                <ns1:executeCommand>
                    <command>{command}</command>
                </ns1:executeCommand>
            </SOAP-ENV:Body>
        </SOAP-ENV:Envelope>'''

        # Autenticación básica usando las credenciales en settings.py
        auth_header = f"Basic {base64.b64encode(f'{settings.AC_SOAP_USER}:{settings.AC_SOAP_PASSWORD}'.encode()).decode()}"

        headers = {
            'Authorization': auth_header,
            'Content-Type': 'application/xml'
        }

        # Realizar la solicitud SOAP al servidor de AzerothCore
        response = requests.post(settings.AC_SOAP_URL, data=soap_command, headers=headers, timeout=5)

        # Verificar si la respuesta fue exitosa
        if response.status_code == 200:
            return response.text
        else:
            print(f"[ERROR] Comando SOAP fallido: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"[EXCEPCIÓN] Error de conexión con el servidor SOAP: {str(e)}")
        return None
    except Exception as e:
        print(f"[EXCEPCIÓN] Error inesperado al ejecutar el comando SOAP: {str(e)}")
        return None
