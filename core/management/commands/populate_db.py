import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from django.core.exceptions import ValidationError
from core.models import User, Room, Client, Reservation, Invoice, Payment

class Command(BaseCommand):
    help = 'Peuple la base de données avec des données de test réalistes.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Début du peuplement de la base de données...'))
        fake = Faker('fr_FR')  # Utilisation d'une locale française pour commencer

        # --- 1. Création des Utilisateurs ---
        self.stdout.write("Création des utilisateurs...")
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@hotel.com', 'adminpass', role=User.Role.ADMIN)
        
        if not User.objects.filter(username='reception').exists():
            User.objects.create_user('reception', 'reception@hotel.com', 'userpass', role=User.Role.RECEPTIONIST)

        # --- 2. Création des Chambres ---
        self.stdout.write("Création des chambres...")
        # Suppression des chambres existantes pour éviter les doublons lors de tests multiples
        if Room.objects.count() == 0:
            categories = [
                (Room.Category.SIMPLE, 5, 25000, 1), # 25000 FCFA env
                (Room.Category.DOUBLE, 5, 45000, 2),
                (Room.Category.SUITE, 5, 85000, 4),
            ]
            
            room_counter = 100
            for cat, count, price, capacity in categories:
                for _ in range(count):
                    room_number = str(room_counter)
                    Room.objects.create(
                        number=room_number,
                        category=cat,
                        price_per_night=price,
                        capacity=capacity,
                        status=Room.Status.LIBRE
                    )
                    room_counter += 1
        else:
            self.stdout.write("Chambres déjà existantes, saut de cette étape.")

        # --- 3. Création des Clients ---
        self.stdout.write("Création des clients...")
        # Liste de noms/prénoms à consonance tchadienne/africaine
        first_names = ['Mahamat', 'Fatime', 'Zara', 'Moussa', 'Abdoulaye', 'Amina', 'Kaltouma', 'Ousmane', 'Yaya', 'Achta', 'Brahim', 'Halime', 'Idriss', 'Mariam', 'Souleymane']
        last_names = ['Daoud', 'Hassan', 'Abakar', 'Mahamat', 'Saleh', 'Ibrahim', 'Adam', 'Moussa', 'Abdellah', 'Youssouf', 'Djarma', 'Koulamallah', 'Ngarlejy']

        clients = []
        for _ in range(50):
            first = random.choice(first_names)
            last = random.choice(last_names)
            # Ajout d'un suffixe aléatoire à l'email pour garantir l'unicité
            email = f"{first.lower()}.{last.lower()}.{random.randint(1000, 9999)}@example.com"
            
            client = Client.objects.create(
                first_name=first,
                last_name=last,
                email=email,
                phone=fake.phone_number(),
                id_document=f"CNI-{random.randint(10000000, 99999999)}"
            )
            clients.append(client)

        # --- 4. Génération des Réservations ---
        self.stdout.write("Génération des réservations...")
        rooms = list(Room.objects.all())
        
        # Helper pour créer une résa safe
        def create_reservation(status_type, check_in_date, duration_days):
            attempts = 0
            while attempts < 50:
                attempts += 1
                room = random.choice(rooms)
                client = random.choice(clients)
                check_out_date = check_in_date + timedelta(days=duration_days)

                res = Reservation(
                    client=client,
                    room=room,
                    check_in=check_in_date,
                    check_out=check_out_date,
                    status=status_type
                )
                try:
                    res.clean() # Vérifie les conflits
                    res.save()
                    return res
                except ValidationError:
                    continue # On réessaie avec une autre chambre ou données
            return None

        today = timezone.localdate()

        # 10 Passées
        for _ in range(10):
            days_ago = random.randint(30, 60)
            duration = random.randint(1, 5)
            start = today - timedelta(days=days_ago) # Il y a 1-2 mois
            create_reservation(Reservation.Status.TERMINEE, start, duration)

        # 10 En cours (Check-in avant ou aujourd'hui, Check-out futur)
        for _ in range(10):
            # Pour être sûr que c'est "en cours", start <= today et end > today
            start_offset = random.randint(0, 5) 
            start = today - timedelta(days=start_offset)
            duration = random.randint(start_offset + 1, 10) # Assure que la fin est dans le futur
            create_reservation(Reservation.Status.CONFIRMEE, start, duration)

        # 10 Futures
        for _ in range(10):
            days_ahead = random.randint(1, 30)
            duration = random.randint(1, 7)
            start = today + timedelta(days=days_ahead)
            create_reservation(Reservation.Status.CONFIRMEE, start, duration)

        # --- 5. Factures et Paiements ---
        self.stdout.write("Génération des factures et paiements...")
        reservations = Reservation.objects.all()
        for res in reservations:
            # Créer la facture
            invoice, created = Invoice.objects.get_or_create(reservation=res)
            invoice.save() # Pour calculer le montant
            
            # Payer si Terminée ou En cours (aléatoire)
            if res.status == Reservation.Status.TERMINEE or (res.status == Reservation.Status.CONFIRMEE and random.choice([True, False])):
                Payment.objects.create(
                    invoice=invoice,
                    amount=invoice.total_amount,
                    payment_method=random.choice(Payment.Method.choices)[0]
                )
                invoice.status = Invoice.Status.PAYEE
                invoice.save()

        self.stdout.write(self.style.SUCCESS("Peuplement terminé avec succès !"))
