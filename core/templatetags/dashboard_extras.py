from django import template
from django.db.models import Sum
from core.models import Client, Room, Reservation, Invoice

register = template.Library()

@register.simple_tag
def get_dashboard_stats():
    # Clients
    total_clients = Client.objects.count()
    
    # Rooms
    rooms_total = Room.objects.count()
    # Assuming 'LIBRE' is the code for free rooms based on models.py
    rooms_available = Room.objects.filter(status='LIBRE').count()
    occupancy_rate = 0
    if rooms_total > 0:
        occupancy_rate = int(((rooms_total - rooms_available) / rooms_total) * 100)
    
    # Reservations
    reservations_pending = Reservation.objects.filter(status='EN_ATTENTE').count()
    reservations_confirmed = Reservation.objects.filter(status='CONFIRMEE').count()
    
    # Revenue (Paid invoices)
    revenue_data = Invoice.objects.filter(status='PAYEE').aggregate(total=Sum('total_amount'))
    revenue = revenue_data['total'] if revenue_data['total'] else 0
    
    return {
        'total_clients': total_clients,
        'rooms_total': rooms_total,
        'rooms_available': rooms_available,
        'occupancy_rate': occupancy_rate,
        'reservations_pending': reservations_pending,
        'reservations_confirmed': reservations_confirmed,
        'revenue': revenue,
    }
