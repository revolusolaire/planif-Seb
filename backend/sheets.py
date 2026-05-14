"""
Synchronisation Google Sheets → CRM
Lit les leads depuis un ou plusieurs Google Sheets et les insère en base.
"""
import os
import json
import logging
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from sqlalchemy.orm import Session
from database import Lead

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# IDs des Google Sheets à surveiller (séparés par virgule dans .env)
# Format: SHEET_ID_1,SHEET_ID_2
SHEET_IDS = os.getenv("GOOGLE_SHEET_IDS", "").split(",")

# Chemin vers le fichier credentials JSON du compte de service Google
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "google_credentials.json")

# Mapping des colonnes du sheet (adapter selon la structure réelle)
# Clé = nom du champ interne, Valeur = nom de la colonne dans le sheet (insensible à la casse)
COLUMN_MAP = {
    "prenom": os.getenv("COL_PRENOM", "Prénom"),
    "nom": os.getenv("COL_NOM", "Nom"),
    "telephone": os.getenv("COL_TEL", "N° de tel"),
    "email": os.getenv("COL_EMAIL", "Email"),
    "campagne": os.getenv("COL_CAMPAGNE", ""),
    "entreprise": os.getenv("COL_ENTREPRISE", "Entreprise"),
    "demande": os.getenv("COL_DEMANDE", "Demande"),
    "horaires_rappel": os.getenv("COL_HORAIRES", "Horaires pour rappel"),
    "remarques": os.getenv("COL_REMARQUES", "Remarques"),
}


def get_sheets_service():
    if not os.path.exists(CREDENTIALS_FILE):
        raise FileNotFoundError(
            f"Fichier credentials Google introuvable : {CREDENTIALS_FILE}\n"
            "Dépose ton fichier google_credentials.json dans le dossier backend/"
        )
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)


def lire_sheet(service, sheet_id: str) -> list[dict]:
    """Retourne toutes les lignes d'un sheet sous forme de liste de dicts."""
    try:
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=sheet_id, range="A:Z")
            .execute()
        )
        rows = result.get("values", [])
        if not rows:
            return []

        headers = [h.strip() for h in rows[0]]
        leads = []
        for row in rows[1:]:
            # Compléter les cellules vides
            while len(row) < len(headers):
                row.append("")
            leads.append(dict(zip(headers, row)))
        return leads
    except Exception as e:
        logger.error(f"Erreur lecture sheet {sheet_id}: {e}")
        return []


def normaliser_telephone(tel: str) -> str:
    """Normalise le numéro : retire espaces, tirets, points."""
    return "".join(c for c in tel if c.isdigit() or c == "+")


def extraire_champ(row: dict, nom_colonne: str) -> str:
    """Cherche un champ dans la ligne (insensible à la casse)."""
    nom_lower = nom_colonne.lower()
    for key, val in row.items():
        if key.lower() == nom_lower:
            return str(val).strip()
    return ""


def sync_leads(db: Session, nouvelles_alertes_callback=None) -> int:
    """
    Synchronise tous les sheets configurés.
    Retourne le nombre de nouveaux leads insérés.
    """
    if not any(SHEET_IDS):
        logger.warning("Aucun GOOGLE_SHEET_IDS configuré dans .env")
        return 0

    try:
        service = get_sheets_service()
    except FileNotFoundError as e:
        logger.warning(str(e))
        return 0

    nouveaux = 0

    for sheet_id in SHEET_IDS:
        sheet_id = sheet_id.strip()
        if not sheet_id:
            continue

        lignes = lire_sheet(service, sheet_id)
        for row in lignes:
            tel_brut = extraire_champ(row, COLUMN_MAP["telephone"])
            if not tel_brut:
                continue

            telephone = normaliser_telephone(tel_brut)
            if not telephone:
                continue

            # Vérifier si ce lead existe déjà
            existant = db.query(Lead).filter(Lead.telephone == telephone).first()
            if existant:
                continue

            lead = Lead(
                prenom=extraire_champ(row, COLUMN_MAP["prenom"]),
                nom=extraire_champ(row, COLUMN_MAP["nom"]),
                telephone=telephone,
                email=extraire_champ(row, COLUMN_MAP["email"]),
                campagne=extraire_champ(row, COLUMN_MAP["campagne"]),
                entreprise=extraire_champ(row, COLUMN_MAP["entreprise"]),
                demande=extraire_champ(row, COLUMN_MAP["demande"]),
                horaires_rappel=extraire_champ(row, COLUMN_MAP["horaires_rappel"]),
                remarques=extraire_champ(row, COLUMN_MAP["remarques"]),
                source_sheet=sheet_id,
                date_arrivee=datetime.utcnow(),
                statut="Nouveau",
                donnees_brutes=json.dumps(row, ensure_ascii=False),
            )
            db.add(lead)
            db.commit()
            db.refresh(lead)
            nouveaux += 1
            logger.info(f"Nouveau lead: {lead.prenom} {lead.nom} ({lead.telephone})")

            if nouvelles_alertes_callback:
                nouvelles_alertes_callback(lead)

    return nouveaux
