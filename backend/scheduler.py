"""
Tâches planifiées :
- Sync Google Sheets toutes les 3 minutes
- Rappels Telegram à 15 min, 30 min, 1h pour les leads non contactés
- Email de relance à 2h pour les leads sans action
"""
import logging
from datetime import datetime, timedelta, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from database import SessionLocal, Lead
from sheets import sync_leads
from notifications import notifier_nouveau_lead, notifier_rappel
from email_service import envoyer_relance_lead

logger = logging.getLogger(__name__)

STATUTS_CONTACTES = {"Appelé", "Rendez-vous", "Signé", "Perdu"}


def get_db() -> Session:
    return SessionLocal()


def tache_sync_sheets():
    """Sync Google Sheets et notifie les nouveaux leads."""
    db = get_db()
    try:
        nb = sync_leads(db, nouvelles_alertes_callback=notifier_nouveau_lead)
        if nb:
            logger.info(f"Sync Sheets : {nb} nouveau(x) lead(s)")
    except Exception as e:
        logger.error(f"Erreur sync sheets: {e}")
    finally:
        db.close()


def tache_rappels():
    """Vérifie les leads non contactés et envoie rappels + emails."""
    db = get_db()
    try:
        maintenant = datetime.now(timezone.utc).replace(tzinfo=None)
        # Leads toujours "Nouveau" ou "Pas répondu" — pas encore traités
        leads_actifs = (
            db.query(Lead)
            .filter(Lead.statut.notin_(STATUTS_CONTACTES))
            .all()
        )

        for lead in leads_actifs:
            arrivee = lead.date_arrivee
            delta = maintenant - arrivee

            # Rappel 15 min
            if delta >= timedelta(minutes=15) and not lead.alerte_15min_envoyee:
                notifier_rappel(lead, "15 min")
                lead.alerte_15min_envoyee = True
                db.commit()

            # Rappel 30 min
            if delta >= timedelta(minutes=30) and not lead.alerte_30min_envoyee:
                notifier_rappel(lead, "30 min")
                lead.alerte_30min_envoyee = True
                db.commit()

            # Rappel 1h
            if delta >= timedelta(hours=1) and not lead.alerte_1h_envoyee:
                notifier_rappel(lead, "1 heure")
                lead.alerte_1h_envoyee = True
                db.commit()

            # Email relance 2h
            if delta >= timedelta(hours=2) and not lead.email_relance_envoye:
                ok = envoyer_relance_lead(lead)
                lead.email_relance_envoye = True
                db.commit()
                if ok:
                    logger.info(f"Email relance envoyé — lead {lead.id}")

    except Exception as e:
        logger.error(f"Erreur tâche rappels: {e}")
    finally:
        db.close()


def demarrer_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    # Sync Google Sheets toutes les 3 minutes
    scheduler.add_job(tache_sync_sheets, "interval", minutes=3, id="sync_sheets")
    # Rappels toutes les minutes
    scheduler.add_job(tache_rappels, "interval", minutes=1, id="rappels")
    scheduler.start()
    logger.info("Scheduler démarré (sync toutes 3 min, rappels toutes 1 min)")
    return scheduler
