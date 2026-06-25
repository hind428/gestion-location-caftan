from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum, Count
from .models import Vetement, Reservation, Paiement
from datetime import datetime

@staff_member_required
def dashboard(request):
    """Dashboard administrateur"""
    
    # Statistiques générales
    total_articles = Vetement.objects.count()
    articles_disponibles = Vetement.objects.filter(est_disponible=True).count()
    total_reservations = Reservation.objects.count()
    reservations_en_attente = Reservation.objects.filter(statut='en_attente').count()
    reservations_confirmees = Reservation.objects.filter(statut='confirmee').count()
    reservations_terminees = Reservation.objects.filter(statut='terminee').count()
    reservations_annulees = Reservation.objects.filter(statut='annulee').count()
    
    # Chiffre d'affaires
    total_ca = Paiement.objects.filter(statut='paye').aggregate(total=Sum('montant'))['total'] or 0
    
    # Réservations du mois
    now = datetime.now()
    debut_mois = datetime(now.year, now.month, 1)
    ca_mois = Paiement.objects.filter(
        statut='paye', 
        date_paiement__gte=debut_mois
    ).aggregate(total=Sum('montant'))['total'] or 0
    
    # Dernières réservations
    dernieres_reservations = Reservation.objects.all().order_by('-date_reservation')[:10]
    
    # Articles les plus réservés
    top_articles = Vetement.objects.annotate(
        nb_reservations=Count('reservation')
    ).order_by('-nb_reservations')[:5]
    
    context = {
        'total_articles': total_articles,
        'articles_disponibles': articles_disponibles,
        'total_reservations': total_reservations,
        'reservations_en_attente': reservations_en_attente,
        'reservations_confirmees': reservations_confirmees,
        'reservations_terminees': reservations_terminees,
        'reservations_annulees': reservations_annulees,
        'total_ca': total_ca,
        'ca_mois': ca_mois,
        'dernieres_reservations': dernieres_reservations,
        'top_articles': top_articles,
    }
    
    return render(request, 'admin/dashboard.html', context)


@staff_member_required
def gestion_articles(request):
    """Gestion des articles"""
    articles = Vetement.objects.all().order_by('-date_ajout')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        article_id = request.POST.get('article_id')
        
        if action == 'supprimer':
            article = Vetement.objects.get(id=article_id)
            article.delete()
            messages.success(request, 'Article supprimé avec succès')
        elif action == 'toggle_disponible':
            article = Vetement.objects.get(id=article_id)
            article.est_disponible = not article.est_disponible
            article.save()
            messages.success(request, 'Statut modifié avec succès')
        
        return redirect('gestion_articles')
    
    context = {'articles': articles}
    return render(request, 'admin/gestion_articles.html', context)


@staff_member_required
def gestion_reservations(request):
    """Gestion des réservations"""
    reservations = Reservation.objects.all().order_by('-date_reservation')
    
    if request.method == 'POST':
        reservation_id = request.POST.get('reservation_id')
        statut = request.POST.get('statut')
        reservation = Reservation.objects.get(id=reservation_id)
        reservation.statut = statut
        reservation.save()
        messages.success(request, f'Réservation #{reservation_id} mise à jour')
        return redirect('gestion_reservations')
    
    context = {'reservations': reservations}
    return render(request, 'admin/gestion_reservations.html', context)