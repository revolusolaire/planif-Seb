"""
Notifications Telegram — alertes nouveaux leads et rappels d'appel.
"""
import os
import logging
import requests
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
APP_URL = os.getenv("APP_URL", "http://72.62.233.55:58645")


def envoyer_message(texte: str) -> bool:
    """Envoie un message Telegram. Retourne True si succès."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram non configuré (TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID manquants)")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": texte,
        "parse_mode": "HTML",
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Erreur envoi Telegram: {e}")
        return False


def notifier_nouveau_lead(lead) -> None:
    """Alerte immédiate à l'arrivée d'un nouveau lead."""
    heure = datetime.utcnow().strftime("%H:%M")
    nom_complet = f"{lead.prenom} {lead.nom}".strip() or "Inconnu"
    texte = (
        f"🔔 <b>NOUVEAU LEAD</b> — {heure}\n\n"
        f"👤 <b>{nom_complet}</b>\n"
        f"📞 <b>{lead.telephone}</b>\n"
        f"✉️ {lead.email or 'Email non renseigné'}\n"
        f"📣 Campagne : {lead.campagne or 'Non spécifiée'}\n\n"
        f"⏱️ <b>Appelez maintenant !</b>\n"
        f"🔗 <a href='{APP_URL}/lead/{lead.id}'>Ouvrir la fiche</a>"
    )
    envoyer_message(texte)


def notifier_rappel(lead, delai_label: str) -> None:
    """Rappel si le lead n'a toujours pas été appelé."""
    nom_complet = f"{lead.prenom} {lead.nom}".strip() or "Inconnu"
    arrivee = lead.date_arrivee.strftime("%H:%M")
    texte = (
        f"⚠️ <b>RAPPEL {delai_label}</b> — Lead non contacté\n\n"
        f"👤 <b>{nom_complet}</b>\n"
        f"📞 <b>{lead.telephone}</b>\n"
        f"🕐 Arrivé à {arrivee}\n\n"
        f"<b>Appelez immédiatement !</b>\n"
        f"🔗 <a href='{APP_URL}/lead/{lead.id}'>Ouvrir la fiche</a>"
    )
    envoyer_message(texte)
