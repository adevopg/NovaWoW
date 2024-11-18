# home/admin.py
from django.contrib import admin
from django import forms
from .models import (
    Noticia, ClienteCategoria, SistemaOperativo, ServerSelection,
    RecruitAFriend, DownloadClientPage, ContentCreator, RecruitReward, GuildRenameSettings, VoteSite
)
from django.db import connections
import logging
from django.shortcuts import redirect
from django_ckeditor_5.widgets import CKEditor5Widget

logger = logging.getLogger(__name__)

# Formulario para el modelo Noticia
class NoticiaAdminForm(forms.ModelForm):
    class Meta:
        model = Noticia
        fields = ['titulo', 'contenido', 'fecha_fin_evento', 'enlace']
        widgets = {
            'contenido': CKEditor5Widget(config_name='default'),
        }

@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    form = NoticiaAdminForm
    list_display = ['titulo', 'fecha_publicacion']
    readonly_fields = ['fecha_publicacion']
    fields = ['titulo', 'contenido', 'fecha_fin_evento', 'enlace']


# Formulario para el modelo RecruitAFriend
class RecruitAFriendAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditor5Widget(config_name='default'))

    class Meta:
        model = RecruitAFriend
        fields = ['title', 'information', 'content']

@admin.register(RecruitAFriend)
class RecruitAFriendAdmin(admin.ModelAdmin):
    form = RecruitAFriendAdminForm
    list_display = ['title', 'updated_at']
    fields = ['title', 'information', 'content']


# Formulario para el modelo DownloadClientPage
class DownloadClientPageAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditor5Widget(config_name='default'))
    mac_instructions = forms.CharField(widget=CKEditor5Widget(config_name='default'))

    class Meta:
        model = DownloadClientPage
        fields = ['title', 'content', 'mac_instructions']

@admin.register(DownloadClientPage)
class DownloadClientPageAdmin(admin.ModelAdmin):
    form = DownloadClientPageAdminForm
    list_display = ['title', 'updated_at']
    fields = ['title', 'content', 'mac_instructions']


# Formulario para el modelo ContentCreator
class ContentCreatorAdminForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditor5Widget(config_name='default'))

    class Meta:
        model = ContentCreator
        fields = [
            'title', 'description', 'content_type', 'subtitle',
            'youtube_video_url', 'avatar_image_url',
            'youtube_channel_url', 'facebook_page_url'
        ]

@admin.register(ContentCreator)
class ContentCreatorAdmin(admin.ModelAdmin):
    form = ContentCreatorAdminForm
    list_display = ['title', 'updated_at']
    fields = [
        'title', 'description', 'content_type', 'subtitle',
        'youtube_video_url', 'avatar_image_url',
        'youtube_channel_url', 'facebook_page_url'
    ]


# Administración para ServerSelection
class ServerSelectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'port', 'gamebuild']
    change_list_template = "admin/server_selection.html"

    def changelist_view(self, request, extra_context=None):
        servers = []
        try:
            with connections['acore_auth'].cursor() as cursor:
                cursor.execute("SELECT id, name, address, port, gamebuild FROM realmlist")
                servers = cursor.fetchall()
        except Exception as e:
            logger.error("Error al obtener servidores: %s", e)

        if request.method == "POST" and "server_selection" in request.POST:
            selected_server_id = int(request.POST["server_selection"])
            selected_server = next((s for s in servers if s[0] == selected_server_id), None)
            if selected_server:
                ServerSelection.objects.all().delete()
                ServerSelection.objects.create(
                    server_id=selected_server[0],
                    name=selected_server[1],
                    address=selected_server[2],
                    port=selected_server[3],
                    gamebuild=selected_server[4]
                )
                return redirect("admin:home_serverselection_changelist")

        extra_context = extra_context or {}
        extra_context['servers'] = servers
        return super().changelist_view(request, extra_context=extra_context)


# Inlines para ClienteCategoria
class SistemaOperativoInline(admin.TabularInline):
    model = SistemaOperativo
    extra = 1

class ClienteCategoriaAdmin(admin.ModelAdmin):
    inlines = [SistemaOperativoInline]
    
    
@admin.register(RecruitReward)
class RecruitRewardAdmin(admin.ModelAdmin):
    list_display = ('required_friends', 'reward_name', 'item_id', 'item_quantity', 'icon_class')
    search_fields = ('reward_name',)

@admin.register(GuildRenameSettings)
class GuildRenameSettingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'cost')
    list_display_links = ('id',)  # Hacemos que 'id' sea el enlace
    list_editable = ('cost',)     # Permitimos que 'cost' sea editable
    fieldsets = (
        (None, {
            'fields': ('cost',)
        }),
    )


@admin.register(VoteSite)
class VoteSiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'points', 'url', 'image_url')
    search_fields = ('name',)
    list_editable = ('points',)
    list_display_links = ('name',)    


# Registro de modelos en el admin
admin.site.register(ClienteCategoria, ClienteCategoriaAdmin)
admin.site.register(SistemaOperativo)
admin.site.register(ServerSelection, ServerSelectionAdmin)
