from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
from .models import Room, Client, Reservation, Invoice

class HotelSystemTest(TestCase):
    def setUp(self):
        # Création des données de base pour les tests
        self.room = Room.objects.create(
            number="101", 
            category=Room.Category.SIMPLE, 
            price_per_night=50000, 
            capacity=2
        )
        self.hotel_client = Client.objects.create(
            first_name="Test", 
            last_name="User", 
            email="test@example.com",
            phone="00000000", 
            id_document="CNI-TEST"
        )
        self.today = timezone.localdate()

    def test_reservation_creation_generates_invoice(self):
        """Test: Une facture est créée automatiquement avec la réservation."""
        reservation = Reservation.objects.create(
            client=self.hotel_client,
            room=self.room,
            check_in=self.today,
            check_out=self.today + timedelta(days=2),
            status=Reservation.Status.CONFIRMEE
        )
        # Vérifie qu'une facture existe pour cette réservation
        self.assertTrue(Invoice.objects.filter(reservation=reservation).exists())
        
        # Vérifie le calcul du montant (2 nuits * 50000 = 100000)
        invoice = Invoice.objects.get(reservation=reservation)
        self.assertEqual(invoice.total_amount, 100000)

    def test_prevent_overbooking(self):
        """Test: Empêcher le surbooking."""
        # Réservation 1 : Du jour J au J+2
        Reservation.objects.create(
            client=self.hotel_client,
            room=self.room,
            check_in=self.today,
            check_out=self.today + timedelta(days=2),
            status=Reservation.Status.CONFIRMEE
        )

        # Tentative de Réservation 2 : Chevauchement (J+1 à J+3)
        res_conflict = Reservation(
            client=self.hotel_client,
            room=self.room,
            check_in=self.today + timedelta(days=1),
            check_out=self.today + timedelta(days=3),
            status=Reservation.Status.CONFIRMEE
        )

        with self.assertRaises(ValidationError):
            res_conflict.clean() # Doit lever une erreur

    def test_room_status_automation(self):
        """Test: La chambre passe à 'OCCUPEE' si une réservation commence aujourd'hui."""
        # Au début, la chambre est LIBRE
        self.assertEqual(self.room.status, Room.Status.LIBRE)

        # On crée une réservation active aujourd'hui
        res = Reservation.objects.create(
            client=self.hotel_client,
            room=self.room,
            check_in=self.today,
            check_out=self.today + timedelta(days=1),
            status=Reservation.Status.CONFIRMEE
        )
        
        # On rafraîchit l'objet depuis la BDD (car modifié par le signal)
        self.room.refresh_from_db()
        self.assertEqual(self.room.status, Room.Status.OCCUPEE)

        # On supprime la réservation
        res.delete()
        self.room.refresh_from_db()
        self.assertEqual(self.room.status, Room.Status.LIBRE)

    def test_dashboard_access(self):
        """Test: Le dashboard s'affiche correctement."""
        # Ici self.client est bien le client de test Django
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
