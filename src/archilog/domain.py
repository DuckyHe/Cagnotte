"""
Couche domain : logique métier de l'application cagnotte.

Règles :
- une seule dépense par participant à une cagnotte
- calcul du "qui doit à qui"
"""
import uuid
from dataclasses import dataclass
from datetime import date
from typing import Optional

from archilog import data


@dataclass
class Cagnotte:
    id: uuid.UUID
    nom: str


@dataclass
class Depense:
    id: uuid.UUID
    cagnotte_id: uuid.UUID
    participant: str
    montant: float
    date_paiement: date


@dataclass
class Remboursement:
    debiteur: str
    creancier: str
    montant: float


# ---------------------------------------------------------------------------
# Cagnottes
# ---------------------------------------------------------------------------

def creer_cagnotte(nom: str) -> Cagnotte:
    new_id = uuid.uuid4()
    data.insert_cagnotte(new_id, nom)
    return Cagnotte(id=new_id, nom=nom)


def supprimer_cagnotte(cagnotte_id: uuid.UUID) -> None:
    data.delete_cagnotte(cagnotte_id)


def lister_cagnottes() -> list[Cagnotte]:
    rows = data.select_cagnottes()
    return [Cagnotte(id=row.id, nom=row.nom) for row in rows]


def obtenir_cagnotte(cagnotte_id: uuid.UUID) -> Optional[Cagnotte]:
    row = data.select_cagnotte(cagnotte_id)
    if row is None:
        return None
    return Cagnotte(id=row.id, nom=row.nom)


# ---------------------------------------------------------------------------
# Dépenses
# ---------------------------------------------------------------------------

def ajouter_depense(
    cagnotte_id: uuid.UUID,
    participant: str,
    montant: float,
    date_paiement: date,
) -> Depense:
    existing = data.select_depense_by_participant(cagnotte_id, participant)
    if existing is not None:
        raise ValueError(
            f"Le participant '{participant}' a déjà une dépense dans cette cagnotte."
        )

    new_id = uuid.uuid4()
    data.insert_depense(new_id, cagnotte_id, participant, montant, str(date_paiement))
    return Depense(
        id=new_id,
        cagnotte_id=cagnotte_id,
        participant=participant,
        montant=montant,
        date_paiement=date_paiement,
    )


def supprimer_depense(depense_id: uuid.UUID) -> None:
    data.delete_depense(depense_id)


def lister_depenses(cagnotte_id: uuid.UUID) -> list[Depense]:
    rows = data.select_depenses(cagnotte_id)
    return [
        Depense(
            id=row.id,
            cagnotte_id=row.cagnotte_id,
            participant=row.participant,
            montant=row.montant,
            date_paiement=row.date_paiement,
        )
        for row in rows
    ]


# ---------------------------------------------------------------------------
# Calcul "qui doit à qui"
# ---------------------------------------------------------------------------

def calculer_remboursements(cagnotte_id: uuid.UUID) -> list[Remboursement]:
    depenses = lister_depenses(cagnotte_id)
    if not depenses:
        return []

    total = sum(d.montant for d in depenses)
    participants = list({d.participant for d in depenses})
    part = total / len(participants)

    soldes: dict[str, float] = {p: 0.0 for p in participants}
    for d in depenses:
        soldes[d.participant] += d.montant
    for p in participants:
        soldes[p] -= part

    creanciers = sorted(
        [(p, s) for p, s in soldes.items() if s > 0.001], key=lambda x: -x[1]
    )
    debiteurs = sorted(
        [(p, -s) for p, s in soldes.items() if s < -0.001], key=lambda x: -x[1]
    )

    remboursements: list[Remboursement] = []
    i, j = 0, 0
    while i < len(creanciers) and j < len(debiteurs):
        creancier, avoir = creanciers[i]
        debiteur, dette = debiteurs[j]
        montant = min(avoir, dette)
        remboursements.append(
            Remboursement(debiteur=debiteur, creancier=creancier, montant=round(montant, 2))
        )
        creanciers[i] = (creancier, avoir - montant)
        debiteurs[j] = (debiteur, dette - montant)
        if creanciers[i][1] < 0.001:
            i += 1
        if debiteurs[j][1] < 0.001:
            j += 1

    return remboursements
