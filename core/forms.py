from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from .models import Reservation, Room, Client, User

class ReservationForm(forms.ModelForm):
    # Champ client avec widget select2-like (standard select pour MVP)
    client = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Client"
    )
    
    # Champ chambre avec filtrage possible
    room = forms.ModelChoiceField(
        queryset=Room.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Chambre"
    )

    check_in = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Date d'arrivée"
    )

    check_out = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Date de départ"
    )

    class Meta:
        model = Reservation
        fields = ['client', 'room', 'check_in', 'check_out']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si une chambre est passée en initial, on la pré-sélectionne
        if 'initial' in kwargs and 'room' in kwargs['initial']:
            self.fields['room'].initial = kwargs['initial']['room']
        
        # Ordonner les chambres par numéro
        self.fields['room'].queryset = Room.objects.all().order_by('number')

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')

        if check_in and check_out:
            if check_in < timezone.now().date():
                self.add_error('check_in', "La date d'arrivée ne peut pas être dans le passé.")
            
            if check_in >= check_out:
                self.add_error('check_out', "La date de départ doit être postérieure à l'arrivée.")

        return cleaned_data


class UserRegistrationForm(UserCreationForm):
    """Formulaire d'inscription simplifié - utilise l'email comme identifiant."""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'votre.email@example.com',
            'autocomplete': 'email'
        }),
        label="Email",
        help_text="Votre email servira aussi d'identifiant de connexion"
    )
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre prénom',
            'autocomplete': 'given-name'
        }),
        label="Prénom"
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre nom',
            'autocomplete': 'family-name'
        }),
        label="Nom"
    )
    
    # Champ de sélection de rôle
    role = forms.ChoiceField(
        choices=User.Role.choices,
        initial=User.Role.RECEPTIONIST,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label="Rôle",
        help_text="Sélectionnez le rôle de cet utilisateur"
    )
    
    # Champ pour définir si l'utilisateur est staff (accès admin)
    is_staff = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        }),
        label="Accès administrateur",
        help_text="Cochez pour donner accès à l'interface d'administration Django"
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Minimum 8 caractères',
            'autocomplete': 'new-password'
        }),
        label="Mot de passe",
        help_text="Au moins 8 caractères"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Répétez le mot de passe',
            'autocomplete': 'new-password'
        }),
        label="Confirmer le mot de passe"
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'role', 'is_staff', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cacher le champ username - on utilisera l'email à la place
        if 'username' in self.fields:
            del self.fields['username']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Un compte avec cet email existe déjà.")
        if User.objects.filter(username=email).exists():
            raise ValidationError("Cet email est déjà utilisé comme identifiant.")
        return email

    def save(self, commit=True):
        email = self.cleaned_data['email']
        # Utiliser l'email comme username automatiquement
        user = super().save(commit=False)
        user.username = email  # Email = username
        user.email = email
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.role = self.cleaned_data['role']  # Utiliser le rôle sélectionné
        user.is_staff = self.cleaned_data.get('is_staff', False)  # Définir le statut staff
        user.is_active = True
        
        # Si le rôle est ADMIN, activer automatiquement is_staff et is_superuser
        if user.role == User.Role.ADMIN:
            user.is_staff = True
            user.is_superuser = True
        
        if commit:
            user.save()
        return user
