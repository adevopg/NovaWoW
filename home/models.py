# home/models.py
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid
from django.contrib.auth.models import User
import secrets

class Noticia(models.Model):
    titulo = models.CharField(max_length=200)
    contenido = CKEditor5Field('Contenido', config_name='default')
    fecha_publicacion = models.DateTimeField(auto_now=True)  # Cambiado a DateTimeField
    fecha_fin_evento = models.DateField(null=True, blank=True)
    enlace = models.URLField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.titulo
        
class UnstuckHistory(models.Model):
    character_name = models.CharField(max_length=50)
    used_at = models.DateTimeField()        


class ClienteCategoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.nombre


class SistemaOperativo(models.Model):
    categoria = models.ForeignKey(ClienteCategoria, related_name='sistemas_operativos', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    url_descarga = models.URLField()

    def __str__(self):
        return f"{self.nombre} - {self.categoria.nombre}"


class ServerSelection(models.Model):
    server_id = models.IntegerField()
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    port = models.IntegerField()
    gamebuild = models.IntegerField()

    def __str__(self):
        expansion = 'WotLK' if self.gamebuild == 12340 else 'Cataclysm' if self.gamebuild == 15595 else 'Unknown'
        return f"{self.name} ({expansion})"


class RecruitAFriend(models.Model):
    title = models.CharField(max_length=255, default="Recluta a un amigo")
    information = models.CharField(max_length=255, default="Información")
    content = CKEditor5Field('Contenido', config_name='default')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class DownloadClientPage(models.Model):
    title = models.CharField(max_length=255, default="Descarga del cliente")
    content = CKEditor5Field('Contenido', config_name='default')
    mac_instructions = CKEditor5Field('Instrucciones para macOS', blank=True, null=True, config_name='default')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ContentCreator(models.Model):
    title = models.CharField(max_length=200)
    description = CKEditor5Field('Descripción', config_name='default')
    content_type = models.CharField(max_length=60, default="Contenido general")
    subtitle = models.CharField(max_length=60, default="Nova WoW")
    youtube_video_url = models.URLField(max_length=300, blank=True, null=True)
    avatar_image_url = models.URLField(max_length=300, blank=True, null=True)
    youtube_channel_url = models.URLField(max_length=300, blank=True, null=True)
    facebook_page_url = models.URLField(max_length=300, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titles     

class RecruitReward(models.Model):
    required_friends = models.IntegerField()
    reward_name = models.CharField(max_length=100)
    item_id = models.IntegerField()
    item_quantity = models.IntegerField(default=1)
    item_link = models.URLField()
    icon_class = models.CharField(max_length=50, help_text="Clase CSS para el icono (ej. 'icontinyl q3')")

    def __str__(self):
        return f"{self.required_friends} amigos - {self.reward_name}"

class ClaimedReward(models.Model):
    recruit_reward = models.ForeignKey(RecruitReward, on_delete=models.CASCADE, related_name='claimed_rewards')
    account_id = models.IntegerField()
    character_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    claimed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.CharField(max_length=45, default='127.0.0.1')  # Añadir un valor predeterminado

    def __str__(self):
        return f"{self.username} - {self.recruit_reward.reward_name} - {self.claimed_at}"

from django.db import models
from django.utils import timezone

from django.db import models
from django.utils import timezone

class AccountActivation(models.Model):
    username = models.CharField(max_length=17)
    email = models.EmailField()
    old_email = models.EmailField(null=True, blank=True)
    password = models.CharField(max_length=64)
    salt = models.BinaryField(max_length=32)
    verifier = models.BinaryField(max_length=32)
    recruiter_id = models.IntegerField(null=True, blank=True)
    hash = models.CharField(max_length=32, unique=True)
    old_email_hash = models.CharField(max_length=32, null=True, blank=True)
    is_used = models.BooleanField(default=False)  # Indica si el old_email_hash ha sido usado
    is_new_email_used = models.BooleanField(default=False)  # Indica si el hash del nuevo correo ha sido usado
    created_at = models.DateTimeField(default=timezone.now)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(hours=1)

    def __str__(self):
        return f"Activation for {self.username}"



class SecurityToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    ip_address = models.GenericIPAddressField()

    def __str__(self):
        return f"Token for {self.user.username}"
        
        
class GuildRenameSettings(models.Model):
    cost = models.IntegerField(default=1000, help_text="Costo en Donation Points (DP) para renombrar una hermandad.")

    def __str__(self):
        return f"Costo actual: {self.cost} DP"

    class Meta:
        verbose_name = "Configuración de Renombrar Hermandad"
        verbose_name_plural = "Configuraciones de Renombrar Hermandad"


class VoteSite(models.Model):
    name = models.CharField(max_length=100, unique=True)
    url = models.URLField(max_length=200, help_text="URL del sitio de votación")
    image_url = models.URLField(max_length=300, help_text="URL completa de la imagen")
    points = models.IntegerField(default=1, help_text="Puntos otorgados por votar")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class VoteLog(models.Model):
    account_id = models.IntegerField()
    vote_site = models.ForeignKey('VoteSite', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_vote_time = models.DateTimeField(null=True, blank=True)
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Voto para {self.vote_site.name} por cuenta {self.account_id}"


class HomeApiPoints(models.Model):
    accountID = models.IntegerField(unique=True)
    vp = models.IntegerField(default=0)
    dp = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'home_api_points'

    def __str__(self):
        return f"Cuenta {self.accountID} - PV: {self.vp}, DP: {self.dp}"        
        