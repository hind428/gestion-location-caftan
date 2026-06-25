from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from app1 import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Pages principales
    path('', views.accueil, name='accueil'),
    path('homme/', views.homme, name='homme'),
    path('femme/', views.femme, name='femme'),
    path('detail/<int:id>/', views.detail, name='detail'),
    
    # Réservations
    path('mes-reservations/', views.mes_reservations, name='mes_reservations'),
    path('annuler/<int:id>/', views.annuler_reservation, name='annuler_reservation'),
    
    # Authentification
    path('register/', views.register, name='register'),
    path('login/', views.connexion, name='login'),
    path('logout/', views.deconnexion, name='logout'),
    
    # Panier
    path('ajouter-panier/<int:id>/', views.ajouter_panier, name='ajouter_panier'),
    path('panier/', views.panier, name='panier'),
    path('supprimer-panier/<int:id>/', views.supprimer_panier, name='supprimer_panier'),
    path('valider-panier/', views.valider_panier, name='valider_panier'),
    
    # Notifications
    path('notifications/', views.mes_notifications, name='mes_notifications'),
    path('notification-lu/<int:id>/', views.marquer_lu, name='marquer_lu'),
    path('notifications/tout-lire/', views.tout_marquer_lu, name='tout_marquer_lu'),
    
    # Historique
    path('mon-historique/', views.mon_historique, name='mon_historique'),
    
    # Mes paiements
    path('mes-paiements/', views.mes_paiements, name='mes_paiements'),
    
    # Admin Dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('gestion-articles/', views.gestion_articles, name='gestion_articles'),
    path('gestion-reservations/', views.gestion_reservations, name='gestion_reservations'),
    
    # Gestionnaire
    path('creer-gestionnaire/', views.creer_gestionnaire, name='creer_gestionnaire'),
    path('manager-dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('manager-valider/<int:id>/', views.manager_valider_reservation, name='manager_valider_reservation'),
    path('manager-message/<int:id>/', views.manager_envoyer_message, name='manager_envoyer_message'),
    path('manager-notes/<int:id>/', views.manager_ajouter_notes, name='manager_ajouter_notes'),

    path('laisser-avis/<int:id>/', views.laisser_avis, name='laisser_avis'),
    path('gerer-avis/', views.gerer_avis, name='gerer_avis'),
    path('corbeille/', views.corbeille, name='corbeille'),

    path('client-message/<int:id>/', views.client_envoyer_message, name='client_envoyer_message'),
    path('mon-profil/', views.mon_profil, name='mon_profil'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)