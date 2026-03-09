from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./crm.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    # Identité
    prenom = Column(String, default="")
    nom = Column(String, default="")
    telephone = Column(String, unique=True, index=True)
    email = Column(String, default="")
    # Source
    source_sheet = Column(String, default="")  # nom du Google Sheet
    campagne = Column(String, default="")
    # Timing
    date_arrivee = Column(DateTime, default=datetime.utcnow)
    # Statut CRM
    statut = Column(String, default="Nouveau")
    # Nouveau | Appelé | Pas répondu | À rappeler | Rendez-vous | Signé | Perdu
    # Alertes
    alerte_15min_envoyee = Column(Boolean, default=False)
    alerte_30min_envoyee = Column(Boolean, default=False)
    alerte_1h_envoyee = Column(Boolean, default=False)
    email_relance_envoye = Column(Boolean, default=False)
    # Données brutes du sheet (JSON)
    donnees_brutes = Column(Text, default="{}")


class Appel(Base):
    __tablename__ = "appels"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, index=True)
    date_appel = Column(DateTime, default=datetime.utcnow)
    resultat = Column(String)
    # Pas répondu | Messagerie | Mauvais numéro | Rappeler | Intéressé | RDV pris | Pas intéressé
    notes = Column(Text, default="")
    duree_minutes = Column(Integer, default=0)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
