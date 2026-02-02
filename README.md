# 🏨 Hôtel La Résilience - Système de Gestion Hôtelière

Un système de gestion hôtelière moderne et complet développé avec Django, offrant une interface premium pour gérer les réservations, clients, chambres, factures et paiements.

## ✨ Fonctionnalités

### 🔐 Authentification & Gestion des Utilisateurs
- ✅ Système de connexion/inscription sécurisé
- ✅ Gestion des rôles : Administrateur, Réceptionniste, Comptable, Direction
- ✅ Interface d'administration Django personnalisée en français
- ✅ Profils utilisateur avec avatars

### 📊 Dashboard Premium
- ✅ Indicateurs clés de performance (KPIs)
- ✅ Graphiques interactifs (Chart.js)
- ✅ Vue en temps réel du parc hôtelier
- ✅ Suivi des revenus et réservations
- ✅ Design moderne avec glassmorphism

### 🛏️ Gestion des Chambres
- ✅ Catégories : Simple, Double, Suite
- ✅ Statuts : Libre, Occupée, Réservée, Maintenance
- ✅ Vue rack interactive avec filtres
- ✅ Gestion des tarifs et capacités

### 📅 Réservations
- ✅ Création et modification de réservations
- ✅ Détection automatique des conflits (overbooking)
- ✅ Gestion des statuts : En attente, Confirmée, Annulée, Terminée
- ✅ Vue calendrier des arrivées/départs

### 💰 Facturation & Paiements
- ✅ Génération automatique des factures
- ✅ Calcul automatique du montant total
- ✅ Gestion des paiements (Espèces, Carte, Mobile Money)
- ✅ Suivi des paiements partiels

### 👥 Gestion des Clients
- ✅ Base de données clients complète
- ✅ Recherche et filtrage avancés
- ✅ Historique des réservations

## 🚀 Installation & Déploiement

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Git

### 1️⃣ Cloner le projet

```bash
git clone https://github.com/nourtd1/la-resilience.git
cd la-resilience
```

### 2️⃣ Créer un environnement virtuel

**Windows :**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac :**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4️⃣ Configurer la base de données

```bash
python manage.py migrate
```

### 5️⃣ Créer un superutilisateur

```bash
python manage.py createsuperuser
```

Suivez les instructions pour créer votre compte administrateur.

### 6️⃣ Charger les données de test (optionnel)

```bash
python manage.py populate_db
```

Cette commande crée :
- 10 chambres avec différentes catégories
- 15 clients
- 20 réservations
- Factures et paiements associés

### 7️⃣ Lancer le serveur de développement

```bash
python manage.py runserver
```

Accédez à l'application sur **http://127.0.0.1:8000**

## 🔗 URLs Principales

- **Page d'accueil** : `http://127.0.0.1:8000/`
- **Connexion** : `http://127.0.0.1:8000/login/`
- **Inscription** : `http://127.0.0.1:8000/register/`
- **Dashboard** : `http://127.0.0.1:8000/dashboard/`
- **Administration** : `http://127.0.0.1:8000/admin/`
- **Gestion Chambres** : `http://127.0.0.1:8000/reception/rooms/`
- **Réservations** : `http://127.0.0.1:8000/reception/reservations/`

## 👤 Comptes par Défaut (après populate_db)

**Administrateur :**
- Email : `admin@resilience.com`
- Mot de passe : `admin123`

**Réceptionniste :**
- Email : `receptionniste@resilience.com`
- Mot de passe : `receptionniste123`

## 🎨 Technologies Utilisées

- **Backend** : Django 6.0
- **Frontend** : Bootstrap 5, Chart.js, Font Awesome
- **Base de données** : SQLite (développement) / PostgreSQL (production recommandée)
- **Admin Interface** : Django Jazzmin
- **Design** : Glassmorphism, animations CSS

## 📁 Structure du Projet

```
hotel_resilience/
├── core/                          # Application principale
│   ├── models.py                  # Modèles de données
│   ├── views.py                   # Vues et contrôleurs
│   ├── forms.py                   # Formulaires
│   ├── admin.py                   # Configuration admin
│   ├── urls.py                    # Routes URL
│   └── management/
│       └── commands/
│           └── populate_db.py     # Script de peuplement
├── templates/                     # Templates HTML
│   ├── admin/                     # Templates admin personnalisés
│   ├── core/                      # Templates de l'application
│   └── base.html                  # Template de base
├── static/                        # Fichiers statiques
│   └── css/
│       └── style.css              # Styles personnalisés
├── hotel_resilience/              # Configuration Django
│   ├── settings.py                # Paramètres
│   ├── urls.py                    # URLs principales
│   └── wsgi.py                    # WSGI config
└── manage.py                      # Script de gestion Django
```

## 🔧 Configuration Production

### Variables d'environnement recommandées

Créez un fichier `.env` :

```env
SECRET_KEY=votre-clé-secrète-très-longue-et-aléatoire
DEBUG=False
ALLOWED_HOSTS=votredomaine.com,www.votredomaine.com
DATABASE_URL=postgres://user:password@localhost/dbname

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.exemple.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=user@exemple.com
EMAIL_HOST_PASSWORD=mot-de-passe-securise
```

### Déploiement sur des plateformes cloud

**Heroku, Railway, Render, etc.** :
1. Ajoutez un fichier `Procfile`
2. Configurez les variables d'environnement
3. Collectez les fichiers statiques : `python manage.py collectstatic`
4. Migrez la base de données : `python manage.py migrate`

## 🛡️ Sécurité

- ✅ Authentification Django sécurisée
- ✅ Protection CSRF activée
- ✅ Validation des données côté serveur
- ✅ Mots de passe hashés (PBKDF2)
- ✅ Permissions basées sur les rôles

## 📝 Licence

Ce projet est propriétaire et destiné à l'usage exclusif de l'Hôtel La Résilience.

## 👨‍💻 Support & Contact

Pour toute question ou assistance :
- Email : support@larésilience.com
- Documentation : Consultez le dossier `docs/` pour plus de détails

---

**Développé avec ❤️ pour l'Hôtel La Résilience**
