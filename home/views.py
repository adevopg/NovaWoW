import socket
import hashlib
import gmpy2
import binascii
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import connections
from django.contrib import messages
from django.contrib.auth import logout
from django import forms
from .models import Noticia, ClienteCategoria, ServerSelection, RecruitAFriend, DownloadClientPage, ContentCreator, RecruitReward, ClaimedReward
from django.views.decorators.csrf import csrf_exempt
import logging
from datetime import datetime, timedelta
from .zone_definitions import get_zone_name
from .ac_soap import execute_soap_command
from django.utils import timezone


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
def register_view(request):
    return render(request, 'auth/register.html')

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
        return redirect('login')

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
        return redirect('login')

    account_id = account_data[0]
    
    # Obtener los personajes asociados a la cuenta
    characters = get_account_characters(account_id)
    has_characters = bool(characters)

    # Obtener el estado de la cuenta
    account_status = get_account_status(account_id)

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
    return render(request, 'account/change_password.html')


def security_token_view(request):
    """
    Vista para la página de 'Security Token'.
    Simplemente renderiza un template con información relevante.
    """
    return render(request, 'account/security_token.html')

def change_email_view(request):
    """
    Vista para la página de 'Cambiar Correo'.
    Simplemente renderiza un template con información relevante.
    """
    return render(request, 'account/change_email.html')
    
def promo_code_view(request):
    return render(request, 'account/promo_code.html')

def transfer_d_points_view(request):
    # Renderizar la plantilla para la transferencia de puntos
    return render(request, 'account/transfer_d_points.html')    

def rename_guild_view(request):
    # Renderizar la plantilla para la transferencia de puntos
    return render(request, 'account/rename_guild.html')
    
def vote_points_view(request):
    """
    Vista para la página de puntos de votación.
    """
    return render(request, 'account/vote_points.html')

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
    