from django.contrib import admin
from .models import Categorie, Vetement, Reservation, Paiement, Notification, Role, Historique

admin.site.register(Categorie)
admin.site.register(Vetement)
admin.site.register(Reservation)
admin.site.register(Paiement)
admin.site.register(Notification)
admin.site.register(Role)
admin.site.register(Historique)
# Register your models here.
