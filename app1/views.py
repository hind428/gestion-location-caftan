from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib.admin.views.decorators import staff_member_required
from datetime import datetime, date
from django.db.models import Sum, Count, Avg
from .models import Vetement, Categorie, Reservation, Paiement, Notification, Panier, Historique, MessageManager, UserProfile, Avis


# ==================== ACCUEIL ====================
def accueil(request):
    # Si l'utilisateur est admin ou gestionnaire, rediriger vers son dashboard
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            if profile.role == 'admin' or request.user.username == 'hind':
                return redirect('admin_dashboard')
            elif profile.role == 'gestionnaire':
                return redirect('manager_dashboard')
        except:
            pass
    
    # Pour les clients et visiteurs, afficher la page d'accueil normale
    recherche = request.GET.get('q', '')
    categorie_id = request.GET.get('categorie')
    
    vetements = Vetement.objects.filter(est_supprime=False, est_disponible=True)
    
    if recherche:
        vetements = vetements.filter(nom__icontains=recherche)
    
    if categorie_id:
        vetements = vetements.filter(categorie_id=categorie_id)
    
    user_reservations_count = 0
    if request.user.is_authenticated:
        user_reservations_count = Reservation.objects.filter(user=request.user).count()
    
    categories = Categorie.objects.all()
    
    context = {
        'vetements': vetements,
        'recherche': recherche,
        'user_reservations_count': user_reservations_count,
        'user': request.user,
        'categories': categories,
    }
    return render(request, 'app1/accueil.html', context)


# ==================== HOMME ====================
def homme(request):
    vetements = Vetement.objects.filter(categorie__nom="Homme", est_supprime=False, est_disponible=True)
    context = {
        'vetements': vetements,
        'user': request.user,
    }
    return render(request, 'app1/homme.html', context)


# ==================== FEMME ====================
def femme(request):
    vetements = Vetement.objects.filter(categorie__nom="Femme", est_supprime=False, est_disponible=True)
    context = {
        'vetements': vetements,
        'user': request.user,
    }
    return render(request, 'app1/femme.html', context)


# ==================== DÉTAIL ====================
def detail(request, id):
    vetement = get_object_or_404(Vetement, id=id)
    
    if vetement.est_supprime:
        messages.error(request, 'Cet article n\'existe plus.')
        return redirect('accueil')
    
    if not vetement.est_disponible:
        messages.warning(request, '⚠️ Cet article n\'est pas disponible pour le moment.')
    
    context = {
        'article': vetement,
        'today': datetime.now().date().strftime('%Y-%m-%d'),
    }
    return render(request, 'app1/detail.html', context)


# ==================== AJOUTER AU PANIER ====================
@login_required
def ajouter_panier(request, id):
    vetement = get_object_or_404(Vetement, id=id)
    
    if vetement.est_supprime or not vetement.est_disponible:
        messages.error(request, '❌ Cet article n\'est pas disponible.')
        return redirect('detail', id=id)
    
    if request.method == 'POST':
        date_debut = request.POST.get('date_debut')
        date_fin = request.POST.get('date_fin')
        
        try:
            debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
            fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
            aujourdhui = date.today()
            
            if debut < aujourdhui:
                messages.error(request, '❌ La date de début ne peut pas être dans le passé !')
                return redirect('detail', id=id)
            
            if fin < debut:
                messages.error(request, '❌ La date de fin doit être après la date de début !')
                return redirect('detail', id=id)
            
            if (fin - debut).days > 30:
                messages.error(request, '❌ La durée maximale de location est de 30 jours !')
                return redirect('detail', id=id)
            
        except ValueError:
            messages.error(request, '❌ Format de date invalide !')
            return redirect('detail', id=id)
        
        panier_item, created = Panier.objects.get_or_create(
            user=request.user,
            vetement=vetement,
            date_debut=date_debut,
            date_fin=date_fin,
            defaults={'quantite': 1}
        )
        
        if not created:
            messages.warning(request, 'Cet article est déjà dans votre panier')
        else:
            Notification.objects.create(
                utilisateur=request.user,
                titre='Article ajouté',
                message=f'{vetement.nom} a été ajouté à votre panier du {date_debut} au {date_fin}',
                type='success'
            )
            messages.success(request, f'{vetement.nom} ajouté au panier')
        
        ajouter_historique(request.user, f"Ajout de {vetement.nom} au panier du {date_debut} au {date_fin}")
        return redirect('panier')
    
    return redirect('detail', id=id)


# ==================== PANIER ====================
@login_required
def panier(request):
    panier_items = Panier.objects.filter(user=request.user)
    total = sum(item.sous_total for item in panier_items)
    
    context = {
        'panier_items': panier_items,
        'total': total,
        'total_articles': panier_items.count(),
    }
    return render(request, 'app1/panier.html', context)


# ==================== SUPPRIMER PANIER ====================
@login_required
def supprimer_panier(request, id):
    panier_item = get_object_or_404(Panier, id=id, user=request.user)
    panier_item.delete()
    messages.success(request, 'Article supprimé du panier')
    return redirect('panier')


# ==================== VALIDER PANIER ====================
@login_required
def valider_panier(request):
    panier_items = Panier.objects.filter(user=request.user)
    
    if not panier_items:
        messages.error(request, 'Votre panier est vide')
        return redirect('panier')
    
    total = sum(item.sous_total for item in panier_items)
    
    if request.method == 'POST':
        nom_carte = request.POST.get('nom_carte')
        num_carte = request.POST.get('num_carte')
        date_exp = request.POST.get('date_exp')
        cvv = request.POST.get('cvv')
        methode_paiement = request.POST.get('methode_paiement')
        
        if not nom_carte or not num_carte or not date_exp or not cvv:
            messages.error(request, 'Veuillez remplir tous les champs de paiement')
            return redirect('valider_panier')
        
        for item in panier_items:
            reservation = Reservation.objects.create(
                user=request.user,
                vetement=item.vetement,
                date_debut=item.date_debut,
                date_fin=item.date_fin,
                statut='en_attente',
                validation_manager=False
            )
            
            Paiement.objects.create(
                reservation=reservation,
                montant=item.sous_total,
                methode=methode_paiement,
                statut='paye'
            )
            
            ajouter_historique(request.user, f"Paiement réussi pour {item.vetement.nom}")
            item.delete()
        
        Notification.objects.create(
            utilisateur=request.user,
            titre='Commande payée',
            message=f'Votre commande a été payée. Total: {total} DH. En attente de validation par le gestionnaire.',
            type='success'
        )
        
        messages.success(request, f'✅ Paiement effectué avec succès ! Total: {total} DH')
        return redirect('mes_reservations')
    
    context = {
        'panier_items': panier_items,
        'total': total,
    }
    return render(request, 'app1/valider_panier.html', context)


# ==================== MES RÉSERVATIONS ====================
@login_required
def mes_reservations(request):
    reservations = Reservation.objects.filter(user=request.user).order_by('-date_reservation')
    
    context = {
        'reservations': reservations,
        'total_reservations': reservations.count(),
        'reservations_actives': reservations.filter(statut__in=['en_attente', 'confirmee']).count(),
    }
    return render(request, 'app1/mes_reservations.html', context)


# ==================== MES PAIEMENTS ====================
@login_required
def mes_paiements(request):
    paiements = Paiement.objects.filter(
        reservation__user=request.user
    ).order_by('-date_paiement')
    
    total_paye = paiements.filter(statut='paye').aggregate(total=Sum('montant'))['total'] or 0
    total_paiements = paiements.count()
    
    context = {
        'paiements': paiements,
        'total_paye': total_paye,
        'total_paiements': total_paiements,
    }
    return render(request, 'app1/mes_paiements.html', context)


# ==================== ANNULER RÉSERVATION ====================
@login_required
def annuler_reservation(request, id):
    reservation = get_object_or_404(Reservation, id=id, user=request.user)
    
    if request.method == 'POST':
        reservation.statut = 'annulee'
        reservation.save()
        ajouter_historique(request.user, f"Annulation de la réservation #{id}")
        messages.success(request, 'Réservation annulée avec succès.')
        return redirect('mes_reservations')
    
    return render(request, 'annuler_reservation.html', {'reservation': reservation})


# ==================== NOTIFICATIONS ====================
@login_required
def mes_notifications(request):
    notifications = Notification.objects.filter(utilisateur=request.user).order_by('-date')
    non_lues = notifications.filter(lu=False).count()
    
    context = {
        'notifications': notifications,
        'non_lues': non_lues,
    }
    return render(request, 'app1/notifications.html', context)


@login_required
def marquer_lu(request, id):
    notification = get_object_or_404(Notification, id=id, utilisateur=request.user)
    notification.lu = True
    notification.save()
    return redirect('mes_notifications')


@login_required
def tout_marquer_lu(request):
    Notification.objects.filter(utilisateur=request.user, lu=False).update(lu=True)
    messages.success(request, 'Toutes les notifications ont été marquées comme lues')
    return redirect('mes_notifications')


# ==================== HISTORIQUE ====================
@login_required
def mon_historique(request):
    historique = Historique.objects.filter(utilisateur=request.user).order_by('-date')
    context = {
        'historique': historique,
        'total': historique.count(),
    }
    return render(request, 'app1/historique.html', context)


# ==================== INSCRIPTION ====================
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if not username or not email or not password:
            messages.error(request, 'Tous les champs sont obligatoires.')
            return render(request, 'register.html')
        
        if password != confirm_password:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
            return render(request, 'register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Ce nom d\'utilisateur existe déjà.')
            return render(request, 'register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Cet email est déjà utilisé.')
            return render(request, 'register.html')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        
        UserProfile.objects.create(user=user, role='client')
        
        ajouter_historique(user, f"Inscription sur la plateforme")
        
        messages.success(request, 'Compte créé avec succès! Connectez-vous.')
        return redirect('login')
    
    return render(request, 'register.html')


# ==================== CONNEXION ====================
@csrf_protect
def connexion(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None
        
        if user is not None:
            login(request, user)
            ajouter_historique(request.user, "Connexion réussie")
            
            try:
                profile = user.profile
                if profile.role == 'gestionnaire':
                    messages.success(request, f'Bienvenue Gestionnaire {user.username}!')
                    return redirect('manager_dashboard')
                elif profile.role == 'admin' or user.username == 'hind':
                    messages.success(request, f'Bienvenue Admin {user.username}!')
                    return redirect('admin_dashboard')
                else:
                    messages.success(request, f'Bienvenue {user.username}!')
                    return redirect('accueil')
            except:
                UserProfile.objects.create(user=user, role='client')
                messages.success(request, f'Bienvenue {user.username}!')
                return redirect('accueil')
        else:
            messages.error(request, 'Email ou mot de passe incorrect.')
            return redirect('login')
    
    return render(request, 'login.html')


# ==================== DÉCONNEXION ====================
def deconnexion(request):
    logout(request)
    messages.success(request, 'Vous êtes déconnecté.')
    return redirect('login')


# ==================== FONCTION HISTORIQUE ====================
def ajouter_historique(user, action):
    if user.is_authenticated:
        Historique.objects.create(utilisateur=user, action=action)


# ==================== ADMIN DASHBOARD ====================
@staff_member_required
def admin_dashboard(request):
    total_articles = Vetement.objects.filter(est_supprime=False).count()
    total_reservations = Reservation.objects.count()
    total_users = User.objects.count()
    total_ca = Paiement.objects.filter(statut='paye').aggregate(total=Sum('montant'))['total'] or 0
    
    reservations_en_attente = Reservation.objects.filter(statut='en_attente').count()
    reservations_confirmees = Reservation.objects.filter(statut='confirmee').count()
    reservations_terminees = Reservation.objects.filter(statut='terminee').count()
    reservations_annulees = Reservation.objects.filter(statut='annulee').count()
    
    dernieres_reservations = Reservation.objects.all().order_by('-date_reservation')[:10]
    
    top_articles = Vetement.objects.filter(est_supprime=False).annotate(
        nb_reservations=Count('reservation')
    ).order_by('-nb_reservations')[:5]
    
    context = {
        'total_articles': total_articles,
        'total_reservations': total_reservations,
        'total_users': total_users,
        'total_ca': total_ca,
        'reservations_en_attente': reservations_en_attente,
        'reservations_confirmees': reservations_confirmees,
        'reservations_terminees': reservations_terminees,
        'reservations_annulees': reservations_annulees,
        'dernieres_reservations': dernieres_reservations,
        'top_articles': top_articles,
    }
    return render(request, 'admin/dashboard.html', context)


# ==================== GESTION ARTICLES ====================
@staff_member_required
def gestion_articles(request):
    articles = Vetement.objects.filter(est_supprime=False).order_by('-date_ajout')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        article_id = request.POST.get('article_id')
        article = Vetement.objects.get(id=article_id)
        
        if action == 'supprimer':
            article.est_supprime = True
            article.date_suppression = datetime.now()
            article.save()
            messages.warning(request, f'Article "{article.nom}" déplacé vers la corbeille')
        elif action == 'toggle_disponible':
            article.est_disponible = not article.est_disponible
            article.save()
            status = "disponible" if article.est_disponible else "indisponible"
            messages.success(request, f'Article "{article.nom}" maintenant {status}')
        
        return redirect('gestion_articles')
    
    return render(request, 'admin/gestion_articles.html', {'articles': articles})


# ==================== GESTION RÉSERVATIONS ====================
@staff_member_required
def gestion_reservations(request):
    reservations = Reservation.objects.all().order_by('-date_reservation')
    
    if request.method == 'POST':
        reservation_id = request.POST.get('reservation_id')
        statut = request.POST.get('statut')
        reservation = Reservation.objects.get(id=reservation_id)
        reservation.statut = statut
        reservation.save()
        messages.success(request, f'Réservation #{reservation_id} mise à jour')
        return redirect('gestion_reservations')
    
    return render(request, 'admin/gestion_reservations.html', {'reservations': reservations})


# ==================== CORBEILLE ====================
@staff_member_required
def corbeille(request):
    articles_supprimes = Vetement.objects.filter(est_supprime=True).order_by('-date_suppression')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        article_id = request.POST.get('article_id')
        article = Vetement.objects.get(id=article_id)
        
        if action == 'restaurer':
            article.est_supprime = False
            article.date_suppression = None
            article.save()
            messages.success(request, f'Article "{article.nom}" restauré avec succès')
        elif action == 'supprimer_definitivement':
            article.delete()
            messages.success(request, f'Article "{article.nom}" supprimé définitivement')
        
        return redirect('corbeille')
    
    context = {
        'articles_supprimes': articles_supprimes,
    }
    return render(request, 'admin/corbeille.html', context)


# ==================== CRÉER GESTIONNAIRE ====================
@staff_member_required
def creer_gestionnaire(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Ce nom d\'utilisateur existe déjà')
            return redirect('creer_gestionnaire')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Cet email existe déjà')
            return redirect('creer_gestionnaire')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_staff = True
        user.save()
        
        UserProfile.objects.create(user=user, role='gestionnaire')
        
        messages.success(request, f'✅ Gestionnaire {username} créé avec succès !')
        return redirect('admin_dashboard')
    
    return render(request, 'admin/creer_gestionnaire.html')


# ==================== GESTIONNAIRE DASHBOARD ====================
def manager_dashboard(request):
    try:
        if request.user.profile.role != 'gestionnaire':
            messages.error(request, 'Accès non autorisé')
            return redirect('accueil')
    except:
        messages.error(request, 'Accès non autorisé')
        return redirect('accueil')
    
    reservations_en_attente = Reservation.objects.filter(statut='en_attente', validation_manager=False).count()
    reservations_validees = Reservation.objects.filter(validation_manager=True).count()
    total_reservations = Reservation.objects.count()
    
    reservations = Reservation.objects.all().order_by('-date_reservation')
    
    context = {
        'reservations': reservations,
        'reservations_en_attente': reservations_en_attente,
        'reservations_validees': reservations_validees,
        'total_reservations': total_reservations,
    }
    return render(request, 'app1/manager_dashboard.html', context)


@staff_member_required
def manager_valider_reservation(request, id):
    reservation = get_object_or_404(Reservation, id=id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'accepter':
            reservation.statut = 'confirmee'
            reservation.validation_manager = True
            reservation.date_validation = datetime.now()
            
            Notification.objects.create(
                utilisateur=reservation.user,
                titre='✅ Réservation acceptée',
                message=f'Votre réservation pour {reservation.vetement.nom} a été acceptée.',
                type='success'
            )
            messages.success(request, f'✅ Réservation #{id} acceptée')
        elif action == 'refuser':
            reservation.statut = 'annulee'
            reservation.validation_manager = False
            
            Notification.objects.create(
                utilisateur=reservation.user,
                titre='❌ Réservation refusée',
                message=f'Votre réservation pour {reservation.vetement.nom} a été refusée.',
                type='error'
            )
            messages.success(request, f'❌ Réservation #{id} refusée')
        
        reservation.save()
        return redirect('manager_dashboard')
    
    return redirect('manager_dashboard')


@staff_member_required
def manager_envoyer_message(request, id):
    reservation = get_object_or_404(Reservation, id=id)
    
    if request.method == 'POST':
        message = request.POST.get('message')
        
        if message:
            MessageManager.objects.create(
                reservation=reservation,
                expediteur='gestionnaire',
                message=message,
                lu=False
            )
            
            Notification.objects.create(
                utilisateur=reservation.user,
                titre='📩 Nouveau message',
                message=f'Message concernant votre réservation #{reservation.id}',
                type='info'
            )
            
            messages.success(request, 'Message envoyé')
    
    return redirect('manager_dashboard')


@staff_member_required
def manager_ajouter_notes(request, id):
    reservation = get_object_or_404(Reservation, id=id)
    
    if request.method == 'POST':
        notes = request.POST.get('notes')
        reservation.manager_notes = notes
        reservation.save()
        messages.success(request, 'Notes ajoutées')
    
    return redirect('manager_dashboard')


# ==================== AVIS ====================
@staff_member_required
def gerer_avis(request):
    avis = Avis.objects.all().order_by('-date')
    
    if request.method == 'POST':
        avis_id = request.POST.get('avis_id')
        action = request.POST.get('action')
        avis_obj = Avis.objects.get(id=avis_id)
        
        if action == 'supprimer':
            avis_obj.delete()
            messages.success(request, 'Avis supprimé avec succès')
        
        return redirect('gerer_avis')
    
    context = {
        'avis': avis,
        'total_avis': avis.count(),
        'note_moyenne': avis.aggregate(moyenne=Avg('note'))['moyenne'] or 0,
    }
    return render(request, 'admin/gerer_avis.html', context)


@login_required
def laisser_avis(request, id):
    vetement = get_object_or_404(Vetement, id=id)
    
    if vetement.est_supprime:
        messages.error(request, 'Article non trouvé')
        return redirect('accueil')
    
    a_reserve = Reservation.objects.filter(
        user=request.user,
        vetement=vetement,
        statut__in=['terminee', 'confirmee']
    ).exists()
    
    if not a_reserve:
        messages.error(request, 'Vous devez avoir loué cet article pour laisser un avis')
        return redirect('detail', id=id)
    
    avis_existant = Avis.objects.filter(user=request.user, vetement=vetement).first()
    
    if request.method == 'POST':
        note = request.POST.get('note')
        commentaire = request.POST.get('commentaire')
        
        if avis_existant:
            avis_existant.note = note
            avis_existant.commentaire = commentaire
            avis_existant.save()
            messages.success(request, 'Votre avis a été modifié avec succès !')
        else:
            Avis.objects.create(
                vetement=vetement,
                user=request.user,
                note=note,
                commentaire=commentaire
            )
            messages.success(request, 'Merci pour votre avis !')
        
        return redirect('detail', id=id)
    
    context = {
        'article': vetement,
        'avis_existant': avis_existant,
    }
    return render(request, 'app1/laisser_avis.html', context)


# ==================== PROFIL UTILISATEUR ====================
from django.contrib.auth import update_session_auth_hash

@login_required
def mon_profil(request):
    user = request.user
    profile = UserProfile.objects.get(user=user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_info':
            username = request.POST.get('username')
            email = request.POST.get('email')
            telephone = request.POST.get('telephone')
            adresse = request.POST.get('adresse')
            
            if username and username != user.username:
                if User.objects.filter(username=username).exclude(id=user.id).exists():
                    messages.error(request, 'Ce nom d\'utilisateur est déjà pris')
                else:
                    user.username = username
                    user.save()
                    messages.success(request, 'Nom d\'utilisateur modifié avec succès')
            
            if email and email != user.email:
                if User.objects.filter(email=email).exclude(id=user.id).exists():
                    messages.error(request, 'Cet email est déjà utilisé')
                else:
                    user.email = email
                    user.save()
                    messages.success(request, 'Email modifié avec succès')
            
            profile.telephone = telephone
            profile.adresse = adresse
            profile.save()
            messages.success(request, 'Vos informations ont été mises à jour')
            return redirect('mon_profil')
        
        elif action == 'update_password':
            old_password = request.POST.get('old_password')
            new_password1 = request.POST.get('new_password1')
            new_password2 = request.POST.get('new_password2')
            
            if not user.check_password(old_password):
                messages.error(request, 'Mot de passe actuel incorrect')
            elif new_password1 != new_password2:
                messages.error(request, 'Les nouveaux mots de passe ne correspondent pas')
            elif len(new_password1) < 6:
                messages.error(request, 'Le mot de passe doit contenir au moins 6 caractères')
            else:
                user.set_password(new_password1)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Mot de passe modifié avec succès')
            return redirect('mon_profil')
    
    context = {
        'user': user,
        'profile': profile,
    }
    return render(request, 'app1/mon_profil.html', context)


# ==================== CLIENT ENVOIE MESSAGE AU GESTIONNAIRE ====================
@login_required
def client_envoyer_message(request, id):
    reservation = get_object_or_404(Reservation, id=id, user=request.user)
    
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            MessageManager.objects.create(
                reservation=reservation,
                expediteur='client',
                message=message,
                lu=False
            )
            messages.success(request, 'Message envoyé au gestionnaire')
    
    return redirect('mes_reservations')