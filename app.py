"""Squelette minimal d'un micro-service Voxenfer (à copier et adapter).

Auteur : Philippe ROUSSILLE <roussille@3il.fr>

Vous avez tout vu aux TP 08 à 12 : Flask + routes REST/JSON avec les bons codes,
JWT (auth.py), /health et /metrics, une base propre au service via un ORM (db.py).
Ce fichier ne donne QUE la charpente : à vous d'écrire les routes de votre domaine
(voir 2-contrats.md pour celles qu'on attend de votre service).
"""
from flask import Flask, request, jsonify

import db
from auth import require_jwt, require_role  # à compléter dans auth.py ; protège vos écritures
  
app = Flask(__name__)
db.init()

_metriques = {"requetes": 0}


@app.before_request
def _compter():
    _metriques["requetes"] += 1


# --- Observabilité (à garder tel quel) ------------------------------------

@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "VOTRE-NOM"})  # mettez votre nom


@app.route("/metrics")
def metrics():
    return jsonify({"requetes_total": _metriques["requetes"]})

# --- Votre domaine : Route Créditer ---------------------------------------

@app.route("/crediter", methods=["POST"])
@require_role("admin")  
def crediter_compte():
    """
    Crédite le compte d'un joueur (Réservé Admin).
    Attend un JSON : { "pseudo": "NomDuJoueur", "montant": 100 }
    """
    donnees = request.get_json(silent=True)
    
    if not donnees or "pseudo" not in donnees or "montant" not in donnees:
        return jsonify({"erreur": "Données manquantes (pseudo et montant requis)"}), 400
    
    pseudo = donnees["pseudo"]
    montant = donnees["montant"]
    
    if not isinstance(montant, int) or montant <= 0:
        return jsonify({"erreur": "Le montant doit être un entier strictement positif"}), 400

    with db.Session() as session:
        compte = session.get(db.Compte, pseudo)
        
        if not compte:
            # Si le pseudo n'existe pas, on crée le compte avec le crédit initial
            compte = db.Compte(pseudo=pseudo, solde=montant)
            session.add(compte)
            code_statut = 201  # 201 Created pour une création
        else:
            # Sinon, on ajoute le montant au solde existant
            compte.solde += montant
            code_statut = 200  # 200 OK pour une mise à jour
        
        # Validation et enregistrement dans la base de données
        session.commit()
        
        return jsonify({
            "pseudo": compte.pseudo,
            "nouveau_solde": compte.solde,
            "message": "Compte crédité avec succès"
        }), code_statut


# --- Votre domaine : À ÉCRIRE ---------------------------------------------
# Ajoutez ici les routes de VOTRE service (cf. 2-contrats.md). Rappels :
#   - lectures ouvertes, écritures protégées (@require_jwt / @require_role) ;
#   - après require_jwt, l'identité de l'appelant est dans request.joueur
#     (request.joueur["pseudo"], request.joueur["roles"]) ;
#   - une session de base par requête : `with db.Session() as s: ...` ;
#   - renvoyez du JSON et le bon code (201 créé, 400 mal formé, 404, 409...).


if __name__ == "__main__":
    # 0.0.0.0 : indispensable en conteneur. Port interne uniforme : 5000.
    app.run(host="0.0.0.0", port=5000)


