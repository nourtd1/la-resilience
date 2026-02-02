from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import Reservation, Room, Invoice

@receiver(post_save, sender=Reservation)
def create_invoice(sender, instance, created, **kwargs):
    """
    Génère automatiquement une facture lors de la création d'une réservation.
    """
    if created:
        Invoice.objects.get_or_create(reservation=instance)

@receiver(post_save, sender=Reservation)
@receiver(post_delete, sender=Reservation)
def update_room_status(sender, instance, **kwargs):
    """
    Met à jour le statut de la chambre automatiquement selon les réservations.
    """
    room = instance.room
    today = timezone.localdate()

    # On cherche s'il existe une réservation active pour cette chambre aujourd'hui
    # Active = Statut 'CONFIRMEE' et la date actuelle est incluse dans la période [check_in, check_out[
    active_reservation_exists = Reservation.objects.filter(
        room=room,
        status=Reservation.Status.CONFIRMEE,
        check_in__lte=today,
        check_out__gt=today
    ).exists()

    # Si la chambre est actuellement en MAINTENANCE, on ne touche pas à son statut via les réservations
    if room.status == Room.Status.MAINTENANCE:
        return

    # Mise à jour du statut
    if active_reservation_exists:
        if room.status != Room.Status.OCCUPEE:
            room.status = Room.Status.OCCUPEE
            room.save(update_fields=['status'])
    else:
        # Si aucune réservation active n'est trouvée et qu'elle était marquée occupée, on la libère.
        # Note: On pourrait raffiner pour 'RESERVEE' si check_in > today, mais le prompt demande 'LIBRE'.
        if room.status == Room.Status.OCCUPEE:
            room.status = Room.Status.LIBRE
            room.save(update_fields=['status'])
