from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Vetement,Reservation,Service,Paiement


class InscriptionForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ConnexionForm(AuthenticationForm):
    username = forms.CharField(label="Nom d'utilisateur")
    password = forms.CharField(widget=forms.PasswordInput)

    


class VetementForm(forms.ModelForm):
    class Meta:
        model = Vetement
        fields = '__all__'

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['nom', 'description', 'prix', 'image', 'duree']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
 # FORMULAIRE RESERVATION
class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['date_service', 'heure_service', 'notes']
        widgets = {
            'date_service': forms.DateInput(attrs={'type': 'date'}),
            'heure_service': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Vos remarques...'}),
        }
class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = ['methode', 'montant']        
       