import os
from functools import wraps

import jwt          # PyJWT : jwt.encode / jwt.decode (HS256)
from flask import request, jsonify

# Secret partagé : DOIT être le même pour tous les services (sinon les jetons
# émis par service-comptes sont rejetés ailleurs). Fixé dans docker-compose.yml.
SECRET = os.environ.get("JWT_SECRET", "je-suis-le-secret-tres-secret-12")

def creer_token(sujet, roles=["joueur"]):
    return jwt.encode({"pseudo": sujet, "roles": roles}, SECRET, algorithm="HS256")

def require_jwt(f):
    @wraps(f)
    def verifie(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"erreur": "Jeton manquant ou mal formaté"}), 401
            
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET, algorithms=["HS256"])
            request.joueur = payload
        except jwt.PyJWTError:
            return jsonify({"erreur": "Jeton invalide ou expiré"}), 401
            
        return f(*args, **kwargs)
    return verifie


def require_role(role):
    def decorateur(f):
        @wraps(f)
        def verifie(*args, **kwargs):
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return jsonify({"erreur": "Jeton manquant ou mal formaté"}), 401
                
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, SECRET, algorithms=["HS256"])
                request.joueur = payload
            except jwt.PyJWTError:
                return jsonify({"erreur": "Jeton invalide ou expiré"}), 401
                
            if role not in payload.get("roles", []):
                return jsonify({"erreur": f"Accès refusé : le rôle {role} est requis"}), 403
                
            return f(*args, **kwargs)
        return verifie
    return decorateur
