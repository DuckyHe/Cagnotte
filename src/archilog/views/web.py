import logging
import uuid

from flask import Blueprint, flash, redirect, render_template, request, url_for

from archilog import domain
from archilog.auth import basic_auth
from archilog.forms import CagnotteForm, DepenseForm

logger = logging.getLogger(__name__)

web_ui = Blueprint("web_ui", __name__)


@web_ui.errorhandler(500)
def handle_500(error):
    logger.exception("Erreur 500 : %s", error)
    flash("Une erreur interne s'est produite.", "error")
    return redirect(url_for("web_ui.index"))


# ---------------------------------------------------------------------------
# Cagnottes
# ---------------------------------------------------------------------------

@web_ui.route("/")
@basic_auth.login_required
def index():
    form = CagnotteForm()
    cagnottes = domain.lister_cagnottes()
    return render_template("index.html", cagnottes=cagnottes, form=form)


@web_ui.route("/cagnottes/creer", methods=["POST"])
@basic_auth.login_required(role="admin")
def cagnotte_creer():
    form = CagnotteForm()
    if form.validate_on_submit():
        domain.creer_cagnotte(form.nom.data.strip())
    else:
        for field_errors in form.errors.values():
            for msg in field_errors:
                flash(msg, "error")
    return redirect(url_for("web_ui.index"))


@web_ui.route("/cagnottes/<cagnotte_id>")
@basic_auth.login_required
def cagnotte_detail(cagnotte_id: str):
    try:
        cid = uuid.UUID(cagnotte_id)
    except ValueError:
        return redirect(url_for("web_ui.index"))
    cagnotte = domain.obtenir_cagnotte(cid)
    if cagnotte is None:
        return redirect(url_for("web_ui.index"))
    depenses = domain.lister_depenses(cid)
    remboursements = domain.calculer_remboursements(cid)
    form = DepenseForm()
    return render_template(
        "cagnotte_detail.html",
        cagnotte=cagnotte,
        depenses=depenses,
        remboursements=remboursements,
        form=form,
    )


@web_ui.route("/cagnottes/<cagnotte_id>/supprimer", methods=["POST"])
@basic_auth.login_required(role="admin")
def cagnotte_supprimer(cagnotte_id: str):
    try:
        cid = uuid.UUID(cagnotte_id)
        domain.supprimer_cagnotte(cid)
    except ValueError:
        pass
    return redirect(url_for("web_ui.index"))


# ---------------------------------------------------------------------------
# Dépenses
# ---------------------------------------------------------------------------

@web_ui.route("/cagnottes/<cagnotte_id>/depenses/ajouter", methods=["POST"])
@basic_auth.login_required
def depense_ajouter(cagnotte_id: str):
    try:
        cid = uuid.UUID(cagnotte_id)
    except ValueError:
        return redirect(url_for("web_ui.index"))

    form = DepenseForm()
    if form.validate_on_submit():
        try:
            domain.ajouter_depense(
                cid,
                form.participant.data.strip(),
                form.montant.data,
                form.date_paiement.data,
            )
            return redirect(url_for("web_ui.cagnotte_detail", cagnotte_id=cagnotte_id))
        except ValueError as e:
            cagnotte = domain.obtenir_cagnotte(cid)
            depenses = domain.lister_depenses(cid)
            remboursements = domain.calculer_remboursements(cid)
            return render_template(
                "cagnotte_detail.html",
                cagnotte=cagnotte,
                depenses=depenses,
                remboursements=remboursements,
                form=form,
                error=str(e),
            )

    # Erreurs de validation WTForms
    cagnotte = domain.obtenir_cagnotte(cid)
    depenses = domain.lister_depenses(cid)
    remboursements = domain.calculer_remboursements(cid)
    return render_template(
        "cagnotte_detail.html",
        cagnotte=cagnotte,
        depenses=depenses,
        remboursements=remboursements,
        form=form,
    )


@web_ui.route("/depenses/<depense_id>/supprimer", methods=["POST"])
@basic_auth.login_required
def depense_supprimer(depense_id: str):
    cagnotte_id = request.form.get("cagnotte_id", "")
    try:
        did = uuid.UUID(depense_id)
        domain.supprimer_depense(did)
    except ValueError:
        pass
    return redirect(url_for("web_ui.cagnotte_detail", cagnotte_id=cagnotte_id))


# ---------------------------------------------------------------------------
# Point d'entrée (archilog-web)
# ---------------------------------------------------------------------------

def run():
    from archilog import create_app
    from archilog.config import config

    app = create_app()
    app.run(debug=config.DEBUG)
