"""
CRM RevoluSolaire — API principale
"""
import os
import logging
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv

load_dotenv()

from database import init_db, get_db, Lead, Appel
from scheduler import demarrer_scheduler
from sheets import sync_leads
from notifications import notifier_nouveau_lead

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    scheduler = demarrer_scheduler()
    # Première sync au démarrage
    db = next(get_db())
    try:
        sync_leads(db, nouvelles_alertes_callback=notifier_nouveau_lead)
    finally:
        db.close()
    yield
    scheduler.shutdown()


app = FastAPI(title="CRM RevoluSolaire", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir le frontend
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


# ─── Schémas Pydantic ───────────────────────────────────────────────────────


class LeadUpdate(BaseModel):
    statut: Optional[str] = None
    prenom: Optional[str] = None
    nom: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None


class AppelCreate(BaseModel):
    lead_id: int
    resultat: str
    notes: Optional[str] = ""
    duree_minutes: Optional[int] = 0


# ─── Routes ─────────────────────────────────────────────────────────────────


@app.get("/")
def index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/lead/{lead_id}")
def lead_page(lead_id: int):
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    """Compteurs du tableau de bord."""
    total = db.query(Lead).count()
    nouveaux = db.query(Lead).filter(Lead.statut == "Nouveau").count()
    a_rappeler = db.query(Lead).filter(Lead.statut == "À rappeler").count()
    rdv = db.query(Lead).filter(Lead.statut == "Rendez-vous").count()
    signes = db.query(Lead).filter(Lead.statut == "Signé").count()
    perdus = db.query(Lead).filter(Lead.statut == "Perdu").count()
    return {
        "total": total,
        "nouveaux": nouveaux,
        "a_rappeler": a_rappeler,
        "rendez_vous": rdv,
        "signes": signes,
        "perdus": perdus,
    }


@app.get("/api/leads")
def list_leads(
    statut: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(100),
    offset: int = Query(0),
    db: Session = Depends(get_db),
):
    """Liste des leads avec filtres optionnels."""
    q = db.query(Lead)
    if statut:
        q = q.filter(Lead.statut == statut)
    if search:
        terme = f"%{search}%"
        q = q.filter(
            Lead.prenom.ilike(terme)
            | Lead.nom.ilike(terme)
            | Lead.telephone.ilike(terme)
            | Lead.email.ilike(terme)
        )
    total = q.count()
    leads = q.order_by(Lead.date_arrivee.desc()).offset(offset).limit(limit).all()

    maintenant = datetime.utcnow()
    result = []
    for l in leads:
        delta_sec = int((maintenant - l.date_arrivee).total_seconds())
        result.append(
            {
                "id": l.id,
                "prenom": l.prenom,
                "nom": l.nom,
                "telephone": l.telephone,
                "email": l.email,
                "campagne": l.campagne,
                "statut": l.statut,
                "date_arrivee": l.date_arrivee.isoformat(),
                "delta_secondes": delta_sec,
                "email_relance_envoye": l.email_relance_envoye,
            }
        )
    return {"total": total, "leads": result}


@app.get("/api/leads/{lead_id}")
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead introuvable")
    appels = db.query(Appel).filter(Appel.lead_id == lead_id).order_by(Appel.date_appel.desc()).all()
    maintenant = datetime.utcnow()
    delta_sec = int((maintenant - lead.date_arrivee).total_seconds())
    return {
        "id": lead.id,
        "prenom": lead.prenom,
        "nom": lead.nom,
        "telephone": lead.telephone,
        "email": lead.email,
        "campagne": lead.campagne,
        "source_sheet": lead.source_sheet,
        "statut": lead.statut,
        "date_arrivee": lead.date_arrivee.isoformat(),
        "delta_secondes": delta_sec,
        "email_relance_envoye": lead.email_relance_envoye,
        "donnees_brutes": lead.donnees_brutes,
        "appels": [
            {
                "id": a.id,
                "date_appel": a.date_appel.isoformat(),
                "resultat": a.resultat,
                "notes": a.notes,
                "duree_minutes": a.duree_minutes,
            }
            for a in appels
        ],
    }


@app.patch("/api/leads/{lead_id}")
def update_lead(lead_id: int, data: LeadUpdate, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead introuvable")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(lead, field, value)
    db.commit()
    return {"ok": True}


@app.post("/api/appels")
def creer_appel(data: AppelCreate, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == data.lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead introuvable")

    appel = Appel(
        lead_id=data.lead_id,
        resultat=data.resultat,
        notes=data.notes,
        duree_minutes=data.duree_minutes,
        date_appel=datetime.utcnow(),
    )
    db.add(appel)

    # Mettre à jour le statut du lead selon le résultat
    STATUT_MAP = {
        "Pas répondu": "Pas répondu",
        "Messagerie": "À rappeler",
        "Mauvais numéro": "Perdu",
        "Rappeler": "À rappeler",
        "Intéressé": "Appelé",
        "RDV pris": "Rendez-vous",
        "Pas intéressé": "Perdu",
    }
    if data.resultat in STATUT_MAP:
        lead.statut = STATUT_MAP[data.resultat]

    db.commit()
    return {"ok": True, "appel_id": appel.id, "nouveau_statut": lead.statut}


@app.post("/api/sync")
def sync_manuel(db: Session = Depends(get_db)):
    """Déclenche une synchronisation manuelle des Google Sheets."""
    nb = sync_leads(db, nouvelles_alertes_callback=notifier_nouveau_lead)
    return {"nouveaux_leads": nb}
