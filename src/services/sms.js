const twilio = require('twilio');

const client = twilio(
  process.env.TWILIO_ACCOUNT_SID,
  process.env.TWILIO_AUTH_TOKEN
);

/**
 * Envoie un SMS de bienvenue au nouveau lead.
 * @param {string} nom - Prénom/nom du lead
 * @param {string} telephone - Numéro de téléphone au format E.164 (ex: +15141234567)
 */
async function sendWelcome(nom, telephone) {
  const message = await client.messages.create({
    from: process.env.TWILIO_PHONE_NUMBER,
    to: telephone,
    body: `Bonjour ${nom} ! 👋 Merci pour votre intérêt. Nous avons bien reçu votre demande et vous serez contacté(e) très prochainement par notre équipe. À bientôt !`,
  });

  console.log(`SMS envoyé à ${telephone} — SID: ${message.sid}`);
  return message;
}

module.exports = { sendWelcome };
