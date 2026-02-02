from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.db.models import Sum
from .models import User, Room, Client, Reservation, Invoice, Payment
from .admin_forms import CustomUserChangeForm

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser')
    readonly_fields = ('profile_header',)

    fieldsets = (
        ('Vue d\'ensemble', {'fields': ('profile_header',)}),
        ('Compte', {'fields': ('username', 'password')}),
        ('Informations Personnelles & Professionnelles', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'profile_photo', 'role')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
        ('Dates Importantes', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',),
        }),
    )

    def profile_header(self, obj):
        if not obj.pk:
            return "Le profil sera généré après l'enregistrement."

        avatar_url = obj.profile_photo.url if obj.profile_photo else "https://ui-avatars.com/api/?name=" + (obj.username or "") + "&background=1a2a6c&color=fff"
        
        status_color = "#2ecc71" if obj.is_active else "#95a5a6"
        status_text = "Actif" if obj.is_active else "Inactif"
        role_label = obj.get_role_display() or "Non défini"
        perm_count = obj.groups.count() + obj.user_permissions.count()
        last_login = obj.last_login.strftime("%d %b %Y") if obj.last_login else "-"
        date_joined = obj.date_joined.strftime("%Y")
        pwd_url = f"/admin/core/user/{obj.pk}/password/"
        
        return format_html(
            """
            <style>
                @keyframes pulse-ring {
                    0% { box-shadow: 0 0 0 0 rgba(46, 204, 113, 0.7); }
                    70% { box-shadow: 0 0 0 10px rgba(46, 204, 113, 0); }
                    100% { box-shadow: 0 0 0 0 rgba(46, 204, 113, 0); }
                }
                .pro-card-container {
                    display: grid;
                    grid-template-columns: 260px 1fr;
                    background: #fff;
                    border-radius: 16px;
                    overflow: hidden;
                    box-shadow: 0 15px 35px rgba(0,0,0,0.1);
                    margin-bottom: 40px;
                    font-family: 'Segoe UI', system-ui, sans-serif;
                    border: 1px solid rgba(0,0,0,0.05);
                }
                .pro-card-sidebar {
                    background: linear-gradient(135deg, #1a2a6c 0%, #b21f1f 100%);
                    padding: 40px 20px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    text-align: center;
                    color: white;
                    position: relative;
                }
                .pro-avatar {
                    width: 120px;
                    height: 120px;
                    border-radius: 50%;
                    border: 4px solid rgba(255,255,255,0.25);
                    box-shadow: 0 8px 20px rgba(0,0,0,0.2);
                    margin-bottom: 20px;
                    object-fit: cover;
                    background: #fff;
                }
                .status-badge {
                    background: rgba(0,0,0,0.2);
                    padding: 6px 15px;
                    border-radius: 20px;
                    font-size: 0.85rem;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    backdrop-filter: blur(5px);
                    border: 1px solid rgba(255,255,255,0.1);
                }
                .status-dot {
                    width: 8px;
                    height: 8px;
                    background: %s;
                    border-radius: 50%;
                    %s
                }
                .pro-card-content {
                    padding: 35px 40px;
                    display: flex;
                    flex-direction: column;
                    background: linear-gradient(to right, #ffffff, #f9fbfd);
                }
                .pro-header h1 {
                    margin: 0;
                    font-size: 2rem;
                    color: #2c3e50;
                    font-weight: 700;
                    letter-spacing: -0.5px;
                }
                .pro-header small {
                    color: #95a5a6;
                    font-weight: 400;
                    font-size: 1.1rem;
                    margin-left: 10px;
                }
                .pro-stats-grid {
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 25px;
                    margin: 35px 0;
                }
                .stat-item {
                    background: #fff;
                    padding: 15px 20px;
                    border-radius: 12px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.03);
                    border-bottom: 3px solid transparent;
                    transition: transform 0.2s;
                }
                .stat-item:hover {
                    transform: translateY(-2px);
                }
                .stat-value {
                    font-size: 1.4rem;
                    font-weight: 800;
                    color: #2c3e50;
                    display: block;
                    margin-bottom: 4px;
                }
                .stat-label {
                    font-size: 0.75rem;
                    color: #7f8c8d;
                    text-transform: uppercase;
                    letter-spacing: 0.8px;
                    font-weight: 600;
                }
                .action-btn {
                    display: inline-flex;
                    align-items: center;
                    padding: 12px 25px;
                    background: linear-gradient(90deg, #1a2a6c, #2a4a8c);
                    color: white !important;
                    text-decoration: none;
                    border-radius: 8px;
                    font-size: 0.95rem;
                    font-weight: 600;
                    box-shadow: 0 4px 12px rgba(26, 42, 108, 0.3);
                    transition: all 0.2s;
                }
                .action-btn:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 6px 15px rgba(26, 42, 108, 0.4);
                }
            </style>
            
            <div class="pro-card-container">
                <div class="pro-card-sidebar">
                    <img src="%s" class="pro-avatar">
                    <div style="font-weight:700; font-size:1.2rem; margin-bottom:5px; text-shadow: 0 2px 4px rgba(0,0,0,0.1);">%s</div>
                    <div style="font-size:0.9rem; opacity:0.9; margin-bottom:20px; font-weight:300;">%s</div>
                    <div class="status-badge">
                        <div class="status-dot"></div>
                        %s
                    </div>
                </div>
                
                <div class="pro-card-content">
                    <div class="pro-header">
                        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                            <div>
                                <h1>%s <small>%s</small></h1>
                                <div style="color:#7f8c8d; margin-top:8px; display:flex; align-items:center; gap:8px;">
                                    <i class="fas fa-envelope" style="color:#1a2a6c;"></i> %s
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="pro-stats-grid">
                        <div class="stat-item" style="border-bottom-color: #e67e22;">
                            <span class="stat-value">%s</span>
                            <span class="stat-label">Dernier Accès</span>
                        </div>
                        <div class="stat-item" style="border-bottom-color: #2ecc71;">
                            <span class="stat-value">%s</span>
                            <span class="stat-label">Permissions</span>
                        </div>
                        <div class="stat-item" style="border-bottom-color: #3498db;">
                            <span class="stat-value">%s</span>
                            <span class="stat-label">Niveau</span>
                        </div>
                    </div>
                    
                    <div style="text-align:right; border-top: 1px solid #f0f2f5; padding-top: 25px;">
                         <a href="%s" class="action-btn">
                            <i class="fas fa-key me-2"></i> Changer le mot de passe
                        </a>
                    </div>
                </div>
            </div>
            """ % (
                status_color,
                "animation: pulse-ring 2s infinite;" if obj.is_active else "",
                avatar_url,
                obj.username,
                role_label,
                status_text,
                f"{obj.first_name} {obj.last_name}".strip() or "Utilisateur",
                f"Membre depuis {date_joined}",
                obj.email or "Non renseigné",
                last_login,
                perm_count,
                "Superutilisateur" if obj.is_superuser else ("Staff" if obj.is_staff else "Utilisateur"),
                pwd_url
            )
        )
    profile_header.short_description = "Fiche Signalétique"
    profile_header.allow_tags = True

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'created_at')
    search_fields = ('first_name', 'last_name', 'email')
    
    fieldsets = (
        ('Identité', {
            'fields': ('first_name', 'last_name', 'id_document')
        }),
        ('Contact', {
            'fields': ('email', 'phone')
        }),
    )

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('number', 'category', 'price_per_night', 'capacity', 'status')
    list_filter = ('category', 'status', 'capacity')
    search_fields = ('number',)
    # list_editable = ('status',)
    
    fieldsets = (
        ('Détails', {
            'fields': ('number', 'category', 'capacity', 'image')
        }),
        ('État & Prix', {
            'fields': ('status', 'price_per_night')
        }),
    )
    
    def status_colored(self, obj):
        colors = {
            'LIBRE': 'green',
            'OCCUPEE': 'red',
            'RESERVEE': 'orange',
            'MAINTENANCE': 'gray',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_colored.short_description = 'Statut'

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'room', 'check_in', 'check_out', 'status', 'created_at')
    list_filter = ('status', 'check_in', 'room__category')
    search_fields = ('client__last_name', 'client__first_name', 'room__number')
    date_hierarchy = 'check_in'
    
    fieldsets = (
        ('Séjour', {
            'fields': ('client', 'room', 'check_in', 'check_out')
        }),
        ('Suivi', {
            'fields': ('status',)
        })
    )

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    can_delete = False
    
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'reservation', 'issued_at', 'total_amount', 'status')
    list_filter = ('status', 'issued_at')
    inlines = [PaymentInline]
    readonly_fields = ('total_amount', 'issued_at')
    
    fieldsets = (
        ('Détails', {
            'fields': ('reservation', 'issued_at', 'status')
        }),
        ('Finances', {
            'fields': ('total_amount',)
        }),
    )

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'amount', 'payment_method', 'date')
    list_filter = ('payment_method', 'date')
