import os

from sqlalchemy import create_engine, Column, CheckConstraint, String, Integer
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DB_PATH = os.environ.get("DB_PATH", "data.db")

db_dir = os.path.dirname(DB_PATH)
if db_dir:
    os.makedirs(db_dir, exist_ok=True)

# Le moteur : il sait parler à CETTE base (ici un fichier SQLite).
engine = create_engine(f"sqlite:///{DB_PATH}")

# Session : la "poignée" par laquelle on lit/écrit. On en ouvre une par requête.
Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    """Classe de base commune à tous vos modèles."""

class Compte(Base):
    __tablename__ = 'comptes'

    pseudo = Column(String, primary_key=True)
    solde = Column(Integer, default=0, nullable=False)

    __table_args__ = (
        CheckConstraint('solde >= 0', name='check_solde_positif'),
    )

def init():
    """Crée les tables si elles n'existent pas. À APPELER au démarrage."""
    Base.metadata.create_all(engine)