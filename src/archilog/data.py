import uuid
from datetime import date

from sqlalchemy import (
    Column,
    Date,
    Float,
    ForeignKey,
    MetaData,
    String,
    Table,
    Uuid,
    create_engine,
    delete,
    insert,
    select,
)

from archilog.config import config


engine = create_engine(config.DATABASE_URL, echo=config.DEBUG)

metadata = MetaData()

cagnottes_table = Table(
    "cagnottes",
    metadata,
    Column("id", Uuid, primary_key=True, default=uuid.uuid4),
    Column("nom", String, nullable=False),
)

depenses_table = Table(
    "depenses",
    metadata,
    Column("id", Uuid, primary_key=True, default=uuid.uuid4),
    Column("cagnotte_id", Uuid, ForeignKey("cagnottes.id"), nullable=False),
    Column("participant", String, nullable=False),
    Column("montant", Float, nullable=False),
    Column("date_paiement", Date, nullable=False),
)



def init_db() -> None:
    """Crée les tables si elles n'existent pas."""
    metadata.create_all(engine)



def insert_cagnotte(id: uuid.UUID, nom: str) -> None:
    stmt = insert(cagnottes_table).values(id=id, nom=nom)
    with engine.begin() as conn:
        conn.execute(stmt)


def select_cagnottes() -> list:
    stmt = select(cagnottes_table)
    with engine.connect() as conn:
        return conn.execute(stmt).fetchall()


def select_cagnotte(id: uuid.UUID):
    stmt = select(cagnottes_table).where(cagnottes_table.c.id == id)
    with engine.connect() as conn:
        return conn.execute(stmt).fetchone()


def delete_cagnotte(id: uuid.UUID) -> None:
    with engine.begin() as conn:
        conn.execute(
            delete(depenses_table).where(depenses_table.c.cagnotte_id == id)
        )
        conn.execute(
            delete(cagnottes_table).where(cagnottes_table.c.id == id)
        )



def insert_depense(
    id: uuid.UUID,
    cagnotte_id: uuid.UUID,
    participant: str,
    montant: float,
    date_paiement: str,
) -> None:
    stmt = insert(depenses_table).values(
        id=id,
        cagnotte_id=cagnotte_id,
        participant=participant,
        montant=montant,
        date_paiement=date.fromisoformat(date_paiement),
    )
    with engine.begin() as conn:
        conn.execute(stmt)


def select_depenses(cagnotte_id: uuid.UUID) -> list:
    stmt = select(depenses_table).where(depenses_table.c.cagnotte_id == cagnotte_id)
    with engine.connect() as conn:
        return conn.execute(stmt).fetchall()


def select_depense_by_participant(cagnotte_id: uuid.UUID, participant: str):
    stmt = select(depenses_table).where(
        (depenses_table.c.cagnotte_id == cagnotte_id)
        & (depenses_table.c.participant == participant)
    )
    with engine.connect() as conn:
        return conn.execute(stmt).fetchone()


def delete_depense(id: uuid.UUID) -> None:
    stmt = delete(depenses_table).where(depenses_table.c.id == id)
    with engine.begin() as conn:
        conn.execute(stmt)
