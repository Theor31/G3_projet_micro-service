"""Squelette minimal d'un micro-service Voxenfer (à copier et adapter).

Auteur : Philippe ROUSSILLE <roussille@3il.fr>

Vous avez tout vu aux TP 08 à 12 : Flask + routes REST/JSON avec les bons codes,
JWT (auth.py), /health et /metrics, une base propre au service via un ORM (db.py).
Ce fichier ne donne QUE la charpente : à vous d'écrire les routes de votre domaine
(voir 2-contrats.md pour celles qu'on attend de votre service).
"""
from flask import Flask, request, jsonify

import db
from auth import require_jwt, require_role

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


@app.route("/solde/<pseudo>", methods=["GET"])
def get_solde(pseudo):
    session = db.Session()
    compte = session.get(db.Compte, pseudo)
    session.close()
    if compte is None:
        return jsonify({"erreur": "Pseudo introuvable"}), 404
    return jsonify({"pseudo": pseudo, "solde": compte.solde})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
