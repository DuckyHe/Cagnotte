# Cagnotte — Gestionnaire de dépenses partagées

Application web et CLI pour gérer des cagnottes et calculer automatiquement les remboursements entre participants.

## Fonctionnalités

- Créer et gérer plusieurs cagnottes
- Enregistrer les dépenses par participant
- Calcul automatique de **qui doit quoi à qui**
- Interface web avec authentification (HTTP Basic)
- API REST documentée avec OpenAPI (Bearer token)
- Interface en ligne de commande (CLI)

## Installation

Prérequis : Python 3.12+ et [uv](https://docs.astral.sh/uv/)

```bash
git clone https://github.com/DuckyHe/Cagnotte.git
cd Cagnotte
uv sync
```

## Utilisation

### Interface web

```bash
uv run archilog-web
```

Ouvre [http://localhost:5000](http://localhost:5000) dans ton navigateur.  
L'authentification HTTP Basic est requise (configurée via les variables d'environnement).

La documentation de l'API REST est disponible sur [http://localhost:5000/apidoc](http://localhost:5000/apidoc).

### CLI

```bash
uv run archilog --help
```

#### Cagnottes

```bash
# Créer une cagnotte
uv run archilog cagnotte creer --nom "Vacances été"

# Lister les cagnottes
uv run archilog cagnotte lister

# Supprimer une cagnotte
uv run archilog cagnotte supprimer <cagnotte_id>
```

#### Dépenses

```bash
# Ajouter une dépense
uv run archilog depense ajouter --cagnotte-id <id> --participant Alice --montant 45.00

# Lister les dépenses d'une cagnotte
uv run archilog depense lister --cagnotte-id <id>

# Supprimer une dépense
uv run archilog depense supprimer <depense_id>
```

#### Remboursements

```bash
# Voir qui doit quoi à qui
uv run archilog remboursements --cagnotte-id <id>
```

Exemple de sortie :
```
Remboursements à effectuer :
  Bob doit 15.00€ à Alice
  Charlie doit 7.50€ à Alice
```

## API REST

Toutes les routes nécessitent un token Bearer (`Authorization: Bearer <token>`).  
Les routes de création/suppression de cagnotte sont réservées au rôle `admin`.

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/cagnottes` | Lister toutes les cagnottes |
| `POST` | `/cagnottes` | Créer une cagnotte |
| `DELETE` | `/cagnottes/<id>` | Supprimer une cagnotte |
| `GET` | `/cagnottes/<id>/depenses` | Lister les dépenses |
| `POST` | `/cagnottes/<id>/depenses` | Ajouter une dépense |
| `DELETE` | `/depenses/<id>` | Supprimer une dépense |
| `GET` | `/cagnottes/<id>/remboursements` | Calculer les remboursements |

## Stack technique

| Outil | Rôle |
|-------|------|
| [Flask](https://flask.palletsprojects.com/) | Serveur web |
| [Click](https://click.palletsprojects.com/) | Interface CLI |
| [SQLAlchemy](https://www.sqlalchemy.org/) | ORM / base de données |
| [Pydantic](https://docs.pydantic.dev/) | Validation des données API |
| [SpecTree](https://github.com/0b01001001/spectree) | Documentation OpenAPI |
| [Flask-WTF](https://flask-wtf.readthedocs.io/) | Formulaires web |
| [Flask-HTTPAuth](https://flask-httpauth.readthedocs.io/) | Authentification |
