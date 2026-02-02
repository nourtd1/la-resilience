from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrateur'
        RECEPTIONIST = 'RECEPTIONIST', 'Réceptionniste'
        ACCOUNTANT = 'ACCOUNTANT', 'Comptable'
        MANAGER = 'MANAGER', 'Direction'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.RECEPTIONIST,
        verbose_name="Rôle"
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Numéro de téléphone"
    )
    profile_photo = models.ImageField(
        upload_to='users/',
        blank=True,
        null=True,
        verbose_name="Photo de profil"
    )

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"


class Room(models.Model):
    class Category(models.TextChoices):
        SIMPLE = 'SIMPLE', 'Simple'
        DOUBLE = 'DOUBLE', 'Double'
        SUITE = 'SUITE', 'Suite'

    class Status(models.TextChoices):
        LIBRE = 'LIBRE', 'Libre'
        OCCUPEE = 'OCCUPEE', 'Occupée'
        RESERVEE = 'RESERVEE', 'Réservée'
        MAINTENANCE = 'MAINTENANCE', 'Maintenance'

    number = models.CharField(max_length=10, unique=True, verbose_name="Numéro de chambre")
    category = models.CharField(max_length=10, choices=Category.choices, verbose_name="Catégorie")
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix par nuit")
    capacity = models.IntegerField(verbose_name="Capacité")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.LIBRE, verbose_name="Statut")
    image = models.ImageField(upload_to='rooms/', blank=True, null=True, verbose_name="Photo")

    class Meta:
        ordering = ['number']
        verbose_name = "Chambre"
        verbose_name_plural = "Chambres"

    def __str__(self):
        return f"Chambre {self.number} ({self.get_category_display()})"


class Client(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, verbose_name="Nom")
    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(max_length=20, db_index=True, verbose_name="Téléphone")
    id_document = models.CharField(max_length=50, verbose_name="Pièce d'identité")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Reservation(models.Model):
    class Status(models.TextChoices):
        EN_ATTENTE = 'EN_ATTENTE', 'En attente'
        CONFIRMEE = 'CONFIRMEE', 'Confirmée'
        ANNULEE = 'ANNULEE', 'Annulée'
        TERMINEE = 'TERMINEE', 'Terminée'

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='reservations', verbose_name="Client")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reservations', verbose_name="Chambre")
    check_in = models.DateField(verbose_name="Date d'arrivée")
    check_out = models.DateField(verbose_name="Date de départ")
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.EN_ATTENTE, 
        verbose_name="Statut"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    class Meta:
        verbose_name = "Réservation"
        verbose_name_plural = "Réservations"
        ordering = ['-created_at']

    def clean(self):
        # 1. Validation des dates
        if self.check_in and self.check_out and self.check_in >= self.check_out:
            raise ValidationError({
                'check_out': "La date de départ doit être postérieure à la date d'arrivée."
            })

        # 2. Vérification des chevauchements (Overbooking)
        # On cherche s'il existe une réservation pour la même chambre
        # qui chevauche la période demandée.
        # Logique de chevauchement : (DebutA < FinB) et (FinA > DebutB)
        overlapping_reservations = Reservation.objects.filter(
            room=self.room,
            check_in__lt=self.check_out,  # La résa existante commence avant que la nouvelle finisse
            check_out__gt=self.check_in   # La résa existante finit après que la nouvelle commence
        ).exclude(
            status=self.Status.ANNULEE # On ignore les réservations annulées
        )

        # Si on modifie une réservation existante, on doit l'exclure de la vérification (elle ne se chevauche pas elle-même)
        if self.pk:
            overlapping_reservations = overlapping_reservations.exclude(pk=self.pk)

        if overlapping_reservations.exists():
            raise ValidationError(
                "Cette chambre est déjà réservée pour tout ou partie de cette période."
            )

    def save(self, *args, **kwargs):
        self.clean() # Appeler clean avant de sauvegarder pour forcer la validation même hors formulaires admin
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Réservation {self.id} - {self.client} ({self.room.number})"


class Invoice(models.Model):
    class Status(models.TextChoices):
        PAYEE = 'PAYEE', 'Payée'
        IMPAYEE = 'IMPAYEE', 'Impayée'
        PARTIELLE = 'PARTIELLE', 'Partielle'

    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name='invoice', verbose_name="Réservation")
    issued_at = models.DateTimeField(auto_now_add=True, verbose_name="Émise le")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant total", blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IMPAYEE, verbose_name="Statut")

    class Meta:
        verbose_name = "Facture"
        verbose_name_plural = "Factures"

    def save(self, *args, **kwargs):
        if not self.total_amount and self.reservation:
            # Calcul automatique du montant
            days = (self.reservation.check_out - self.reservation.check_in).days
            # Assurer au moins 1 nuit si même jour
            if days <= 0: 
                days = 1
            self.total_amount = days * self.reservation.room.price_per_night
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Facture #{self.id} - {self.reservation.client}"


class Payment(models.Model):
    class Method(models.TextChoices):
        ESPECES = 'ESPECES', 'Espèces'
        CARTE = 'CARTE', 'Carte bancaire'
        MOBILE_MONEY = 'MOBILE_MONEY', 'Mobile Money'

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments', verbose_name="Facture")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant")
    payment_method = models.CharField(max_length=20, choices=Method.choices, verbose_name="Mode de paiement")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Date de paiement")

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"

    def __str__(self):
        return f"Paiement {self.id} - {self.amount}€ ({self.get_payment_method_display()})"
