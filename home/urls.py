from django.urls import path
from . import views
from .views import home_view, download_client_view, content_creators_view

urlpatterns = [
    path('', views.home_view, name='index'),  # Ruta para la página principal
    path('download-client/', views.download_client_view, name='download_client'),
    path('content-creators/', views.content_creators_view, name='content_creators'),
    path('log-in/', views.login_view, name='login'),
    path('log-out/', views.logout_view, name='log-out'),
    path('create-account/', views.register_view, name='register'),
    path('novawow-realm/', views.novawow_realm_view, name='novawow_realm'),
    path('recover/', views.recover_account_view, name='recover'),
    path('contact-us/', views.contact_us_view, name='contact_us'),
    path('legal-notice/', views.legal_notice_view, name='legal_notice'),
    path('terms-and-conditions/', views.terms_and_conditions_view, name='terms_and_conditions'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    path('refund-policy/', views.refund_policy_view, name='refund_policy'),
    path('cookies/', views.cookies_view, name='cookies'),
    path('download-addons/', views.download_addons_view, name='download_addons'),
    path('recruit-a-friend/', views.recruit_a_friend_view, name='recruit_a_friend'),
    path('my-account/', views.my_account, name='my-account'),
    path('not-found/', views.not_found, name='not-found'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('security-token/', views.security_token_view, name='security_token'),
    path('change-email/', views.change_email_view, name='change_email'),
    path('promo-code/', views.promo_code_view, name='promo_code'),
    path('transfer-d-points/', views.transfer_d_points_view, name='transfer_d_points'),
    path('rename-guild/', views.rename_guild_view, name='rename-guild'),
    path('vote-points/', views.vote_points_view, name='vote_points'),
    path('d-points/', views.d_points_view, name='d_points'),
    path('points-history/', views.points_history_view, name='points_history'),
    path('trans-history/', views.trans_history_view, name='trans_history'),
    path('ban-history/', views.ban_history_view, name='ban-history'),
    path('security-history/', views.security_history_view, name='security_history'),
    path('trade-points/', views.trade_points_view, name='trade_points'),
    path('activate-account', views.activate_account_view, name='activate_account'),
    path('help', views.help_view, name='help'),
    
]

handler404 = 'home.views.not_found'
