RandAudit - Backend API

## Présentation

RandAudit est un système d'audit pour générateurs de nombres pseudo-aléatoires développé dans le cadre d'un mémoire de fin d'année de Master 2 TDSI. Ce dépôt contient uniquement la partie backend du projet, implémentée avec Django et Django REST Framework.

Le système permet d'exécuter et de gérer des batteries de tests statistiques (NIST, FIPS, etc.) sur différents générateurs de nombres pseudo-aléatoires afin d'évaluer leur qualité et leur conformité aux standards internationaux.

## Fonctionnalités

- Gestion des batteries de tests statistiques (TestSuite)
- Gestion des cas de tests individuels (TestCase)
- API RESTful pour l'intégration avec l'interface utilisateur
- Exécution de tests statistiques standardisés (NIST, FIPS)
- Analyse et génération de rapports sur la qualité des nombres pseudo-aléatoires

## Architecture technique

Ce backend est développé avec :
- Python 3
- Django
- Django REST Framework
- SQLite (base de données par défaut)

## Structure du projet
randaudit/  
├── api/ # Application principale │  
├── migrations/ # Migrations de base de données │  
├── models.py # Modèles de données │  
├── serializers.py # Sérialiseurs pour l'API REST │  
├── views.py # Vues et endpoints de l'API │  
└── urls.py # Configuration des routes de l'API  
 
├── randaudit/ # Configuration du projet Django │  
├── settings.py # Paramètres du projet │  
├── urls.py # Routes principales │  
└── wsgi.py # Configuration WSGI  
└── manage.py # Script de gestion Django  

## API Endpoints

### Batteries de tests (Test Suites)
- `GET /api/test-suites` - Liste toutes les batteries de tests
- `POST /api/test-suites` - Crée une nouvelle batterie de tests
- `GET /api/test-suites/{id}` - Affiche les détails d'une batterie spécifique
- `PUT /api/test-suites/{id}` - Met à jour une batterie existante
- `DELETE /api/test-suites/{id}` - Supprime une batterie de tests
- `PUT /api/run-tests` - Execute les tests sur la sequence
```json
{
   "bit_sequence" : "1100100100001111110110101010001000100001011010001100001000110100110001001100011001100010100010111000",
   "test_list" : [
      "frequency_monobit",
      "runs",
      "block_frequency"
   ]
}
```

### Cas de tests (Test Cases)
- `GET /api/test-suites/{suite_id}/test-cases` - Liste tous les cas de tests d'une batterie
- `POST /api/test-suites/{suite_id}/test-cases` - Ajoute un nouveau cas de test à une batterie
- `GET /api/test-suites/{suite_id}/test-cases/{id}` - Affiche les détails d'un cas de test spécifique
- `PUT /api/test-suites/{suite_id}/test-cases/{id}` - Met à jour un cas de test
- `DELETE /api/test-suites/{suite_id}/test-cases/{id}` - Supprime un cas de test

## Installation et démarrage

### Prérequis
- Python 3.x
- pip
- virtualenv

### Installation
1. Cloner le dépôt :
   ```
   git clone https://github.com/AmbaC0de/prng-audit-system-api.git
   cd randaudit
   ```

2. Créer et activer un environnement virtuel :
   ```
   python -m venv .venv
   source venv/bin/activate  # Sur Windows : venv\Scripts\activate
   ```

3. Installer les dépendances :
   ```
   pip install -r requirements.txt
   ```

4. Appliquer les migrations :
   ```
   python manage.py migrate
   ```

5. Lancer le serveur de développement :
   ```
   python manage.py runserver
   ```

## Tests
Pour exécuter les tests unitaires :



## Développement futur

- Implémentation complète des algorithmes de test NIST
- Intégration des tests FIPS 140-2
- Support pour différents formats d'entrée de données
- Génération de rapports détaillés au format PDF/HTML
- Intégration avec des services cloud pour l'analyse à grande échelle

## Auteur

Amadou BA - Master 2 Transmission de donnees et securite de l'information (TDSI)

## Licence

[Préciser la licence]
