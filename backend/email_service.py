"""
Service d'email — relance automatique des leads après 2h sans contact.
"""
import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "revolusolaire@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")  # Mot de passe d'application Gmail
FROM_NAME = os.getenv("FROM_NAME", "RevoluSolaire")


def envoyer_email(destinataire: str, sujet: str, corps_html: str) -> bool:
    """Envoie un email HTML. Retourne True si succès."""
    if not SMTP_PASSWORD:
        logger.warning("SMTP_PASSWORD non configuré — email non envoyé.")
        return False
    if not destinataire or "@" not in destinataire:
        logger.warning(f"Email destinataire invalide : {destinataire}")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = sujet
    msg["From"] = f"{FROM_NAME} <{SMTP_USER}>"
    msg["To"] = destinataire
    msg.attach(MIMEText(corps_html, "html", "utf-8"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, destinataire, msg.as_string())
        logger.info(f"Email envoyé à {destinataire}")
        return True
    except Exception as e:
        logger.error(f"Erreur envoi email à {destinataire}: {e}")
        return False


def generer_email_relance(prenom: str, nom: str) -> tuple[str, str]:
    """Retourne (sujet, corps_html) pour l'email de relance volet solaire."""
    prenom_affiche = prenom if prenom else "Madame, Monsieur"
    sujet = "Votre projet de volets solaires — RevoluSolaire"
    corps = f"""
<!DOCTYPE html>
<html lang="fr">
<head><meta charset="UTF-8"></head>
<body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: auto; padding: 20px;">

  <div style="text-align: center; margin-bottom: 30px;">
    <h1 style="color: #f5a623; font-size: 24px;">RevoluSolaire</h1>
    <p style="color: #666; font-size: 14px;">Solutions en énergie solaire</p>
  </div>

  <p>Bonjour <strong>{prenom_affiche}</strong>,</p>

  <p>
    Nous avons bien reçu votre demande concernant un projet de <strong>volets solaires</strong>
    et nous vous en remercions chaleureusement.
  </p>

  <p>
    Notre équipe a essayé de vous joindre par téléphone afin de vous présenter
    nos solutions adaptées à votre situation. Nous souhaitons vous accompagner
    au mieux dans votre projet d'économie d'énergie.
  </p>

  <div style="background: #fff8ec; border-left: 4px solid #f5a623; padding: 15px; margin: 20px 0;">
    <p style="margin: 0; font-weight: bold;">Pourquoi choisir RevoluSolaire ?</p>
    <ul style="margin: 10px 0 0 0; padding-left: 20px;">
      <li>Installation rapide et professionnelle</li>
      <li>Économies sur votre facture d'énergie dès le premier mois</li>
      <li>Devis gratuit et sans engagement</li>
      <li>Accompagnement pour les aides et subventions disponibles</li>
    </ul>
  </div>

  <p>
    N'hésitez pas à nous rappeler au <strong>numéro indiqué sur notre site</strong>
    ou à répondre directement à cet email — nous reviendrons vers vous dans les plus brefs délais.
  </p>

  <p>Bien cordialement,</p>
  <p>
    <strong>L'équipe RevoluSolaire</strong><br>
    <a href="mailto:revolusolaire@gmail.com" style="color: #f5a623;">revolusolaire@gmail.com</a>
  </p>

  <hr style="border: none; border-top: 1px solid #eee; margin-top: 30px;">
  <p style="font-size: 11px; color: #aaa; text-align: center;">
    Vous recevez cet email car vous avez soumis une demande d'information via nos campagnes publicitaires.
  </p>

</body>
</html>
"""
    return sujet, corps


def envoyer_relance_lead(lead) -> bool:
    """Envoie l'email de relance pour un lead donné."""
    if not lead.email or "@" not in lead.email:
        logger.info(f"Lead {lead.id} sans email valide — relance email ignorée.")
        return False
    sujet, corps = generer_email_relance(lead.prenom, lead.nom)
    return envoyer_email(lead.email, sujet, corps)
