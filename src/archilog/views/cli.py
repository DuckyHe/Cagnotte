
import uuid
from datetime import date

import click

from archilog.data import init_db
from archilog import domain


@click.group()
def cli():
    """Archilog - Gestionnaire de cagnottes / partage des dépenses."""
    init_db()


@cli.group()
def cagnotte():
    """Gestion des cagnottes."""
    pass


@cagnotte.command("creer")
@click.option("--nom", prompt="Nom de la cagnotte", help="Nom de la cagnotte")
def cagnotte_creer(nom: str):
    """Crée une nouvelle cagnotte."""
    c = domain.creer_cagnotte(nom)
    click.echo(f"✓ Cagnotte créée : {c.nom} (id={c.id})")


@cagnotte.command("lister")
def cagnotte_lister():
    """Liste toutes les cagnottes."""
    cagnottes = domain.lister_cagnottes()
    if not cagnottes:
        click.echo("Aucune cagnotte.")
        return
    for c in cagnottes:
        click.echo(f"  [{c.id}] {c.nom}")


@cagnotte.command("supprimer")
@click.argument("cagnotte_id")
def cagnotte_supprimer(cagnotte_id: str):
    """Supprime une cagnotte et ses dépenses."""
    try:
        cid = uuid.UUID(cagnotte_id)
    except ValueError:
        click.echo("Identifiant invalide.", err=True)
        return
    domain.supprimer_cagnotte(cid)
    click.echo(f"✓ Cagnotte {cagnotte_id} supprimée.")



@cli.group()
def depense():
    """Gestion des dépenses."""
    pass


@depense.command("ajouter")
@click.option("--cagnotte-id", required=True, help="ID de la cagnotte")
@click.option("--participant", prompt="Participant", help="Nom du participant")
@click.option("--montant", prompt="Montant (€)", type=float, help="Montant payé")
@click.option(
    "--date",
    "date_paiement",
    default=str(date.today()),
    show_default=True,
    help="Date (YYYY-MM-DD)",
)
def depense_ajouter(cagnotte_id: str, participant: str, montant: float, date_paiement: str):
    """Ajoute une dépense à une cagnotte."""
    try:
        cid = uuid.UUID(cagnotte_id)
    except ValueError:
        click.echo("Identifiant de cagnotte invalide.", err=True)
        return
    try:
        dp = date.fromisoformat(date_paiement)
    except ValueError:
        click.echo("Date invalide (format attendu : YYYY-MM-DD).", err=True)
        return
    try:
        d = domain.ajouter_depense(cid, participant, montant, dp)
        click.echo(f"✓ Dépense ajoutée : {d.participant} → {d.montant}€ le {d.date_paiement}")
    except ValueError as e:
        click.echo(f"Erreur : {e}", err=True)


@depense.command("lister")
@click.option("--cagnotte-id", required=True, help="ID de la cagnotte")
def depense_lister(cagnotte_id: str):
    """Liste les dépenses d'une cagnotte."""
    try:
        cid = uuid.UUID(cagnotte_id)
    except ValueError:
        click.echo("Identifiant invalide.", err=True)
        return
    depenses = domain.lister_depenses(cid)
    if not depenses:
        click.echo("Aucune dépense.")
        return
    for d in depenses:
        click.echo(f"  [{d.id}] {d.participant} : {d.montant}€ le {d.date_paiement}")


@depense.command("supprimer")
@click.argument("depense_id")
def depense_supprimer(depense_id: str):
    """Supprime une dépense."""
    try:
        did = uuid.UUID(depense_id)
    except ValueError:
        click.echo("Identifiant invalide.", err=True)
        return
    domain.supprimer_depense(did)
    click.echo(f"✓ Dépense {depense_id} supprimée.")



@cli.command("remboursements")
@click.option("--cagnotte-id", required=True, help="ID de la cagnotte")
def remboursements(cagnotte_id: str):
    """Affiche qui doit quoi à qui."""
    try:
        cid = uuid.UUID(cagnotte_id)
    except ValueError:
        click.echo("Identifiant invalide.", err=True)
        return
    rembours = domain.calculer_remboursements(cid)
    if not rembours:
        click.echo("Aucun remboursement nécessaire.")
        return
    click.echo("Remboursements à effectuer :")
    for r in rembours:
        click.echo(f"  {r.debiteur} doit {r.montant}€ à {r.creancier}")
