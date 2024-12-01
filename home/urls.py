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
    path('change-email/', views.change_email_view, name='change-email'),
    path('confirm-old-email/', views.confirm_old_email_view, name='confirm-old-email'),
    path('confirm-new-email/', views.confirm_new_email_view, name='confirm-new-email'),
    path('expired-link/', views.expired_link_view, name='expired-link'),
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
    path('novawow-players', views.novawow_players_view, name='novawow_players'),
    path('unstuck-character/', views.unstuck_character_view, name='unstuck-character'),
    path('revive-character/', views.revive_character_view, name='revive-character'),
    path('rename-character/', views.rename_character_view, name='rename-character'),
    path('rename-success/', views.rename_success_view, name='rename-success'),
    path('rename-cancel/', views.rename_cancel_view, name='rename-cancel'),
    path('customize-character/', views.customize_character_view, name='customize-character'),
    path('customize-success/', views.customize_success_view, name='customize-success'),
    path('customize-cancel/', views.customize_cancel_view, name='customize-cancel'),
    path('change-race-character/', views.change_race_character_view, name ='change-race-character'),
    path('change-race-success/', views.change_race_success_view, name='change-race-success'),
    path('change-race-cancel/'  , views.change_race_cancel_view, name='change-race-cancel'),
    path('change-faction-character/', views.change_faction_character_view, name='change-faction-character'),
    path('change-faction-success/', views.change_faction_success_view, name='change-faction-success'),
    path('change-faction-cancel/'  , views.change_faction_cancel_view, name='change-faction-cancel'),
    path('level-up-character/', views.level_up_character_view, name='level_up_character'),
    path('level-up-success/', views.level_up_success_view, name='level-up-success'),
    path('level-up-cancel/'  , views.level_up_cancel_view, name='level-up-cancel'),
    path('gold-character/'  , views.gold_character_view, name='gold-character'),
    path('gold-success/'  , views.gold_success_view, name='gold-success'),
    path('gold-cancel/'  , views.gold_cancel_view, name='gold-cancel'),
    path('transfer-character/'  , views.transfer_character_view, name='transfer-character'),
    path('transfer-success/'  , views.transfer_success_view, name='transfer-success'),
    path('transfer-cancel/'  , views.transfer_cancel_view, name='transfer-cancel'),
    path('store-novawow/'  , views.store_novawow_view, name='store-novawow'),
    
    
    
    
    
    
]

handler404 = 'home.views.not_found'
