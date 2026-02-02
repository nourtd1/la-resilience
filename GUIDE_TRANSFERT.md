# 📖 Guide de Transfert du Projet

## Pour le Développeur (Vous)

### Option 1 : Transférer la Propriété du Repository GitHub

1. **Aller sur GitHub** : https://github.com/nourtd1/la-resilience
2. **Cliquer sur "Settings"** (en haut à droite)
3. **Descendre jusqu'à "Danger Zone"** (zone rouge en bas)
4. **Cliquer sur "Transfer ownership"**
5. **Entrer le nom d'utilisateur GitHub du propriétaire**
6. **Taper le nom du repository pour confirmer**
7. **Cliquer sur "I understand, transfer this repository"**

✅ **Avantages** : Le propriétaire devient le propriétaire officiel du repository
⚠️ **Note** : Vous perdrez l'accès au repository après le transfert

---

### Option 2 : Ajouter le Propriétaire comme Collaborateur (Recommandé)

1. **Aller sur GitHub** : https://github.com/nourtd1/la-resilience
2. **Cliquer sur "Settings"**
3. **Dans le menu de gauche, cliquer sur "Collaborators"** (ou "Manage access")
4. **Cliquer sur "Add people"**
5. **Entrer le nom d'utilisateur GitHub ou l'email du propriétaire**
6. **Sélectionner le rôle "Admin"** (accès complet)
7. **Envoyer l'invitation**

✅ **Avantages** : Le propriétaire a un accès complet sans transférer le repository
✅ **Vous gardez aussi l'accès** pour maintenance future

---

## Pour le Propriétaire

### 1️⃣ Accepter l'Invitation (si Option 2)

1. **Vérifier votre email** pour l'invitation GitHub
2. **Cliquer sur le lien d'invitation**
3. **Accepter l'invitation**

Vous avez maintenant un accès Admin complet !

---

### 2️⃣ Cloner le Projet sur Votre Ordinateur

Ouvrez un terminal et tapez :

```bash
git clone https://github.com/nourtd1/la-resilience.git
cd la-resilience
```

---

### 3️⃣ Configuration de l'Environnement

#### Windows

```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

#### Linux / Mac

```bash
# Créer l'environnement virtuel
python3 -m venv venv

# Activer l'environnement
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

---

### 4️⃣ Initialiser la Base de Données

```bash
# Créer les tables
python manage.py migrate

# Créer votre compte administrateur
python manage.py createsuperuser
```

Suivez les instructions et entrez :
- Email (qui servira aussi d'identifiant)
- Prénom
- Nom
- Mot de passe (2 fois)

---

### 5️⃣ (Optionnel) Charger des Données de Test

```bash
python manage.py populate_db
```

Cela créera automatiquement :
- ✅ 10 chambres
- ✅ 15 clients
- ✅ 20 réservations
- ✅ Factures et paiements

---

### 6️⃣ Lancer l'Application

```bash
python manage.py runserver
```

Ouvrez votre navigateur sur : **http://127.0.0.1:8000**

---

## 🎯 Accès à l'Application

### Pages Principales

| Page | URL | Description |
|------|-----|-------------|
| Accueil | http://127.0.0.1:8000/ | Page d'accueil |
| Connexion | http://127.0.0.1:8000/login/ | Connexion utilisateur |
| Inscription | http://127.0.0.1:8000/register/ | Créer un nouveau compte |
| Dashboard | http://127.0.0.1:8000/dashboard/ | Tableau de bord principal |
| Admin | http://127.0.0.1:8000/admin/ | Interface d'administration |
| Chambres | http://127.0.0.1:8000/reception/rooms/ | Gestion des chambres |
| Réservations | http://127.0.0.1:8000/reception/reservations/ | Gestion des réservations |

---

## 🔐 Comptes de Test (après populate_db)

Si vous avez exécuté `populate_db`, vous pouvez vous connecter avec :

**Administrateur :**
- Email : `admin@resilience.com`
- Mot de passe : `admin123`

**Réceptionniste :**
- Email : `receptionniste@resilience.com`
- Mot de passe : `receptionniste123`

---

## 📱 Utilisation Quotidienne

### Créer une Nouvelle Réservation

1. Se connecter au dashboard
2. Aller dans **"Réservations"** → **"Nouvelle Réservation"**
3. Remplir le formulaire :
   - Sélectionner le client
   - Choisir la chambre
   - Dates d'arrivée et de départ
   - Confirmer

### Gérer les Chambres

1. Aller dans **"Chambres"**
2. Voir l'état de toutes les chambres
3. Filtrer par statut ou catégorie
4. Modifier via l'interface admin si nécessaire

### Consulter les Factures

1. Aller dans l'**interface admin** : http://127.0.0.1:8000/admin/
2. Section **"Factures"**
3. Voir toutes les factures avec leurs paiements

---

## 🚀 Déploiement en Production

### Hébergement Recommandé

- **PythonAnywhere** (Gratuit pour commencer)
- **Heroku** (Facile, payant)
- **DigitalOcean** (Serveur VPS, plus de contrôle)
- **Railway** (Moderne, simple)

### Étapes Générales

1. **Configurer les variables d'environnement**
2. **Changer `DEBUG = False` dans settings.py**
3. **Définir `ALLOWED_HOSTS`** avec votre nom de domaine
4. **Utiliser PostgreSQL ou MySQL** au lieu de SQLite
5. **Collecter les fichiers statiques** : `python manage.py collectstatic`
6. **Configurer un serveur web** (Nginx, Gunicorn)

---

## 📞 Support

Si vous rencontrez des problèmes :

1. ✅ Consultez le **README.md**
2. ✅ Vérifiez que l'environnement virtuel est activé
3. ✅ Assurez-vous que toutes les dépendances sont installées
4. ✅ Vérifiez que les migrations sont appliquées : `python manage.py migrate`

Pour une assistance technique, contactez le développeur initial.

---

**Bon courage avec votre système de gestion hôtelière ! 🏨✨**
