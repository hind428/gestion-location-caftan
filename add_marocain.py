import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'location.settings')
django.setup()

from app1.models import Vetement, Categorie

def ajouter_vetements_marocains():
    # Créer les catégories
    femme, _ = Categorie.objects.get_or_create(nom="Femme")
    homme, _ = Categorie.objects.get_or_create(nom="Homme")
    
    # Supprimer les anciens (optionnel)
    # Vetement.objects.all().delete()
    
    # Vêtements traditionnels marocains
    vetements_data = [
        # ========== FEMME ==========
        {
            'nom': 'Caftan Fassi Doré',
            'type_marocain': 'caftan',
            'genre': 'femme',
            'description': 'Superbe caftan Fassi en brocart doré, idéal pour les mariages et grandes occasions.',
            'prix_jour': 450,
            'couleur': 'Doré',
            'matiere': 'Brocart',
            'taille': 'M',
            'categorie': femme
        },
        {
            'nom': 'Takchita Marrakchia',
            'type_marocain': 'takchita',
            'genre': 'femme',
            'description': 'Takchita traditionnelle de Marrakech, broderie fine, parfaite pour les cérémonies.',
            'prix_jour': 380,
            'couleur': 'Bordeaux',
            'matiere': 'Satin',
            'taille': 'L',
            'categorie': femme
        },
        {
            'nom': 'Djellaba Fdila',
            'type_marocain': 'djellaba',
            'genre': 'femme',
            'description': 'Djellaba en laine fine, confortable et élégante pour le quotidien.',
            'prix_jour': 120,
            'couleur': 'Beige',
            'matiere': 'Laine',
            'taille': 'XL',
            'categorie': femme
        },
        {
            'nom': 'Caftan Tétouani Bleu',
            'type_marocain': 'caftan',
            'genre': 'femme',
            'description': 'Caftan Tétouani en velours bleu, broderie à la main.',
            'prix_jour': 520,
            'couleur': 'Bleu roi',
            'matiere': 'Velours',
            'taille': 'S',
            'categorie': femme
        },
        {
            'nom': 'Takchita Verte',
            'type_marocain': 'takchita',
            'genre': 'femme',
            'description': 'Takchita verte émeraude, broderie en fils dorés.',
            'prix_jour': 490,
            'couleur': 'Verte',
            'matiere': 'Satin',
            'taille': 'M',
            'categorie': femme
        },
        {
            'nom': 'Caftan Blanc',
            'type_marocain': 'caftan',
            'genre': 'femme',
            'description': 'Caftan blanc pur, idéal pour les cérémonies de mariage.',
            'prix_jour': 480,
            'couleur': 'Blanc',
            'matiere': 'Soie',
            'taille': 'L',
            'categorie': femme
        },
        
        # ========== HOMME ==========
        {
            'nom': 'Jabador Royal',
            'type_marocain': 'jabador',
            'genre': 'homme',
            'description': 'Jabador de cérémonie en soie, parfait pour les mariages.',
            'prix_jour': 250,
            'couleur': 'Blanc',
            'matiere': 'Soie',
            'taille': 'L',
            'categorie': homme
        },
        {
            'nom': 'Djellaba Homme Marocaine',
            'type_marocain': 'djellaba',
            'genre': 'homme',
            'description': 'Djellaba homme en coton, confortable et élégante.',
            'prix_jour': 100,
            'couleur': 'Gris',
            'matiere': 'Coton',
            'taille': 'XL',
            'categorie': homme
        },
        {
            'nom': 'Gandoura Cérémonie',
            'type_marocain': 'gandoura',
            'genre': 'homme',
            'description': 'Gandoura traditionnelle pour les prières et occasions religieuses.',
            'prix_jour': 80,
            'couleur': 'Blanc',
            'matiere': 'Coton',
            'taille': 'M',
            'categorie': homme
        },
        {
            'nom': 'Selham Homme',
            'type_marocain': 'selham',
            'genre': 'homme',
            'description': 'Selham en laine, manteau traditionnel marocain.',
            'prix_jour': 180,
            'couleur': 'Marron',
            'matiere': 'Laine',
            'taille': 'L',
            'categorie': homme
        },
        {
            'nom': 'Jabador Bleu',
            'type_marocain': 'jabador',
            'genre': 'homme',
            'description': 'Jabador bleu ciel en coton, parfait pour l\'été.',
            'prix_jour': 120,
            'couleur': 'Bleu',
            'matiere': 'Coton',
            'taille': 'XL',
            'categorie': homme
        },
        {
            'nom': 'Djellaba Noire',
            'type_marocain': 'djellaba',
            'genre': 'homme',
            'description': 'Djellaba noire en laine, élégante et chaude.',
            'prix_jour': 150,
            'couleur': 'Noir',
            'matiere': 'Laine',
            'taille': 'L',
            'categorie': homme
        },
    ]
    
    added_count = 0
    for data in vetements_data:
        article, created = Vetement.objects.get_or_create(
            nom=data['nom'],
            defaults=data
        )
        if created:
            added_count += 1
            print(f"✅ Ajouté: {article.nom} - {article.prix_jour} DH/jour")
        else:
            print(f"⚠️ Existe déjà: {article.nom}")
    
    print(f"\n🎉 Terminé! {added_count} nouveaux vêtements ajoutés.")
    print(f"📊 Total des vêtements dans la base: {Vetement.objects.count()}")

if __name__ == '__main__':
    ajouter_vetements_marocains()