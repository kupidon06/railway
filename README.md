# Railway Digital Twin - Plateforme Intelligente pour Nœud Ferroviaire

Système de jumeau numérique intelligent pour la visualisation, simulation et prédiction des opérations ferroviaires.

## 🚀 Fonctionnalités

### ✅ Phase 1 (MVP) - **IMPLÉMENTÉ**

- ✅ **Modèles de données core** : Node, Track, Train, Schedule, Event, Incident
- ✅ **Modèles de visualisation** : TrainPosition (temps réel)
- ✅ **Modèles de simulation** : SimulationScenario, SimulationRun
- ✅ **Modèles IA/ML** : MLModel, PredictionResult
- ✅ **Modèles Analytics** : Alert
- ✅ **Interface Admin Django** complète avec badges colorés et actions personnalisées
- ✅ **Génération de données de démo** : 5 nœuds, 108 voies, 11 trains
- ✅ **Système de permissions RBAC** : Admin, Operator, Analyst, Viewer, API_User

### 📋 Prochaines Étapes (Selon le Plan)

- **Phase 2** : API REST avec DRF, Dashboard web avec Tailwind CSS
- **Phase 3** : WebSocket temps réel avec Django Channels
- **Phase 4** : Moteur de simulation avec détection de conflits
- **Phase 5** : Prédictions IA/ML (congestion, anomalies, risques)
- **Phase 6** : Analytics, reporting, KPIs

## 🏗️ Architecture

```
railway_project/
├── railway_core/          # Modèles de base (Node, Track, Train, Schedule, Event, Incident)
├── railway_twin/          # Jumeau numérique (TrainPosition)
├── railway_simulation/    # Moteur de simulation
├── railway_ai/            # IA/ML prédictif
├── railway_analytics/     # Analytics & reporting
└── common/                # Utilitaires partagés (TimeStampedModel, SoftDeleteModel, Permissions)
```

## 🛠️ Stack Technique

- **Backend** : Django 5.2.9, Django REST Framework (à venir)
- **Database** : SQLite3 (dev), PostgreSQL + TimescaleDB (prod)
- **Frontend** : Django Templates, Tailwind CSS (à venir)
- **IA/ML** : scikit-learn, pandas, numpy (à venir)
- **Real-time** : Django Channels, Redis (Phase 2)

## 🚦 Installation & Démarrage

### 1. Prérequis

```bash
Python 3.13
Django 5.2.9
```

### 2. Installation

```bash
cd /Users/mac/Desktop/authy/railway_project

# Installer les dépendances (si nécessaire)
pip install Django==5.2.9

# Appliquer les migrations (déjà fait)
python manage.py migrate

# Générer des données de démo
python manage.py seed_data
```

### 3. Créer un superuser

```bash
python manage.py createsuperuser
```

### 4. Lancer le serveur

```bash
python manage.py runserver
```

### 5. Accéder à l'application

- **Interface Admin** : http://localhost:8000/admin
- **API** (à venir) : http://localhost:8000/api/
- **Dashboard** (à venir) : http://localhost:8000/

## 📊 Données de Démo

La commande `seed_data` génère :

- **5 Nœuds (Stations)** :
  - Paris Gare du Nord (30 voies)
  - Lyon Part-Dieu (25 voies)
  - Marseille Saint-Charles (20 voies)
  - Lille Europe (15 voies)
  - Bordeaux Saint-Jean (18 voies)

- **108 Voies** réparties sur les 5 nœuds
- **11 Trains** : 3 TGV, 2 Intercité, 4 TER, 2 Cargo
- **29 Horaires** pour les prochaines 24 heures
- **50 Événements** (arrivées, départs, retards, changements de voie)
- **2 Incidents** actifs

### Effacer et régénérer les données

```bash
python manage.py seed_data --clear
```

## 🎨 Interface Admin

L'interface admin Django inclut :

### Gestion des Nœuds (Nodes)
- Vue liste avec code, nom, type, capacité, nombre de voies actives
- Filtres par type et statut
- Recherche par code et nom

### Gestion des Voies (Tracks)
- Vue liste avec statut, direction, vitesse max
- Filtres par statut, direction, nœud
- Autocomplétion pour les nœuds

### Gestion des Trains (Trains)
- Vue liste avec numéro, type, opérateur, capacité
- Filtres par type et opérateur
- Recherche par numéro et opérateur

### Horaires (Schedules)
- Vue liste avec badges de statut colorés (ON_TIME vert, DELAYED orange, CANCELLED rouge)
- Filtres par statut, nœud, date
- Hiérarchie par date d'arrivée
- Autocomplétion pour trains, nœuds, voies

### Événements (Events)
- Vue liste avec badges de sévérité colorés
- Filtres par type, sévérité, nœud
- Recherche par description
- Hiérarchie par date

### Incidents
- Vue liste avec badges de sévérité et durée
- Filtres par type, sévérité, statut, nœud
- Gestion many-to-many des voies et trains affectés
- Hiérarchie par date de début

### Alertes (Alerts)
- Vue liste avec statut d'acquittement
- Actions groupées : Acquitter, Rejeter
- Filtres par type, sévérité, statut

### Simulations
- Gestion des scénarios et exécutions
- Badges de statut (RUNNING bleu, COMPLETED vert, FAILED rouge)
- Paramètres JSON configurables

### Modèles ML & Prédictions
- Gestion des versions de modèles
- Action pour activer un modèle
- Résultats de prédictions avec feedback loop

## 🔐 Système de Permissions (RBAC)

Rôles définis dans `common/permissions.py` :

- **ADMIN** : Accès complet, gestion utilisateurs, configuration
- **OPERATOR** : Dashboard, incidents, simulations, alertes
- **ANALYST** : Dashboard, simulations (lecture seule), rapports
- **VIEWER** : Dashboard lecture seule
- **API_USER** : Accès API programmatique (ingestion de données)

## 📦 Modèles de Données

### Core Models ([railway_core/models.py](railway_core/models.py))

- **Node** : Station/Junction/Depot avec GPS, capacité, timezone
- **Track** : Voie physique avec direction, vitesse max, statut
- **Train** : Train avec type (TGV/TER/Cargo), capacité, caractéristiques
- **Schedule** : Horaire avec heures prévues/réelles, statut, retard
- **Event** : Événement horodaté (arrivée, départ, retard, changement)
- **Incident** : Incident opérationnel avec sévérité, voies/trains affectés

### Digital Twin ([railway_twin/models.py](railway_twin/models.py))

- **TrainPosition** : Position temps réel des trains (horodaté, GPS, vitesse)

### Simulation ([railway_simulation/models.py](railway_simulation/models.py))

- **SimulationScenario** : Scénario de simulation configurable
- **SimulationRun** : Exécution d'un scénario avec résultats JSON

### AI/ML ([railway_ai/models.py](railway_ai/models.py))

- **MLModel** : Version de modèle ML avec métriques de performance
- **PredictionResult** : Résultat de prédiction avec feedback loop

### Analytics ([railway_analytics/models.py](railway_analytics/models.py))

- **Alert** : Alerte système avec acquittement et auto-rejet

## 🧪 Tests

```bash
# Lancer les tests (à venir)
python manage.py test
```

## 📝 Commandes de Management

### seed_data
```bash
# Générer des données de démo
python manage.py seed_data

# Effacer et régénérer
python manage.py seed_data --clear
```

### Futures commandes (selon le plan)
- `import_schedules` : Importer des horaires depuis CSV/JSON
- `retrain_models` : Réentraîner les modèles ML
- `generate_report` : Générer des rapports

## 🗂️ Structure de Settings

Les settings sont organisés en 3 fichiers :

- **base.py** : Configuration commune
- **development.py** : SQLite, DEBUG=True, logging détaillé
- **production.py** : PostgreSQL, Redis, Celery, Security hardened

Le système détecte automatiquement l'environnement via `DJANGO_SETTINGS_MODULE`.

## 🎯 Roadmap

- [x] **Semaine 1** : Bootstrap projet + patterns réutilisables
- [x] **Semaine 2** : Modèles core + Admin interfaces + Seed data
- [ ] **Semaine 3** : API REST (DRF) + Documentation
- [ ] **Semaine 4** : Dashboard web basique (Tailwind CSS)
- [ ] **Semaine 5-6** : WebSocket temps réel + Incidents
- [ ] **Semaine 7-9** : Moteur de simulation
- [ ] **Semaine 10-13** : IA/ML prédictif
- [ ] **Semaine 14-15** : Analytics & Reporting
- [ ] **Semaine 16+** : Production hardening (Docker, CI/CD, monitoring)

## 📚 Documentation

- [Plan complet d'implémentation](../.claude/plans/melodic-munching-hamster.md)
- [Spécification Railway](../Railway/readme.md)
- [Django Documentation](https://docs.djangoproject.com/)

## 🤝 Contribution

Projet généré avec **Claude Sonnet 4.5** via [Claude Code](https://claude.com/claude-code)

---

**Status** : ✅ Phase 1 (MVP Foundation) - COMPLET
**Prochaine étape** : Phase 2 (API REST + Dashboard basique)
