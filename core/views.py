from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Sum, Q
from django.utils import timezone
from .models import Room, Reservation, Payment, Client
from datetime import timedelta
from django.db.models.functions import TruncMonth
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import ReservationForm, UserRegistrationForm
from django.contrib import messages

def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def register_view(request):
    """Vue pour l'inscription d'un nouveau compte utilisateur."""
    # Si l'utilisateur est déjà connecté, on lui permet quand même de créer un compte
    # (par exemple pour créer un compte pour un collègue)
    # Mais on affiche un message informatif
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Compte créé avec succès ! Bienvenue {user.first_name} {user.last_name}.')
            # Connecter automatiquement l'utilisateur après inscription seulement s'il n'est pas déjà connecté
            if not request.user.is_authenticated:
                login(request, user)
                return redirect('dashboard')
            else:
                # Si déjà connecté, on reste sur la page avec un message
                messages.info(request, f'Le compte pour {user.email} a été créé. Vous pouvez vous déconnecter et vous connecter avec ce nouveau compte.')
                form = UserRegistrationForm()  # Réinitialiser le formulaire
    else:
        form = UserRegistrationForm()
    
    return render(request, 'core/register.html', {
        'form': form,
        'is_authenticated': request.user.is_authenticated
    })

@login_required
def dashboard_view(request):
    today = timezone.localdate()
    start_of_month = today.replace(day=1)

    # 1. Taux d'occupation
    total_rooms = Room.objects.count()
    occupied_rooms = Room.objects.filter(status=Room.Status.OCCUPEE).count()
    occupation_rate = 0
    if total_rooms > 0:
        occupation_rate = round((occupied_rooms / total_rooms) * 100, 1)

    # 2. Revenu du mois
    monthly_revenue = Payment.objects.filter(
        date__gte=start_of_month
    ).aggregate(total=Sum('amount'))['total'] or 0

    # 3. Réservations à venir (Check-in futur ou aujourd'hui)
    upcoming_reservations = Reservation.objects.filter(
        check_in__gte=today,
        status__in=[Reservation.Status.CONFIRMEE, Reservation.Status.EN_ATTENTE]
    ).count()

    # 4. Total Clients
    total_clients = Client.objects.count()

    # 5. Répartition par catégorie (pour Chart.js)
    cat_stats = Reservation.objects.values('room__category').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Labels en français via le modèle
    cat_labels = [dict(Room.Category.choices).get(item['room__category']) for item in cat_stats]
    cat_data = [item['count'] for item in cat_stats]

    # 6. Tendance des Revenus (Derniers 6 mois)
    last_6_months = today - timedelta(days=180)
    revenue_trend = Payment.objects.filter(date__gte=last_6_months).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')

    rev_labels = [item['month'].strftime('%B') for item in revenue_trend]
    rev_data = [float(item['total']) for item in revenue_trend] # Decimal as float for JSON

    # 7. Dernières Réservations
    recent_reservations = Reservation.objects.select_related('client', 'room').order_by('-created_at')[:5]

    # 8. Statut des Chambres (Distribution)
    room_status_counts = Room.objects.values('status').annotate(count=Count('id'))
    room_status_dict = {item['status']: item['count'] for item in room_status_counts}

    context = {
        'occupation_rate': occupation_rate,
        'occupied_rooms': occupied_rooms,
        'total_rooms': total_rooms,
        'monthly_revenue': monthly_revenue,
        'upcoming_reservations': upcoming_reservations,
        'total_clients': total_clients,
        
        # Charts Data - Passed as simple lists, template will interpret
        'cat_labels': cat_labels,
        'cat_data': cat_data,
        'rev_labels': rev_labels,
        'rev_data': rev_data,
        
        # Tables & Grids
        'recent_reservations': recent_reservations,
        'room_status': room_status_dict,
    }
    return render(request, 'core/dashboard.html', context)

# --- VUES RECEPTION ---

@login_required
def reception_rooms_view(request):
    """Vue liste des chambres pour la réception."""
    status_filter = request.GET.get('status')
    category_filter = request.GET.get('category')
    
    rooms = Room.objects.all().order_by('number')
    
    if status_filter:
        rooms = rooms.filter(status=status_filter)
    if category_filter:
        rooms = rooms.filter(category=category_filter)
        
    context = {
        'rooms': rooms,
        'room_statuses': Room.Status,
        'room_categories': Room.Category,
        'current_status': status_filter,
        'current_category': category_filter,
    }
    return render(request, 'core/reception_rooms.html', context)

@login_required
def reception_reservations_view(request):
    """Vue liste des réservations pour la réception."""
    status_filter = request.GET.get('status')
    today = timezone.now().date()
    
    # Réservations à partir d'aujourd'hui, ou en cours (overlap today)
    # On prend toutes celles qui finissent après ou égale à aujourd'hui
    reservations = Reservation.objects.select_related('client', 'room').filter(
        check_out__gte=today
    ).order_by('check_in')

    if status_filter:
        reservations = reservations.filter(status=status_filter)

    context = {
        'reservations': reservations,
        'reservation_statuses': Reservation.Status,
        'current_status': status_filter,
    }
    return render(request, 'core/reception_reservations.html', context)

@login_required
def reception_reservation_create_view(request):
    """Création d'une nouvelle réservation."""
    room_id = request.GET.get('room')
    initial_data = {}
    if room_id:
        try:
            room = Room.objects.get(id=room_id)
            initial_data['room'] = room
        except Room.DoesNotExist:
            pass
            
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            try:
                reservation = form.save()
                messages.success(request, f"Réservation créée avec succès pour {reservation.client} !")
                return redirect('reception_reservations')
            except Exception as e:
                # Normalement clean() du model lève ValidationError qui est attrapé par form.is_valid()
                # Mais au cas où d'autres erreurs surviennent
                messages.error(request, f"Erreur lors de la création : {str(e)}")
    else:
        form = ReservationForm(initial=initial_data)

    return render(request, 'core/reception_reservation_form.html', {
        'form': form,
        'is_new': True
    })

@login_required
def reception_reservation_update_status(request, pk, new_status):
    """Action rapide pour changer le statut d'une réservation."""
    reservation = get_object_or_404(Reservation, pk=pk)
    
    if new_status in Reservation.Status.values:
        reservation.status = new_status
        reservation.save()
        messages.success(request, f"Statut mis à jour : {reservation.get_status_display()}")
    
    return redirect('reception_reservations')
