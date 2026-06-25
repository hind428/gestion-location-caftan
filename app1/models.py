from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg


# ==================== CATEGORIE ====================
class Categorie(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom


# ==================== VÊTEMENTS ====================
class Vetement(models.Model):
    # Types de vêtements marocains
    TYPE_MAROCAIN = [
        ('caftan', 'Caftan'),
        ('takchita', 'Takchita'),
        ('djellaba', 'Djellaba'),
        ('jabador', 'Jabador'),
        ('gandoura', 'Gandoura'),
        ('selham', 'Selham'),
    ]
    
    # Genre
    GENRE_CHOICES = [
        ('homme', 'Homme'),
        ('femme', 'Femme'),
        ('mixte', 'Mixte'),
    ]
    
    # Informations de base
    nom = models.CharField(max_length=200)
    type_marocain = models.CharField(max_length=50, choices=TYPE_MAROCAIN, default='caftan')
    genre = models.CharField(max_length=10, choices=GENRE_CHOICES, default='femme')
    description = models.TextField()
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Images
    image = models.ImageField(upload_to='vetements/', null=True, blank=True)
    image1 = models.ImageField(upload_to='vetements/', null=True, blank=True)
    image2 = models.ImageField(upload_to='vetements/', null=True, blank=True)
    
    # Spécifications
    taille = models.CharField(max_length=20, choices=[
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
    ], blank=True, null=True)
    couleur = models.CharField(max_length=50, blank=True, null=True)
    matiere = models.CharField(max_length=100, blank=True, null=True)
    marque = models.CharField(max_length=100, blank=True, null=True)
    
    # Prix
    prix_jour = models.DecimalField(max_digits=10, decimal_places=2)
    caution = models.DecimalField(max_digits=10, decimal_places=2, default=200)
    
    # Disponibilité
    est_disponible = models.BooleanField(default=True)
    date_ajout = models.DateTimeField(auto_now_add=True, null=True)
    est_supprime = models.BooleanField(default=False)
    date_suppression = models.DateTimeField(null=True, blank=True)
    @property
    def note_moyenne(self):
        avg = self.avis.aggregate(moyenne=Avg('note'))['moyenne']
        return round(avg, 1) if avg else 0
    
    @property
    def nb_avis(self):
        return self.avis.count()
    
    def __str__(self):
        return f"{self.get_type_marocain_display()} - {self.nom}"


# ==================== PROFIL UTILISATEUR (RÔLE) ====================
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('client', 'Client'),
        ('gestionnaire', 'Gestionnaire'),
        ('admin', 'Administrateur'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    telephone = models.CharField(max_length=15, blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


# ==================== RÉSERVATION ====================
class Reservation(models.Model):
    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirmee', 'Confirmée'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    vetement = models.ForeignKey(Vetement, on_delete=models.CASCADE)
    date_reservation = models.DateTimeField(auto_now_add=True)
    date_debut = models.DateField()
    date_fin = models.DateField()
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    notes = models.TextField(blank=True, null=True)
    
    # Champs pour le gestionnaire
    validation_manager = models.BooleanField(default=False)
    manager_notes = models.TextField(blank=True, null=True)
    date_validation = models.DateTimeField(null=True, blank=True)
    
    @property
    def nombre_jours(self):
        return (self.date_fin - self.date_debut).days + 1
    
    @property
    def montant_total(self):
        return self.nombre_jours * self.vetement.prix_jour
    
    def __str__(self):
        return f"{self.user.username} - {self.vetement.nom}"


# ==================== PAIEMENT ====================
class Paiement(models.Model):
    METHODE_CHOICES = [
        ('carte', 'Carte bancaire'),
        ('paypal', 'PayPal'),
        ('virement', 'Virement'),
        ('especes', 'Espèces'),
    ]
    
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('paye', 'Payé'),
        ('echoue', 'Échoué'),
        ('rembourse', 'Remboursé'),
    ]
    
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='paiements')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    methode = models.CharField(max_length=50, choices=METHODE_CHOICES)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_paiement = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.montant} DH - {self.get_statut_display()}"


# ==================== PANIER ====================
class Panier(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='panier')
    vetement = models.ForeignKey(Vetement, on_delete=models.CASCADE)
    date_debut = models.DateField()
    date_fin = models.DateField()
    quantite = models.IntegerField(default=1)
    date_ajout = models.DateTimeField(auto_now_add=True)
    
    @property
    def nombre_jours(self):
        return (self.date_fin - self.date_debut).days + 1
    
    @property
    def sous_total(self):
        return self.nombre_jours * self.vetement.prix_jour
    
    class Meta:
        unique_together = ['user', 'vetement', 'date_debut', 'date_fin']
    
    def __str__(self):
        return f"{self.user.username} - {self.vetement.nom}"


# ==================== NOTIFICATION ====================
class Notification(models.Model):
    TYPE_CHOICES = [
        ('info', 'Information'),
        ('success', 'Succès'),
        ('warning', 'Avertissement'),
        ('error', 'Erreur'),
    ]
    
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    titre = models.CharField(max_length=200, default='Notification')
    message = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    date = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.titre} - {self.utilisateur.username}"


# ==================== HISTORIQUE ====================
class Historique(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='historiques')
    action = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.utilisateur.username} - {self.action}"


# ==================== MESSAGE MANAGER (Gestionnaire/Client) ====================
class MessageManager(models.Model):
    """Messages entre gestionnaire et clients"""
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='messages')
    expediteur = models.CharField(max_length=20, choices=[
        ('gestionnaire', 'Gestionnaire'),
        ('client', 'Client'),
    ])
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Message #{self.id} - Réservation #{self.reservation.id}"


# ==================== AVIS ET NOTES ====================
class Avis(models.Model):
    NOTE_CHOICES = [
        (1, '⭐ 1 étoile'),
        (2, '⭐⭐ 2 étoiles'),
        (3, '⭐⭐⭐ 3 étoiles'),
        (4, '⭐⭐⭐⭐ 4 étoiles'),
        (5, '⭐⭐⭐⭐⭐ 5 étoiles'),
    ]
    
    vetement = models.ForeignKey(Vetement, on_delete=models.CASCADE, related_name='avis')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='avis')
    note = models.IntegerField(choices=NOTE_CHOICES)
    commentaire = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    reservation = models.ForeignKey(Reservation, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['user', 'vetement']  # Un client ne peut pas laisser 2 avis sur le même article
    
    def __str__(self):
        return f"{self.user.username} - {self.vetement.nom} - {self.note}⭐"


# ==================== ROLE (Optionnel - gardé pour compatibilité) ====================
class Role(models.Model):
    nom = models.CharField(max_length=50)

    def __str__(self):
        return self.nom