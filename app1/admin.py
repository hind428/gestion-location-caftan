from django.contrib import admin
from .models import (
    Vetement, Reservation, Categorie, Paiement, 
    Notification, Historique, Panier, UserProfile, Role,
    MessageManager
)


# ==================== ADMIN VETEMENT ====================
class VetementAdmin(admin.ModelAdmin):
    list_display = ['id', 'nom', 'prix_jour', 'est_disponible', 'date_ajout']
    list_editable = ['prix_jour', 'est_disponible']
    list_filter = ['est_disponible', 'categorie', 'genre', 'type_marocain']
    search_fields = ['nom']
    list_per_page = 20


# ==================== ADMIN RESERVATION ====================
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'vetement', 'date_debut', 'date_fin', 'statut', 'validation_manager']
    list_filter = ['statut', 'validation_manager']
    search_fields = ['user__username', 'vetement__nom']
    list_per_page = 20
    readonly_fields = ['date_reservation', 'date_validation']


# ==================== ADMIN CATEGORIE ====================
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['id', 'nom']
    search_fields = ['nom']


# ==================== ADMIN PAIEMENT ====================
class PaiementAdmin(admin.ModelAdmin):
    list_display = ['id', 'reservation', 'montant', 'methode', 'statut', 'date_paiement']
    list_filter = ['statut', 'methode']
    search_fields = ['reservation__user__username']
    readonly_fields = ['date_paiement']


# ==================== ADMIN NOTIFICATION ====================
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'utilisateur', 'titre', 'date', 'lu']
    list_filter = ['lu', 'date', 'type']
    search_fields = ['utilisateur__username', 'titre']
    list_editable = ['lu']


# ==================== ADMIN HISTORIQUE ====================
class HistoriqueAdmin(admin.ModelAdmin):
    list_display = ['id', 'utilisateur', 'action', 'date']
    list_filter = ['date']
    search_fields = ['utilisateur__username', 'action']
    readonly_fields = ['date']


# ==================== ADMIN PANIER ====================
class PanierAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'vetement', 'date_debut', 'date_fin', 'date_ajout']
    search_fields = ['user__username', 'vetement__nom']


# ==================== ADMIN USER PROFILE ====================
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'role', 'telephone']
    list_filter = ['role']
    search_fields = ['user__username']


# ==================== ADMIN ROLE ====================
class RoleAdmin(admin.ModelAdmin):
    list_display = ['id', 'nom']


# ==================== ADMIN MESSAGE MANAGER ====================
class MessageManagerAdmin(admin.ModelAdmin):
    list_display = ['id', 'reservation', 'expediteur', 'message', 'date', 'lu']
    list_filter = ['expediteur', 'lu', 'date']
    search_fields = ['reservation__user__username', 'message']


# ==================== ENREGISTREMENT DES MODÈLES ====================
admin.site.register(Vetement, VetementAdmin)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Categorie, CategorieAdmin)
admin.site.register(Paiement, PaiementAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Historique, HistoriqueAdmin)
admin.site.register(Panier, PanierAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(MessageManager, MessageManagerAdmin)