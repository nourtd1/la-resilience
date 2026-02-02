from django.contrib.auth.forms import UserChangeForm, ReadOnlyPasswordHashWidget
from django import forms
from .models import User


class CustomUserChangeForm(UserChangeForm):
    """Formulaire personnalisé pour l'édition d'utilisateur dans l'admin."""
    
    password = forms.CharField(
        label="Mot de passe",
        help_text=(
            "Les mots de passe bruts ne sont pas stockés, il n'y a donc aucun moyen "
            "de voir le mot de passe de cet utilisateur. Vous pouvez le "
            "modifier en utilisant <a href=\"../password/\">ce formulaire</a>."
        ),
        widget=ReadOnlyPasswordHashWidget,
        required=False,
    )
    
    username = forms.CharField(
        label="Nom d'utilisateur",
        help_text="150 caractères max. Lettres, chiffres et @/./+/-/_ uniquement.",
        max_length=150,
    )
    
    class Meta:
        model = User
        fields = '__all__'
