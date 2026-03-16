const twilio = require('twilio');

const client = twilio(
  process.env.TWILIO_ACCOUNT_SID,
  process.env.TWILIO_AUTH_TOKEN
);

/**
 * Lance un appel vocal automatique vers le lead.
 * Twilio appellera l'endpoint /twiml/welcome pour obtenir le message à lire.
 * @param {string} nom - Prénom/nom du lead
 * @param {string} telephone - Numéro de téléphone au format E.164 (ex: +15141234567)
 */
async function initiateCall(nom, telephone) {
  const twimlUrl = `${process.env.BASE_URL}/twiml/welcome?nom=${encodeURIComponent(nom)}`;

  const call = await client.calls.create({
    from: process.env.TWILIO_PHONE_NUMBER,
    to: telephone,
    url: twimlUrl,
  });

  console.log(`Appel vocal initié vers ${telephone} — SID: ${call.sid}`);
  return call;
}

module.exports = { initiateCall };
