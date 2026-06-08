import logging
import uuid
from datetime import date
from typing import Optional

from flask import Blueprint, jsonify, request
from pydantic import BaseModel
from spectree import Response, SecurityScheme, SpecTree

from archilog import domain
from archilog.auth import token_auth

logger = logging.getLogger(__name__)

api_spec = SpecTree(
    "flask",
    title="Archilog API",
    version="0.1.0",
    path="apidoc",
    security_schemes=[
        SecurityScheme(
            name="BearerAuth",
            data={"type": "http", "scheme": "bearer"},
        )
    ],
    security={"BearerAuth": []},
)
api = Blueprint("api", __name__)


# ---------------------------------------------------------------------------
# Modèles Pydantic
# ---------------------------------------------------------------------------

class CagnotteIn(BaseModel):
    nom: str


class CagnotteOut(BaseModel):
    id: str
    nom: str


class DepenseIn(BaseModel):
    participant: str
    montant: float
    date_paiement: Optional[str] = None


class DepenseOut(BaseModel):
    id: str
    participant: str
    montant: float
    date_paiement: str


class RemboursementOut(BaseModel):
    debiteur: str
    creancier: str
    montant: float


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@api.errorhandler(500)
def handle_500(error):
    logger.exception("Erreur 500 API : %s", error)
    return jsonify({"error": "Erreur interne du serveur"}), 500


@api.route("/cagnottes", methods=["GET"])
@token_auth.login_required
def list_cagnottes():
    return jsonify([{"id": str(c.id), "nom": c.nom} for c in domain.lister_cagnottes()])


@api.route("/cagnottes", methods=["POST"])
@token_auth.login_required(role="admin")
@api_spec.validate(json=CagnotteIn)
def create_cagnotte():
    data = request.context.json
    c = domain.creer_cagnotte(data.nom.strip())
    return jsonify({"id": str(c.id), "nom": c.nom}), 201


@api.route("/cagnottes/<cagnotte_id>", methods=["DELETE"])
@token_auth.login_required(role="admin")
def delete_cagnotte(cagnotte_id: str):
    try:
        cid = uuid.UUID(cagnotte_id)
    except ValueError:
        return jsonify({"error": "id invalide"}), 400
    domain.supprimer_cagnotte(cid)
    return "", 204


@api.route("/cagnottes/<cagnotte_id>/depenses", methods=["GET"])
@token_auth.login_required
def list_depenses(cagnotte_id: str):
    try:
        cid = uuid.UUID(cagnotte_id)
    except ValueError:
        return jsonify({"error": "id invalide"}), 400
    return jsonify(
        [
            {
                "id": str(d.id),
                "participant": d.participant,
                "montant": d.montant,
                "date_paiement": str(d.date_paiement),
            }
            for d in domain.lister_depenses(cid)
        ]
    )


@api.route("/cagnottes/<cagnotte_id>/depenses", methods=["POST"])
@token_auth.login_required
@api_spec.validate(json=DepenseIn)
def add_depense(cagnotte_id: str):
    try:
        cid = uuid.UUID(cagnotte_id)
    except ValueError:
        return jsonify({"error": "id invalide"}), 400
    data = request.context.json
    try:
        dp = date.fromisoformat(data.date_paiement) if data.date_paiement else date.today()
        d = domain.ajouter_depense(cid, data.participant, data.montant, dp)
        return (
            jsonify({"id": str(d.id), "participant": d.participant, "montant": d.montant}),
            201,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@api.route("/depenses/<depense_id>", methods=["DELETE"])
@token_auth.login_required
def delete_depense(depense_id: str):
    try:
        did = uuid.UUID(depense_id)
    except ValueError:
        return jsonify({"error": "id invalide"}), 400
    domain.supprimer_depense(did)
    return "", 204


@api.route("/cagnottes/<cagnotte_id>/remboursements", methods=["GET"])
@token_auth.login_required
def get_remboursements(cagnotte_id: str):
    try:
        cid = uuid.UUID(cagnotte_id)
    except ValueError:
        return jsonify({"error": "id invalide"}), 400
    return jsonify(
        [
            {"debiteur": r.debiteur, "creancier": r.creancier, "montant": r.montant}
            for r in domain.calculer_remboursements(cid)
        ]
    )


api_spec.register(api)
