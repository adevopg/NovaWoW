import socket
import hashlib
import gmpy2
import binascii
import os
import re
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.db import connections
from django.contrib import messages
from django.contrib.auth import logout
from django import forms
from .models import Noticia, ClienteCategoria, ServerSelection, RecruitAFriend, DownloadClientPage, ContentCreator, RecruitReward, ClaimedReward, AccountActivation, SecurityToken, GuildRenameSettings, VoteSite, VoteLog, HomeApiPoints
from django.views.decorators.csrf import csrf_exempt
import logging
from datetime import datetime, timedelta
from .zone_definitions import get_zone_name
from .ac_soap import execute_soap_command
from django.utils import timezone
from .library_correo import enviar_correo
from django.utils.crypto import get_random_string
from django.conf import settings
import secrets

# Configuración del logger
logger = logging.getLogger(__name__)

def get_class_css(class_id):
    class_map = {
        1: 'warrior',
        2: 'paladin',
        3: 'hunter',
        4: 'rogue',
        5: 'priest',
        6: 'death-knight',
        7: 'shaman',
        8: 'mage',
        9: 'warlock',
        11: 'druid'
    }
    return class_map.get(class_id, 'unknown')

def get_class_text_css(class_id):
    text_class_map = {
        1: 'warrior',
        2: 'paladin',
        3: 'hunter',
        4: 'rogue',
        5: 'priest',
        6: 'death-knight',
        7: 'shaman',
        8: 'mage',
        9: 'warlock',
        11: 'druid'
    }
    return text_class_map.get(class_id, 'unknown')

def get_character_image(class_id, race, gender):
    """
    Devuelve la imagen del personaje basada en la raza, clase y género.
    `gender`: 0 = Hombre, 1 = Mujer
    """
    # Definir los nombres de archivos según el género
    gender_suffix = 'male' if gender == 0 else 'female'

    # Raza y clases compatibles
    race_class_map = {
        10: [2, 3, 4, 5, 6, 8, 9],  # Elfo de Sangre
        8: [1, 3, 4, 5, 6, 7, 8],   # Trol
        6: [1, 3, 6, 7, 11],        # Tauren
        5: [1, 4, 5, 6, 8, 9],      # No-Muerto
        2: [1, 3, 4, 6, 7, 9],      # Orco
        11: [1, 2, 3, 5, 6, 7, 8],  # Draenei
        7: [1, 4, 6, 8, 9],         # Gnomo
        4: [1, 3, 4, 5, 6, 11],     # Elfo de la Noche
        3: [1, 2, 3, 4, 5, 6],      # Enano
        1: [1, 2, 4, 5, 6, 8, 9]    # Humano
    }

    # Verificar si la clase es compatible con la raza
    if class_id not in race_class_map.get(race, []):
        return 'nw-themes/nw-ryu/nw-images/nw-classes/unknown.webp'  # Imagen por defecto si no es compatible

    # Construir el nombre del archivo basado en la raza y el género
    race_image_map = {
        10: f"big-blood-elf-{gender_suffix}.webp",
        8: f"big-troll-{gender_suffix}.webp",
        6: f"big-tauren-{gender_suffix}.webp",
        5: f"big-undead-{gender_suffix}.webp",
        2: f"big-orc-{gender_suffix}.webp",
        11: f"big-draenei-{gender_suffix}.webp",
        7: f"big-gnome-{gender_suffix}.webp",
        4: f"big-night-elf-{gender_suffix}.webp",
        3: f"big-dwarf-{gender_suffix}.webp",
        1: f"big-human-{gender_suffix}.webp"
    }

    # Devolver la imagen según la raza y género, o una imagen por defecto
    return f"nw-themes/nw-ryu/nw-images/nw-races/{race_image_map.get(race, 'unknown.webp')}"

    

dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

def formatear_fecha(fecha):
    """Formatea la fecha al estilo solicitado."""
    dia_semana = dias_semana[fecha.weekday()]
    mes = meses[fecha.month - 1]
    return f"{dia_semana} {fecha.day:02d} de {mes} del {fecha.year}"


# Clase de formulario de inicio de sesión
class LoginForm(forms.Form):
    username = forms.CharField(max_length=32, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

def sha1(data):
    """Función auxiliar para calcular SHA-1."""
    return hashlib.sha1(data).digest()

def calculate_srp6_verifier(username, password, salt):
    """Calcula el verifier usando SRP6 basado en la implementación PHP."""
    g = gmpy2.mpz(7)
    N = gmpy2.mpz('894B645E89E1535BBDAD5B8B290650530801B18EBFBF5E8FAB3C82872A3E9BB7', 16)

    # Paso 1: Calcular H(username:password)
    h1 = sha1((username.upper() + ':' + password.upper()).encode('utf-8'))

    # Usar el salt proporcionado (sin invertir)
    salt_bytes = bytes.fromhex(salt)

    # Paso 2: Calcular H(salt + H(username:password))
    h2 = sha1(salt_bytes + h1)

    # Convertir el hash a un entero (little-endian)
    h2_int = gmpy2.mpz.from_bytes(h2, 'little')

    # Calcular el verifier usando g^h2 mod N
    verifier = gmpy2.powmod(g, h2_int, N)
    verifier_bytes = verifier.to_bytes(32, 'little')

    # Convertir el resultado a hexadecimal en mayúsculas
    return binascii.hexlify(verifier_bytes).decode('utf-8').upper()

def authenticate(username, password):
    try:
        # Obtener el salt y el verifier de la base de datos
        with connections['acore_auth'].cursor() as cursor:
            cursor.execute("SELECT salt, verifier FROM account WHERE username = %s", [username])
            result = cursor.fetchone()

        if not result:
            return False

        salt, stored_verifier = result

        # Convertir `salt` y `verifier` a formato hexadecimal si son bytes
        if isinstance(salt, bytes):
            salt = salt.hex()
        if isinstance(stored_verifier, bytes):
            stored_verifier = stored_verifier.hex()

        # Calcular el verifier con el username y password proporcionados
        calculated_verifier = calculate_srp6_verifier(username, password, salt)

        # Comparar el verifier calculado con el almacenado en la base de datos
        return calculated_verifier.strip().upper() == stored_verifier.strip().upper()

    except Exception:
        return False

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Llamar a la función de autenticación
            if authenticate(username, password):
                # Guardar el nombre de usuario en mayúsculas en la sesión
                request.session['username'] = username.upper()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': "Usuario o contraseña incorrectos"})
        else:
            return JsonResponse({'success': False, 'error': "Formulario no válido"})
    
    form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})

# Función para contar los personajes en línea
def get_online_characters_count():
    with connections['acore_characters'].cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM characters WHERE online = 1")
        result = cursor.fetchone()
        return result[0] if result else 0

# Verificar si un servidor está en línea
def check_server_status(host, port):
    if not host or host == "N/A":
        return False
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect((host, port))
        s.close()
        return True
    except (socket.timeout, ConnectionRefusedError, socket.gaierror):
        return False

# Vista principal que muestra noticias y estado del servidor
def home_view(request):
    noticias = Noticia.objects.order_by('-fecha_publicacion')[:50]
    online_characters = get_online_characters_count()
    server_selection = ServerSelection.objects.first()
    status = check_server_status(server_selection.address, server_selection.port) if server_selection else None
    game_version = 'WotLK' if server_selection and server_selection.gamebuild == 12340 else 'Cataclysm'

    context = {
        'noticias': noticias,
        'server': server_selection,
        'status': 'Online' if status else 'Offline',
        'expansion': game_version,
        'online_characters': online_characters,
    }
    return render(request, 'home/home.html', context)

# Vista para descargar el cliente
def download_client_view(request):
    download_content = DownloadClientPage.objects.first()
    categorias = ClienteCategoria.objects.all()
    return render(request, 'download/download_client.html', {
        'download_content': download_content,
        'categorias': categorias,
    })

# Vista para descargar addons
def download_addons_view(request):
    return redirect("https://foro.novawow.com/files/")

# Vista para mostrar creadores de contenido
def content_creators_view(request):
    content_creator = ContentCreator.objects.first()
    return render(request, 'community/content_creators.html', {'content_creator': content_creator})

# Vista para mostrar el estado del servidor
def server_status_view(request):
    server_selection = ServerSelection.objects.first()
    if server_selection:
        status = check_server_status(server_selection.address, server_selection.port)
        game_version = 'WotLK' if server_selection.gamebuild == 12340 else 'Cataclysm'
    else:
        status = None
        game_version = None

    return render(request, 'server_status/server_status.html', {
        'server': server_selection,
        'status': 'Online' if status else 'Offline',
        'game_version': game_version,
    })


# Vista para cerrar sesión
def logout_view(request):
    if 'username' in request.session:
        del request.session['username']
    return redirect('index')

# Vistas adicionales
@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        password = request.POST.get('password').strip()
        conf_password = request.POST.get('conf-password').strip()
        email = request.POST.get('email').strip()
        conf_email = request.POST.get('conf-email').strip()
        recruiter = request.POST.get('recruiter').strip()

        # Validar entradas
        if not username or not password or not email:
            return JsonResponse({'success': False, 'message': 'Por favor, complete todos los campos.'})
        
        if len(username) > 17 or not username.isalnum():
            return JsonResponse({'success': False, 'message': 'Nombre de usuario no válido.'})

        if password != conf_password:
            return JsonResponse({'success': False, 'message': 'Las contraseñas no coinciden.'})

        if email != conf_email or not re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', email):
            return JsonResponse({'success': False, 'message': 'El correo electrónico no es válido.'})

        # Verificar si el usuario ya existe
        with connections['acore_auth'].cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM account WHERE username = %s", [username])
            if cursor.fetchone()[0] > 0:
                return JsonResponse({'success': False, 'message': 'El nombre de usuario ya está en uso.'})

        # Validar y obtener recruiter_id
        recruiter_id = 0  # Valor por defecto si no se proporciona un reclutador
        if recruiter:
            with connections['acore_auth'].cursor() as cursor:
                cursor.execute("SELECT id FROM account WHERE username = %s", [recruiter])
                recruiter_data = cursor.fetchone()
                if recruiter_data:
                    recruiter_id = recruiter_data[0]
                else:
                    with connections['acore_characters'].cursor() as char_cursor:
                        char_cursor.execute("SELECT account FROM characters WHERE name = %s", [recruiter])
                        character_data = char_cursor.fetchone()
                        if character_data:
                            recruiter_id = character_data[0]
                        else:
                            return JsonResponse({'success': False, 'message': 'El reclutador ingresado no existe.'})

        # Generar salt y verifier
        salt = binascii.hexlify(os.urandom(32)).decode('utf-8').upper()
        verifier = calculate_srp6_verifier(username, password, salt)

        # Convertir `salt` y `verifier` a bytes antes de guardarlos en la base de datos
        salt_bytes = binascii.unhexlify(salt)
        verifier_bytes = binascii.unhexlify(verifier)

        # Generar un hash único para activación
        activation_hash = get_random_string(32)

        # Guardar la información en la tabla `AccountActivation`
        AccountActivation.objects.create(
            username=username,
            email=email,
            password=password,
            salt=salt_bytes,
            verifier=verifier_bytes,
            recruiter_id=recruiter_id,
            hash=activation_hash
        )

        # Enviar correo de activación
        activation_link = f"{settings.URL_PRINCIPAL}/es/activate-account?act={activation_hash}"
        context = {
            'username': username,
            'password': password,
            'activation_link': activation_link,
            'NOMBRE_SERVIDOR': settings.NOMBRE_SERVIDOR
        }
        enviar_correo(
            subject=f'Activación de la cuenta {username} - {settings.NOMBRE_SERVIDOR}',
            to_email=email,
            template='emails/activation.html',
            context=context
        )

         # Preparar el mensaje de respuesta
        message = f"""
        <div class="alert-message" id="create-response" style="display: block;">
            <span class="ok-form-response">La cuenta '{username}' ha sido creada.</span><br><br>
            <span>Se ha enviado un enlace de activación al correo {email}.</span>
        </div>
        """
        return JsonResponse({'success': True, 'message': message})

    return render(request, 'auth/register.html')
 
    
def activate_account_view(request):
    activation_hash = request.GET.get('act')

    try:
        activation = AccountActivation.objects.get(hash=activation_hash)
        
        if activation.is_expired():
            return render(request, 'auth/activation_invalid.html')

        # Insertar la cuenta en `acore_auth`
        with connections['acore_auth'].cursor() as cursor:
            cursor.execute("""
                INSERT INTO account (username, salt, verifier, email, reg_mail, recruiter, joindate, last_ip)
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s)
            """, [
                activation.username, activation.salt, activation.verifier,
                activation.email, activation.email, activation.recruiter_id,
                request.META.get('REMOTE_ADDR')
            ])
        
        # Eliminar el registro de activación
        activation.delete()

        return render(request, 'auth/activation_success.html')

    except AccountActivation.DoesNotExist:
        return render(request, 'auth/activation_invalid.html')    

def recover_account_view(request):
    return render(request, 'auth/recover_account.html')

def novawow_realm_view(request):
    return render(request, 'realms/novawow_realm.html')

def contact_us_view(request):
    return render(request, 'contact/contact_us.html')

def legal_notice_view(request):
    return render(request, 'legal/legal_notice.html')
    
def not_found(request, exception=None):
    return render(request, '404.html', status=404)
        
def terms_and_conditions_view(request):
    return render(request, 'legal/terms_and_conditions.html')

def privacy_policy_view(request):
    return render(request, 'legal/privacy_policy.html')

def refund_policy_view(request):
    return render(request, 'legal/refund_policy.html')

def cookies_view(request):
    return render(request, 'legal/cookies.html')

def recruit_a_friend_view(request):
    username = request.session.get('username')
    account_status = None
    characters = []
    claimed_rewards_count = 0

    # Si el usuario está logueado, obtener su información
    if username:
        # Obtener información del usuario
        with connections['acore_auth'].cursor() as cursor:
            cursor.execute("SELECT id, last_ip FROM account WHERE username = %s", [username])
            account_data = cursor.fetchone()

        if account_data:
            account_id = account_data[0]
            user_ip = account_data[1]
            account_status = get_account_status(account_id)
            characters = get_account_characters(account_id)
            claimed_rewards_count = ClaimedReward.objects.filter(account_id=account_id).count()
        else:
            account_id = None
            user_ip = None
    else:
        account_id = None
        user_ip = None

    # Obtener todas las recompensas
    all_rewards = RecruitReward.objects.all()
    available_rewards = []
    
    # Si el usuario está logueado, filtrar recompensas disponibles
    if account_id:
        available_rewards = [reward for reward in all_rewards if not ClaimedReward.objects.filter(account_id=account_id, recruit_reward=reward).exists()]

    # Manejar solicitudes POST (solo si el usuario está logueado)
    if request.method == 'POST':
        if not username:
            return JsonResponse({'success': False, 'message': 'Debes estar logueado para reclamar una recompensa.'})
        
        reward_id = request.POST.get('reward_id')
        character_name = request.POST.get('character')

        if not reward_id or not character_name:
            return JsonResponse({'success': False, 'message': 'Selecciona una recompensa y un personaje.'})

        try:
            reward = RecruitReward.objects.get(id=reward_id)

            # Verificar si ya se ha reclamado la recompensa
            if ClaimedReward.objects.filter(account_id=account_id, recruit_reward=reward).exists():
                return JsonResponse({'success': False, 'message': 'Ya has reclamado esta recompensa.'})

            # Verificar si cumple los requisitos
            if account_status['recruited_level_80_count'] < reward.required_friends:
                return JsonResponse({'success': False, 'message': 'No cumples con los requisitos.'})

            # Obtener amigos reclutados que han alcanzado el nivel 80
            recruited_friends = get_recruited_friends_at_level_80(account_id, reward.required_friends)
            
            # Comprobar si alguno de los reclutados es válido
            if len(recruited_friends) < reward.required_friends:
                return JsonResponse({'success': False, 'message': 'No cumples con los requisitos o los amigos tienen la misma IP.'})

            # Comprobar si alguno de los reclutados tiene la misma IP que el usuario
            if check_recruited_ip_conflict(recruited_friends, user_ip):
                return JsonResponse({'success': False, 'message': 'No puedes reclamar recompensas de amigos que tienen la misma IP.'})

            # Ejecutar el comando SOAP
            command = f".send items {character_name} 'Recompensa de Recluta Amigo' 'Tu amigo alcanzó el Nivel 80' {reward.item_id}:{reward.item_quantity}"
            response = execute_soap_command(command)

            if response and "Mail sent to" in response:
                # Registrar la recompensa como reclamada
                ClaimedReward.objects.create(
                    account_id=account_id,
                    username=username,
                    recruit_reward=reward,
                    character_name=character_name,
                    claimed_at=timezone.now(),
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                claimed_rewards_count = ClaimedReward.objects.filter(account_id=account_id).count()
                
                return JsonResponse({
                    'success': True,
                    'message': f"Recompensa '{reward.reward_name}' entregada a {character_name}.",
                    'claimed_count': claimed_rewards_count
                })
            else:
                return JsonResponse({'success': False, 'message': 'Error al entregar la recompensa.'})

        except RecruitReward.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Recompensa no encontrada.'})

    # Renderizar la página para usuarios no logueados y logueados
    return render(request, 'recruit/recruit_a_friend.html', {
        'account_status': account_status,
        'all_rewards': all_rewards,
        'available_rewards': available_rewards,
        'characters': characters,
        'claimed_rewards_count': claimed_rewards_count,
        'is_logged_in': username is not None
    })


def check_recruited_ip_conflict(recruited_accounts, user_ip):
    """
    Verifica si alguna de las cuentas reclutadas tiene la misma IP que la cuenta del reclutador.
    """
    if not recruited_accounts:
        return False

    with connections['acore_auth'].cursor() as cursor:
        cursor.execute("""
            SELECT last_ip FROM account WHERE id IN %s
        """, [tuple(recruited_accounts)])
        recruited_ips = [ip[0] for ip in cursor.fetchall()]

    return user_ip in recruited_ips
    
def get_recruited_friends_at_level_80(account_id, required_count):
    """
    Obtiene una lista de IDs de amigos reclutados que han alcanzado el nivel 80 y 
    no tienen la misma IP que el reclutador.
    """
    # Primero obtener los IDs de cuentas reclutadas desde `acore_auth`
    with connections['acore_auth'].cursor() as auth_cursor:
        auth_cursor.execute("""
            SELECT id, last_ip FROM account WHERE recruiter = %s
        """, [account_id])
        recruited_accounts = auth_cursor.fetchall()
    
    if not recruited_accounts:
        return []

    # Extraer IDs y IPs de las cuentas reclutadas
    recruited_ids = [acc[0] for acc in recruited_accounts]
    recruited_ips = {acc[0]: acc[1] for acc in recruited_accounts}

    # Obtener la IP del usuario actual
    with connections['acore_auth'].cursor() as cursor:
        cursor.execute("SELECT last_ip FROM account WHERE id = %s", [account_id])
        user_ip = cursor.fetchone()[0]

    # Luego, verificar cuáles de esas cuentas tienen personajes al nivel 80 en `acore_characters`
    with connections['acore_characters'].cursor() as char_cursor:
        char_cursor.execute("""
            SELECT DISTINCT account FROM characters
            WHERE level = 80 AND account IN %s
            LIMIT %s
        """, [tuple(recruited_ids), required_count])
        recruited_at_level_80 = [acc[0] for acc in char_cursor.fetchall()]

    # Filtrar cuentas que no tienen la misma IP que el usuario actual
    valid_recruits = [acc for acc in recruited_at_level_80 if recruited_ips[acc] != user_ip]

    return valid_recruits
    
    
def my_account(request):
    # Verificar si la sesión contiene el usuario
    username = request.session.get('username')
    
    # Si la sesión no tiene el usuario, redirigir al inicio de sesión
    if not username:
        return redirect('log-in')

    is_logged_in = True  # Si el usuario está en la sesión, asumimos que está conectado

    # Obtener información básica de la cuenta
    with connections['acore_auth'].cursor() as cursor:
        cursor.execute("""
            SELECT id, username, reg_mail, email, last_ip, last_attempt_ip, joindate 
            FROM account 
            WHERE username = %s
        """, [username])
        account_data = cursor.fetchone()

    if not account_data:
        return redirect('index')

    account_id = account_data[0]
    
    # Obtener los personajes asociados a la cuenta
    characters = get_account_characters(account_id)
    has_characters = bool(characters)

    # Obtener el estado de la cuenta
    account_status = get_account_status(account_id)
    
    # Obtener los puntos (DP y VP) del usuario desde la tabla `home_api_points`
    user_points = HomeApiPoints.objects.filter(accountID=account_id).first()
    dp = user_points.dp if user_points else 0
    vp = user_points.vp if user_points else 0
    
    
    # Obtener el estado del token de seguridad
    security_token = SecurityToken.objects.filter(user_id=account_id).first()
    if security_token:
        token_status = "Solicitado"
        token_date = security_token.created_at.strftime('%H:%M:%S %d-%m-%Y')
    else:
        token_status = "Sin solicitar"
        token_date = None

    return render(request, 'my-account/my-account.html', {
        'is_logged_in': is_logged_in,
        'user_info': {
            'username': account_data[1],
            'reg_mail': account_data[2],
            'email': account_data[3],
            'last_ip': account_data[4],
            'last_attempt_ip': account_data[5],
            'joindate': formatear_fecha(account_data[6]),
            
        },
        'account_status': account_status,
        'characters': characters,
        'has_characters': has_characters,
        'dp': dp,
        'vp': vp,
        'token_status': token_status,
        'token_date': token_date
    })



def get_account_status(account_id):
    with connections['acore_auth'].cursor() as cursor:
        # Obtener información de la tabla 'account'
        cursor.execute("""
            SELECT username, reg_mail, email, last_ip, last_attempt_ip, joindate, recruiter 
            FROM account 
            WHERE id = %s
        """, [account_id])
        account_data = cursor.fetchone()

        if not account_data:
            return None

        # Verificar si la cuenta está baneada
        cursor.execute("""
            SELECT unbandate, UNIX_TIMESTAMP() 
            FROM account_banned 
            WHERE id = %s AND active = 1
        """, [account_id])
        ban_data = cursor.fetchone()

        # Obtener el número de amigos reclutados
        cursor.execute("""
            SELECT id 
            FROM account 
            WHERE recruiter = %s
        """, [account_id])
        recruited_accounts = cursor.fetchall()
        recruited_count = len(recruited_accounts)

        # Contar cuántos personajes de amigos reclutados han alcanzado el nivel 80
        if recruited_count > 0:
            recruited_ids = [acc[0] for acc in recruited_accounts]
            with connections['acore_characters'].cursor() as char_cursor:
                char_cursor.execute("""
                    SELECT COUNT(*) 
                    FROM characters 
                    WHERE account IN %s AND level = 80
                """, [tuple(recruited_ids)])
                level_80_count = char_cursor.fetchone()[0]
        else:
            level_80_count = 0

    # Asignar los datos a variables
    user_info = {
        'username': account_data[0] if account_data[0] else 'No disponible',
        'reg_mail': account_data[1] if account_data[1] else 'No disponible',
        'email': account_data[2] if account_data[2] else 'No disponible',
        'last_ip': account_data[3] if account_data[3] else 'Nunca',
        'last_attempt_ip': account_data[4] if account_data[4] else 'Nunca',
        'joindate': account_data[5].strftime("%A %d de %B del %Y a las %H:%M:%S Horas") if account_data[5] else 'No disponible',
        'is_recruited': bool(account_data[6]),
        'recruited_count': recruited_count,
        'recruited_level_80_count': level_80_count
    }

    # Información sobre la suspensión, si existe
    if ban_data:
        unban_timestamp, current_timestamp = ban_data
        remaining_time = unban_timestamp - current_timestamp
        user_info['is_banned'] = True
        user_info['unban_date'] = datetime.datetime.fromtimestamp(unban_timestamp).strftime("%A %d de %B del %Y a las %H:%M:%S Horas")
        user_info['remaining_time'] = remaining_time
    else:
        user_info['is_banned'] = False

    return user_info

    
def get_character_image(class_id, race, gender):
    """
    Devuelve la imagen del personaje basada en la raza, clase y género.
    `gender`: 0 = Hombre, 1 = Mujer
    """
    # Definir los nombres de archivos según el género
    gender_suffix = 'male' if gender == 0 else 'female'

    # Raza y clases compatibles
    race_class_map = {
        10: [2, 3, 4, 5, 6, 8, 9],  # Elfo de Sangre
        8: [1, 3, 4, 5, 6, 7, 8],   # Trol
        6: [1, 3, 6, 7, 11],        # Tauren
        5: [1, 4, 5, 6, 8, 9],      # No-Muerto
        2: [1, 3, 4, 6, 7, 9],      # Orco
        11: [1, 2, 3, 5, 6, 7, 8],  # Draenei
        7: [1, 4, 6, 8, 9],         # Gnomo
        4: [1, 3, 4, 5, 6, 11],     # Elfo de la Noche
        3: [1, 2, 3, 4, 5, 6],      # Enano
        1: [1, 2, 4, 5, 6, 8, 9]    # Humano
    }

    # Verificar si la clase es compatible con la raza
    if class_id not in race_class_map.get(race, []):
        return 'nw-themes/nw-ryu/nw-images/nw-classes/unknown.webp'  # Imagen por defecto si no es compatible

    # Construir el nombre del archivo basado en la raza y el género
    race_image_map = {
        10: f"big-blood-elf-{gender_suffix}.webp",
        8: f"big-troll-{gender_suffix}.webp",
        6: f"big-tauren-{gender_suffix}.webp",
        5: f"big-undead-{gender_suffix}.webp",
        2: f"big-orc-{gender_suffix}.webp",
        11: f"big-draenei-{gender_suffix}.webp",
        7: f"big-gnome-{gender_suffix}.webp",
        4: f"big-night-elf-{gender_suffix}.webp",
        3: f"big-dwarf-{gender_suffix}.webp",
        1: f"big-human-{gender_suffix}.webp"
    }

    # Devolver la imagen según la raza y género, o una imagen por defecto
    return f"nw-themes/nw-ryu/nw-images/nw-races/{race_image_map.get(race, 'unknown.webp')}"

def get_account_characters(account_id):
    """Obtiene los personajes de la cuenta dada."""
    with connections['acore_characters'].cursor() as cursor:
        cursor.execute("""
            SELECT name, level, money, race, class, zone, gender
            FROM characters
            WHERE account = %s
        """, [account_id])
        characters = cursor.fetchall()

    character_list = []
    for char in characters:
        name, level, money, race, class_id, zone, gender = char
        gold = money // 10000
        silver = (money % 10000) // 100
        copper = money % 100

        # Obtener la clase CSS y la imagen antes de pasarla a la plantilla
        class_css = get_class_css(class_id)
        image_url = get_character_image(class_id, race, gender)

        # Obtener el nombre de la zona usando la función get_zone_name
        zone_name = get_zone_name(zone)

        character_list.append({
            'name': name,
            'level': level,
            'gold': gold,
            'silver': silver,
            'copper': copper,
            'race': race,
            'class_id': class_id,
            'zone': zone_name,
            'class_css': class_css,
            'image_url': image_url
        })
    return character_list
    
    
def change_password_view(request):
    # Verificar si el usuario está autenticado mediante la sesión
    username = request.session.get('username')
    if not username:
        return redirect('login')

    # Obtener el usuario desde la base de datos de `acore_auth`
    user_data = get_user_from_acore(username)
    if not user_data:
        return redirect('login')

    user_id = user_data['id']
    email = user_data['email']

    if request.method == 'POST':
        current_password = request.POST.get('cur-password').strip()
        new_password = request.POST.get('new-password').strip()
        conf_new_password = request.POST.get('conf-new-password').strip()
        security_token = request.POST.get('security-token').strip()

        # Validar campos vacíos
        if not current_password or not new_password or not conf_new_password or not security_token:
            return JsonResponse({'success': False, 'message': '<span class="red-form-response">Por favor, complete todos los campos.</span>'})

        # Validar que la nueva contraseña coincida con su confirmación
        if new_password != conf_new_password:
            return JsonResponse({'success': False, 'message': '<span class="red-form-response">Las contraseñas no coinciden.</span>'})

        # Validar longitud de la nueva contraseña
        if len(new_password) > 16:
            return JsonResponse({'success': False, 'message': '<span class="red-form-response">La contraseña nueva no debe exceder los 16 caracteres.</span>'})

        # Verificar si el token de seguridad ha sido generado
        existing_token = SecurityToken.objects.filter(user_id=user_id).first()
        if not existing_token:
            return JsonResponse({'success': False, 'message': '<span class="red-form-response">No tienes un token de seguridad generado. Por favor, genera uno antes de cambiar tu contraseña.</span>'})

        # Verificar si el token proporcionado es correcto
        if existing_token.token != security_token:
            return JsonResponse({'success': False, 'message': '<span class="red-form-response">El token ingresado es incorrecto.</span>'})

        # Verificar la contraseña actual usando la función `authenticate`
        if not authenticate(username, current_password):
            return JsonResponse({'success': False, 'message': '<span class="red-form-response">La contraseña actual es incorrecta.</span>'})

        # Generar salt y verifier para la nueva contraseña
        new_salt = binascii.hexlify(os.urandom(32)).decode('utf-8').upper()
        new_verifier = calculate_srp6_verifier(username, new_password, new_salt)

        # Convertir `salt` y `verifier` a bytes antes de guardarlos en la base de datos
        new_salt_bytes = binascii.unhexlify(new_salt)
        new_verifier_bytes = binascii.unhexlify(new_verifier)

        # Actualizar la contraseña en la base de datos
        with connections['acore_auth'].cursor() as cursor:
            cursor.execute("""
                UPDATE account SET salt = %s, verifier = %s WHERE username = %s
            """, [new_salt_bytes, new_verifier_bytes, username])

        # Cerrar la sesión por seguridad
        if 'username' in request.session:
            del request.session['username']

        # Redirigir al usuario a la página de inicio de sesión
        return JsonResponse({
            'success': True,
            'message': '<span class="ok-form-response">Contraseña cambiada exitosamente. Has sido desconectado por seguridad.</span>',
            'redirect': True
        })

    return render(request, 'account/change_password.html')


def get_user_from_acore(username):
    """
    Obtiene la información del usuario desde la base de datos `acore_auth`.
    """
    with connections['acore_auth'].cursor() as cursor:
        cursor.execute("SELECT id, email FROM account WHERE username = %s", [username])
        result = cursor.fetchone()
        if result:
            return {'id': result[0], 'email': result[1]}
    return None

def security_token_view(request):
    # Verificar si el usuario está autenticado mediante la sesión
    username = request.session.get('username')
    if not username:
        return redirect('index')

    # Obtener el usuario desde la base de datos de `acore_auth`
    user_data = get_user_from_acore(username)
    if not user_data:
        return redirect('index')

    user_id = user_data['id']
    email = user_data['email']
    ip_address = request.META.get('REMOTE_ADDR')

    # Verificar si existe un token activo para mostrar la fecha en la plantilla
    existing_token = SecurityToken.objects.filter(user_id=user_id).first()
    
    # Obtener la fecha del token o "Sin solicitar" si no hay token
    token_date = "Sin solicitar"
    if existing_token:
        token_date = existing_token.created_at.strftime('%H:%M:%S %d-%m-%Y')

    if request.method == 'POST':
        # Verificar si ya existe un token y si se puede generar uno nuevo después de 7 días
        if existing_token:
            # Comprobar si han pasado al menos 7 días desde la creación del token
            days_since_creation = (timezone.now() - existing_token.created_at).days
            if days_since_creation < 7:
                remaining_days = 7 - days_since_creation
                return JsonResponse({
                    'success': False,
                    'message': f'<span class="red-form-response">Sólo puedes solicitar un nuevo Token de seguridad cada 7 días, faltan {remaining_days} días para generar un nuevo Token.</span>'
                })

        # Generar un nuevo token
        token = secrets.token_urlsafe(4)[:6]
        expires_at = timezone.now() + timedelta(days=7)

        # Eliminar el token anterior y crear uno nuevo
        if existing_token:
            existing_token.delete()

        # Crear y guardar el nuevo token
        new_token = SecurityToken.objects.create(
            user_id=user_id,
            token=token,
            ip_address=ip_address,
            expires_at=expires_at  # Esta fecha solo se usa para el control de los 7 días
        )

        # Enviar el correo con el token al usuario
        send_security_token_email(email, username, token, ip_address)

        # Obtener la nueva fecha del token
        new_token_date = new_token.created_at.strftime('%H:%M:%S %d-%m-%Y')

        # Responder con un mensaje exitoso y la nueva fecha
        return JsonResponse({
            'success': True,
            'message': f'<span class="ok-form-response">Se ha enviado el Token de seguridad al correo {email}.</span>',
            'token_date': new_token_date
        })

    # Pasar `token_date` al contexto de la plantilla
    return render(request, 'account/security_token.html', {
        'token_date': token_date
    })

def send_security_token_email(email, username, token, ip_address):
    """
    Envía un correo electrónico con el token de seguridad.
    """
    context = {
        'username': username,
        'token': token,
        'ip_address': ip_address,
        'NOMBRE_SERVIDOR': settings.NOMBRE_SERVIDOR
    }

    # Llamada a tu función personalizada `enviar_correo`
    enviar_correo(
         subject=f'Token de seguridad de la cuenta {username} - {settings.NOMBRE_SERVIDOR}',
        to_email=email,
        template='emails/security_token.html',  # Asegúrate de que este template exista
        context=context
    )

def change_email_view(request):
    username = request.session.get('username')
    if not username:
        return redirect('login')

    # Obtener el usuario desde la base de datos de `acore_auth`
    with connections['acore_auth'].cursor() as cursor:
        cursor.execute("""
            SELECT id, email, reg_mail
            FROM account 
            WHERE username = %s
        """, [username])
        account_data = cursor.fetchone()

    if not account_data:
        return redirect('login')

    user_id, current_email, reg_email = account_data
    security_token = SecurityToken.objects.filter(user_id=user_id).first()

    if request.method == 'POST':
        print("Datos recibidos:", request.POST)

        current_password = request.POST.get('cur-password', '').strip()
        current_email_input = request.POST.get('cur-email', '').strip()
        new_email = request.POST.get('new-email', '').strip()
        conf_new_email = request.POST.get('conf-new-email', '').strip()
        token = request.POST.get('security-token', '').strip()

        # Validar los campos
        if not all([current_password, current_email_input, new_email, conf_new_email, token]):
            return JsonResponse({'success': False, 'message': 'Por favor, complete todos los campos.'})

        if current_email_input != current_email:
            return JsonResponse({'success': False, 'message': 'El correo actual no es correcto.'})

        if new_email != conf_new_email:
            return JsonResponse({'success': False, 'message': 'Los correos no coinciden.'})

        if not re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', new_email):
            return JsonResponse({'success': False, 'message': 'El nuevo correo no es válido.'})

        if not security_token or security_token.token != token:
            return JsonResponse({'success': False, 'message': 'Token de seguridad incorrecto.'})

        if not authenticate(username, current_password):
            return JsonResponse({'success': False, 'message': 'Contraseña incorrecta.'})

        # Generar hashes
        old_email_hash = secrets.token_urlsafe(16)
        new_email_hash = secrets.token_urlsafe(16)

        # Guardar en `AccountActivation`
        AccountActivation.objects.create(
            username=username,
            email=new_email,
            old_email=current_email,
            password='',
            salt=b'',
            verifier=b'',
            recruiter_id=user_id,
            hash=new_email_hash,
            old_email_hash=old_email_hash
        )

        # Enviar confirmación al correo actual
        confirm_old_email_link = f"{settings.URL_PRINCIPAL}/es/confirm-old-email?hash={old_email_hash}"
        context_old_email = {
            'username': username,
            'confirm_link': confirm_old_email_link,
            'NOMBRE_SERVIDOR': settings.NOMBRE_SERVIDOR
        }
        enviar_correo(
            subject=f'Confirme el cambio de correo para {username}',
            to_email=current_email,
            template='emails/confirm_old_email.html',
            context=context_old_email
        )

        return JsonResponse({'success': True, 'message': 'Se ha enviado un correo de confirmación al correo actual.'})

    return render(request, 'account/change_email.html')


def confirm_old_email_view(request):
    hash = request.GET.get('hash')
    activation = AccountActivation.objects.filter(old_email_hash=hash, is_used=False).first()

    if not activation or activation.is_expired():
        return HttpResponse('Enlace no válido o expirado.', status=400)

    # Marcar solo el old_email_hash como usado
    activation.is_used = True
    activation.save()

    # Enviar correo al nuevo correo para confirmar el cambio
    activation_link = f"{settings.URL_PRINCIPAL}/es/confirm-new-email?hash={activation.hash}"
    context_new_email = {
        'username': activation.username,
        'activation_link': activation_link,
        'NOMBRE_SERVIDOR': settings.NOMBRE_SERVIDOR
    }
    enviar_correo(
        subject=f'Confirme su nuevo correo para {activation.username}',
        to_email=activation.email,
        template='emails/confirm_new_email.html',
        context=context_new_email
    )

    return HttpResponse('Correo confirmado. Se ha enviado un enlace al nuevo correo.')


def confirm_new_email_view(request):
    hash = request.GET.get('hash')
    activation = AccountActivation.objects.filter(hash=hash, is_new_email_used=False).first()

    if not activation or activation.is_expired():
        return HttpResponse('Enlace no válido o expirado.', status=400)

    # Marcar solo el new_email_hash como usado
    activation.is_new_email_used = True
    activation.save()

    # Actualizar el correo en la base de datos
    with connections['acore_auth'].cursor() as cursor:
        cursor.execute("""
            UPDATE account 
            SET email = %s, reg_mail = %s 
            WHERE username = %s
        """, [activation.email, activation.email, activation.username])

    # Enviar notificación al correo anterior
    context_old_email = {
        'username': activation.username,
        'new_email': activation.email,
        'NOMBRE_SERVIDOR': settings.NOMBRE_SERVIDOR
    }
    enviar_correo(
        subject=f'Su correo ha sido cambiado en {settings.NOMBRE_SERVIDOR}',
        to_email=activation.old_email,
        template='emails/old_email_notification.html',
        context=context_old_email
    )

    return HttpResponse('El cambio de correo ha sido confirmado y completado con éxito.')

   
def promo_code_view(request):
    return render(request, 'account/promo_code.html')

def transfer_d_points_view(request):
    # Renderizar la plantilla para la transferencia de puntos
    return render(request, 'account/transfer_d_points.html')    

def rename_guild_view(request):
    # Verificar si el usuario está autenticado mediante la sesión
    username = request.session.get('username')
    if not username:
        return redirect('login')

    # Obtener el usuario desde la base de datos `acore_auth`
    user_data = get_user_from_acore(username)
    if not user_data:
        return redirect('login')

    user_id = user_data['id']

    # Obtener el costo desde la configuración
    try:
        settings = GuildRenameSettings.objects.first()
        rename_cost = settings.cost if settings else 1000
    except GuildRenameSettings.DoesNotExist:
        rename_cost = 1000  # Valor predeterminado si no se encuentra la configuración

    # Comprobar si hay personajes que sean líderes de una hermandad
    with connections['acore_characters'].cursor() as cursor:
        cursor.execute("""
            SELECT g.guildid, g.name, gm.rank, c.name
            FROM guild g
            JOIN guild_member gm ON g.guildid = gm.guildid
            JOIN characters c ON c.guid = gm.guid
            WHERE c.account = %s AND gm.rank = 0
        """, [user_id])
        guild_leader_data = cursor.fetchall()

    if not guild_leader_data:
        no_guild_leader_message = "No tienes personajes que sean Maestros de Hermandad en tu cuenta."
    else:
        no_guild_leader_message = None

    if request.method == 'POST':
        old_guild_name = request.POST.get('old-guild-name').strip()
        new_guild_name = request.POST.get('new-guild-name').strip()
        conf_new_guild_name = request.POST.get('conf-new-guild-name').strip()
        current_password = request.POST.get('cur-password').strip()
        security_token = request.POST.get('security-token').strip()

        # Validar campos vacíos
        if not old_guild_name or not new_guild_name or not conf_new_guild_name or not current_password or not security_token:
            return JsonResponse({'success': False, 'message': '<span class="red-form-response">Por favor, complete todos los campos.</span>'})

        # Verificar si el usuario tiene suficientes Donation Points (DP)
        with connections['default'].cursor() as cursor:
            cursor.execute("SELECT dp FROM home_api_points WHERE accountID = %s", [user_id])
            points_data = cursor.fetchone()

        if not points_data or points_data[0] < rename_cost:
            return JsonResponse({'success': False, 'message': f'<span class="red-form-response">No tienes suficientes Donation Points (se requieren {rename_cost} DP).</span>'})

        # Deducir los Donation Points del usuario
        with connections['default'].cursor() as cursor:
            cursor.execute("UPDATE home_api_points SET dp = dp - %s WHERE accountID = %s", [rename_cost, user_id])

        return JsonResponse({'success': True, 'message': '<span class="ok-form-response">Hermandad renombrada exitosamente.</span>'})

    return render(request, 'account/rename_guild.html', {
        'guild_leader_data': guild_leader_data,
        'no_guild_leader_message': no_guild_leader_message,
        'rename_cost': rename_cost
    })

def vote_points_view(request):
    # Verificar si el usuario tiene un `username` en la sesión
    username = request.session.get('username')
    if not username:
        return redirect('login')

    # Obtener el `account_id` basado en el `username`
    with connections['acore_auth'].cursor() as cursor:
        cursor.execute("SELECT id FROM account WHERE username = %s", [username])
        account_data = cursor.fetchone()
    
    if not account_data:
        return JsonResponse({'success': False, 'message': 'Cuenta no encontrada.'})

    account_id = account_data[0]

    if request.method == 'POST':
        vote_url = request.POST.get('vote').strip()

        site = VoteSite.objects.filter(url=vote_url).first()
        if not site:
            return JsonResponse({'success': False, 'message': 'Sitio de votación no encontrado.'})

        # Verificar si ya ha votado en las últimas 12 horas y 30 minutos
        last_vote = VoteLog.objects.filter(account_id=account_id, vote_site=site).order_by('-created_at').first()
        now = timezone.now()
        if last_vote:
            time_diff = now - last_vote.created_at
            cooldown_period = timedelta(hours=12, minutes=30)
            
            if time_diff < cooldown_period:
                remaining_time = cooldown_period - time_diff
                hours, remainder = divmod(remaining_time.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                return JsonResponse({
                    'success': False,
                    'message': f'<span class="red-form-response">Tienes que esperar {hours} horas y {minutes} minutos antes de volver a votar.</span>'
                })

        # Acreditar puntos al usuario y registrar el voto
        user_points = HomeApiPoints.objects.filter(accountID=account_id).first()
        if user_points:
            user_points.vp += site.points
            user_points.save()
        else:
            HomeApiPoints.objects.create(accountID=account_id, vp=site.points, dp=0)

        # Registrar el voto
        VoteLog.objects.create(account_id=account_id, vote_site=site, last_vote_time=now)

        return JsonResponse({'success': True, 'message': f'Has votado en {site.name}. Se han acreditado {site.points} PV.'})

    vote_sites = VoteSite.objects.all()
    return render(request, 'account/vote_points.html', {'vote_sites': vote_sites})

def d_points_view(request):
    """
    Vista para la página de D-Points.
    Simplemente renderiza la plantilla d_points.html.
    """
    return render(request, 'account/d_points.html')


def points_history_view(request):    
    return render(request, 'account/points_history.html')
    
    
def trans_history_view(request):
    return render(request, 'account/trans_history.html')
    
def ban_history_view(request):
    return render(request, 'account/ban_history.html')

def security_history_view(request):
    """
    Vista para mostrar el historial de seguridad del usuario.
    """
    return render(request, 'account/security_history.html')


def trade_points_view(request):
    """
    Vista para la página de intercambio de puntos.
    """
    return render(request, 'account/trade_points.html')    
    

def help_view(request):
    # Verificar si el usuario está logueado
    if 'username' not in request.session:
        # Si no está logueado, redirigir al inicio de sesión
        return redirect('index')
    
    # Si está logueado, renderizar la página de ayuda
    return render(request, 'community/help.html')

def get_race_icon(race):
    race_icons = {
        1: "human-male",
        2: "orc-male",
        3: "dwarf-male",
        4: "night-elf-male",
        5: "undead-male",
        6: "tauren-male",
        7: "gnome-male",
        8: "troll-male",
        9: "goblin-male",
        10: "blood-elf-male",
        11: "draenei-male"
    }
    return race_icons.get(race, "unknown")
    
    
def get_race_iconss(race):
    race_iconss = {
        1: "human",
        2: "orc",
        3: "dwarf",
        4: "night-elf",
        5: "undead",
        6: "tauren",
        7: "gnome",
        8: "troll",
        9: "goblin",
        10: "blood-elf",
        11: "draenei"
    }
    return race_iconss.get(race, "unknown")

def get_class_icon(char_class):
    class_icons = {
        1: "warrior",
        2: "paladin",
        3: "hunter",
        4: "rogue",
        5: "priest",
        6: "death-knight",
        7: "shaman",
        8: "mage",
        9: "warlock",
        11: "druid"
    }
    return class_icons.get(char_class, "unknown")
    
    
def get_class_name(char_class):
    names = {
        1: "Guerrero",
        2: "Paladín",
        3: "Cazador",
        4: "Pícaro",
        5: "Sacerdote",
        6: "Caballero de la Muerte",
        7: "Chamán",
        8: "Mago",
        9: "Brujo",
        11: "Druida"
    }
    return names.get(char_class, "Desconocido")

def get_achievement_name(achievement_id):
    achievement_names = {
        457: "¡Primero del reino! Nivel 80",
        458: "¡Primero del reino! Pícaro nivel 80",
        463: "¡Primero del reino! Brujo nivel 80",
        461: "¡Primero del reino! Caballero de la Muerte nivel 80",
        462: "¡Primero del reino! Cazador nivel 80",
        467: "¡Primero del reino! Chamán nivel 80",
        466: "¡Primero del reino! Druida nivel 80",
        459: "¡Primero del reino! Guerrero nivel 80",
        460: "¡Primero del reino! Mago nivel 80",
        465: "¡Primero del reino! Paladín nivel 80",
        464: "¡Primero del reino! Sacerdote nivel 80",
        1408: "¡Primero del reino! Humano nivel 80",
        1407: "¡Primero del reino! Enano nivel 80",
        1409: "¡Primero del reino! Elfo de la noche nivel 80",
        1404: "¡Primero del reino! Gnomo nivel 80",
        1406: "¡Primero del reino! Draenei nivel 80",
        1410: "¡Primero del reino! Orco nivel 80",
        1413: "¡Primero del reino! Renegado nivel 80",
        1411: "¡Primero del reino! Tauren nivel 80",
        1412: "¡Primero del reino! Trol nivel 80",
        1405: "¡Primero del reino! Elfo de sangre nivel 80"
    }
    return achievement_names.get(achievement_id, "Logro Desconocido")


def novawow_players_view(request):
    # Verificar si el usuario está logueado
    if 'username' not in request.session:
        return redirect('index')

    # Obtener las 5 hermandades con más miembros
    with connections['acore_characters'].cursor() as cursor:
        guild_query = """
        SELECT g.name, c.name AS leader, 
               CASE WHEN c.race IN (1, 3, 4, 7, 11) THEN 'alliance' ELSE 'horde' END AS faction,
               COUNT(gm.guid) AS members, 
               g.createdate
        FROM guild g
        JOIN characters c ON c.guid = g.leaderguid
        LEFT JOIN guild_member gm ON gm.guildid = g.guildid
        GROUP BY g.guildid
        ORDER BY members DESC
        LIMIT 5
        """
        cursor.execute(guild_query)
        guilds = cursor.fetchall()

    formatted_guilds = [
        (name, leader, faction, members, datetime.fromtimestamp(createdate).strftime('%d-%m-%Y'))
        for name, leader, faction, members, createdate in guilds
    ]

    # Obtener el top 10 de jugadores con más muertes con honor
    with connections['acore_characters'].cursor() as cursor:
        kills_query = """
        SELECT name, race, class, totalKills, todayKills
        FROM characters
        ORDER BY totalKills DESC
        LIMIT 10
        """
        cursor.execute(kills_query)
        top_kills = cursor.fetchall()

    players_with_kills = [
        {
            'name': name,
            'race_icon': f"big-{get_race_icon(race)}",
            'class_icon': f"{get_class_icon(char_class)}-medium",
            'total_kills': total_kills,
            'today_kills': today_kills
        }
        for name, race, char_class, total_kills, today_kills in top_kills
    ]

    # Obtener personajes por clase y facción
    with connections['acore_characters'].cursor() as cursor:
        class_faction_query = """
        SELECT class,
               SUM(CASE WHEN race IN (1, 3, 4, 7, 11) THEN 1 ELSE 0 END) AS alliance_count,
               SUM(CASE WHEN race IN (2, 5, 6, 8, 10) THEN 1 ELSE 0 END) AS horde_count,
               COUNT(*) AS total_count
        FROM characters
        GROUP BY class
        """
        cursor.execute(class_faction_query)
        class_faction_data = cursor.fetchall()

    classes_data = [
        {
            'class_icon': f"{get_class_icon(char_class)}-chest",
            'class_name': get_class_name(char_class),
            'total': total_count,
            'alliance': alliance_count,
            'horde': horde_count
        }
        for char_class, alliance_count, horde_count, total_count in class_faction_data
    ]

    # Obtener el top 10 de jugadores con más logros
    with connections['acore_characters'].cursor() as cursor:
        achievements_query = """
        SELECT c.name, c.race, c.class, MAX(cap.counter) AS achievement_points
        FROM character_achievement_progress cap
        JOIN characters c ON cap.guid = c.guid
        GROUP BY c.guid
        ORDER BY achievement_points DESC
        LIMIT 10
        """
        cursor.execute(achievements_query)
        top_achievements = cursor.fetchall()

    players_with_achievements = [
        {
            'name': name,
            'race_icon': f"big-{get_race_icon(race)}",
            'class_icon': f"{get_class_icon(char_class)}-medium",
            'achievement_points': achievement_points
        }
        for name, race, char_class, achievement_points in top_achievements
    ]

    # Obtener logros "Primeros del Reino"
    with connections['acore_characters'].cursor() as cursor:
        first_realm_query = """
        SELECT ca.achievement, c.name, c.race, c.class, c.gender, ca.date
        FROM character_achievement ca
        JOIN characters c ON ca.guid = c.guid
        WHERE ca.achievement IN (
            457, 458, 463, 461, 462, 467, 466, 459, 460, 465, 464, 
            1408, 1407, 1409, 1404, 1406, 1410, 1413, 1411, 1412, 1405
        )
        ORDER BY ca.date ASC
        """
        cursor.execute(first_realm_query)
        first_realm_achievements = cursor.fetchall()

    first_realm_data = []
    for achievement in first_realm_achievements:
        achievement_id, name, race, char_class, gender, date = achievement
        formatted_date = datetime.fromtimestamp(date).strftime('%H:%M:%S %d-%m-%Y')

        # Determinar el ícono correcto basado en el logro
        if achievement_id == 457:
            icon_url = f"{settings.URL_PRINCIPAL}/static/nw-themes/nw-ryu/nw-images/nw-icons/achievement-level-80.jpg"
        elif achievement_id in [1408, 1407, 1409, 1404, 1406, 1410, 1413, 1411, 1412, 1405]:
            race_iconss = get_race_iconss(race)
            gender_suffix = "male" if gender == 0 else "female"
            icon_url = f"{settings.URL_PRINCIPAL}/static/nw-themes/nw-ryu/nw-images/nw-races/big-{race_iconss}-{gender_suffix}.webp"
        else:
            icon_url = f"{settings.URL_PRINCIPAL}/static/nw-themes/nw-ryu/nw-images/nw-classes/{get_class_icon(char_class)}-medium.jpg"

        first_realm_data.append({
            'achievement_name': get_achievement_name(achievement_id),
            'name': name,
            'race_iconss': f"big-{get_race_iconss(race)}",
            'icon_url': icon_url,
            'date': formatted_date
        })

    # Renderizar la plantilla con los datos obtenidos
    return render(request, 'realms/novawow_players.html', {
        'guilds': formatted_guilds,
        'players_with_kills': players_with_kills,
        'players_with_achievements': players_with_achievements,
        'classes_data': classes_data,
        'first_realm_data': first_realm_data
    })
