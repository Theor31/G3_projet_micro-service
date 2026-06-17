# Service Économie

Ce projet est un micro-service Flask nommé **service-economie**.

Il permet de gérer l’économie d’un jeu ou d’une application avec des comptes joueurs, un solde, des crédits et des débits.

Le service expose une API REST en JSON et utilise une base de données SQLite.

---

## Fonctionnement général

Le service gère des comptes identifiés par un `pseudo`.

Chaque compte possède :

- un `pseudo`, qui sert d’identifiant unique ;
- un `solde`, qui représente le montant disponible sur le compte.

La base de données est propre à ce micro-service.  
Par défaut, elle est stockée dans un fichier SQLite nommé `data.db`.

Le service permet de :

- vérifier que le service fonctionne ;
- consulter les métriques ;
- créditer un compte ;
- consulter le solde d’un joueur ;
- débiter un compte.

---

## Technologies utilisées

- Python 3.12
- Flask
- SQLAlchemy
- SQLite
- JWT
- Docker
- Docker Compose

---

## Routes disponibles

## GET `/health`

Permet de vérifier que le service est bien lancé.

### Exemple de requête

```bash
curl http://localhost:5001/health
```

### Exemple de réponse

```json
{
  "status": "ok",
  "service": "service-economie"
}
```

---

## GET `/metrics`

Permet de récupérer le nombre total de requêtes reçues par le service.

### Exemple de requête

```bash
curl http://localhost:5001/metrics
```

### Exemple de réponse

```json
{
  "requetes_total": 12
}
```

---

## POST `/crediter`

Permet de créditer le compte d’un joueur.

Cette route est réservée aux utilisateurs ayant le rôle `admin`.

### Authentification

Il faut envoyer un token JWT dans le header HTTP :

```http
Authorization: Bearer <token>
```

Le token doit contenir le rôle `admin`.

### Corps de la requête

```json
{
  "pseudo": "joueur1",
  "montant": 100
}
```

### Exemple de requête

```bash
curl -X POST http://localhost:5001/crediter \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token_admin>" \
  -d '{"pseudo": "joueur1", "montant": 100}'
```

### Exemple de réponse

```json
{
  "pseudo": "joueur1",
  "nouveau_solde": 100,
  "message": "Compte crédité avec succès"
}
```

### Fonctionnement

- Si le compte n’existe pas, il est créé automatiquement.
- Si le compte existe déjà, le montant est ajouté au solde existant.
- Le montant doit être un entier strictement positif.

### Codes HTTP possibles

| Code | Signification |
|---|---|
| `201` | Compte créé et crédité |
| `200` | Compte existant crédité |
| `400` | Données invalides |
| `401` | Token JWT absent ou invalide |
| `403` | Rôle `admin` manquant |

---

## GET `/solde/<pseudo>`

Permet de consulter le solde d’un joueur.

### Exemple de requête

```bash
curl http://localhost:5001/solde/joueur1
```

### Exemple de réponse

```json
{
  "pseudo": "joueur1",
  "solde": 100
}
```

### Codes HTTP possibles

| Code | Signification |
|---|---|
| `200` | Solde trouvé |
| `404` | Pseudo introuvable |

---

## POST `/debiter`

Permet de retirer un montant du compte d’un joueur.

Cette route nécessite un token JWT valide.

### Authentification

Il faut envoyer un token JWT dans le header HTTP :

```http
Authorization: Bearer <token>
```

Un joueur peut uniquement débiter son propre compte.  
Un utilisateur avec le rôle `admin` peut débiter n’importe quel compte.

### Corps de la requête

```json
{
  "pseudo": "joueur1",
  "montant": 50
}
```

### Exemple de requête

```bash
curl -X POST http://localhost:5001/debiter \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token_joueur>" \
  -d '{"pseudo": "joueur1", "montant": 50}'
```

### Exemple de réponse

```json
{
  "pseudo": "joueur1",
  "nouveau_solde": 50,
  "message": "Débit réussi"
}
```

### Fonctionnement

- Le compte doit exister.
- Le solde doit être suffisant.
- Le montant doit être un entier positif ou nul.
- Un joueur ne peut pas débiter le compte d’un autre joueur.
- Un administrateur peut débiter n’importe quel compte.

### Codes HTTP possibles

| Code | Signification |
|---|---|
| `200` | Débit effectué |
| `400` | JSON invalide ou montant incorrect |
| `401` | Token JWT absent ou invalide |
| `403` | Accès refusé pour ce pseudo |
| `409` | Solde insuffisant ou compte inexistant |

---

## Authentification JWT

Certaines routes sont protégées par JWT.

Le token doit être envoyé dans l’en-tête HTTP suivant :

```http
Authorization: Bearer <token>
```

Le token doit contenir un payload de cette forme :

```json
{
  "pseudo": "joueur1",
  "roles": ["joueur"]
}
```

Pour un administrateur :

```json
{
  "pseudo": "admin",
  "roles": ["admin"]
}
```

Le secret JWT peut être configuré avec la variable d’environnement :

```bash
JWT_SECRET=je-suis-le-secret-tres-secret-12
```

---

## Variables d’environnement

| Variable | Description | Valeur par défaut |
|---|---|---|
| `DB_PATH` | Chemin du fichier SQLite utilisé par le service | `data.db` |
| `JWT_SECRET` | Secret utilisé pour vérifier les tokens JWT | `je-suis-le-secret-tres-secret-12` |

---
## Lancer le service avec Docker

### 1. Construire l’image Docker

A la racinedu projet :
```bash
docker compose -d --build
```

Le service sera accessible sur :

```text
http://localhost:5003
```

---

## Lancer le service avec Docker Compose

Si un fichier `docker-compose.yaml` est présent à la racine du projet, le service peut être lancé avec :

```bash
docker compose up --build
```

Pour arrêter les conteneurs :

```bash
docker compose down
```

---

## Structure simplifiée du projet

```text
service-economie/
├── app.py
├── auth.py
├── db.py
├── Dockerfile
└── requirements.txt
```

---

## Rôle des fichiers principaux

| Fichier | Rôle |
|---|---|
| `app.py` | Contient l’application Flask et les routes REST |
| `auth.py` | Gère la vérification des tokens JWT et des rôles |
| `db.py` | Configure la base SQLite et le modèle de compte |
| `Dockerfile` | Permet de construire l’image Docker du service |
| `requirements.txt` | Contient les dépendances Python du projet |

---

## Résumé

Ce micro-service permet de gérer une économie simple pour des joueurs.

Il permet de :

- créer automatiquement un compte lors d’un crédit ;
- créditer un joueur ;
- débiter un joueur ;
- consulter le solde d’un joueur ;
- stocker les données dans SQLite ;
- être lancé en local, avec Docker ou avec Docker Compose.
