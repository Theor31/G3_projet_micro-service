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
    return jsonify({"status": "ok", "service": "service-economie"})


@app.route("/metrics")
def metrics():
    return jsonify({"requetes_total": _metriques["requetes"]})


# --- Votre domaine : À ÉCRIRE ---------------------------------------------
# Ajoutez ici les routes de VOTRE service (cf. 2-contrats.md). Rappels :
#   - lectures ouvertes, écritures protégées (@require_jwt / @require_role) ;
#   - après require_jwt, l'identité de l'appelant est dans request.joueur
#     (request.joueur["pseudo"], request.joueur["roles"]) ;
#   - une session de base par requête : `with db.Session() as s: ...` ;
#   - renvoyez du JSON et le bon code (201 créé, 400 mal formé, 404, 409...).

@app.route("/debiter", methods=["POST"])
@require_jwt
def debiter():
    data = request.get_json()
    if not data or "pseudo" not in data or "montant" not in data:
        return jsonify({"erreur": "JSON invalide. 'pseudo' et 'montant' requis"}), 400
        
    pseudo = data["pseudo"]
    
    # On s'assure qu'un joueur ne débite pas le compte de quelqu'un d'autre
    if request.joueur["pseudo"] != pseudo and "admin" not in request.joueur.get("roles", []):
        return jsonify({"erreur": "Accès refusé pour ce pseudo"}), 403

    try:
        montant = int(data["montant"])
    except ValueError:
        return jsonify({"erreur": "Le montant doit être un entier"}), 400
        
    if montant < 0:
        return jsonify({"erreur": "Le montant doit être positif ou nul"}), 400

    with db.Session() as s:
        compte = s.query(db.Compte).filter_by(pseudo=pseudo).first()
        
        # Si le compte n'existe pas, on considère qu'il a 0 pièce
        if not compte:
            return jsonify({"erreur": "Solde insuffisant (compte inexistant)"}), 409
            
        if compte.solde < montant:
            return jsonify({"erreur": "Solde insuffisant"}), 409
            
        compte.solde -= montant
        s.commit()
        
        return jsonify({
            "message": "Débit réussi",
            "pseudo": compte.pseudo,
            "nouveau_solde": compte.solde
        }), 200


if __name__ == "__main__":
    # 0.0.0.0 : indispensable en conteneur. Port interne uniforme : 5000.
    app.run(host="0.0.0.0", port=5000)
