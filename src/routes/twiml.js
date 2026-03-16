const express = require('express');
const router = express.Router();

// GET /twiml/welcome?nom=Jean
// Endpoint appelé par Twilio lors de l'appel sortant.
// Retourne du XML TwiML qui fait lire un message de bienvenue vocal en français.
router.get('/welcome', (req, res) => {
  const nom = req.query.nom || 'cher client';

  // Polly.Lea est la voix neurale française canadienne d'Amazon (disponible via Twilio).
  // Alternatives FR : Polly.Celine (fr-FR), Polly.Mathieu (fr-FR)
  const twiml = `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say language="fr-FR" voice="Polly.Celine">
    Bonjour ${escapeXml(nom)}, bienvenue !
    Nous avons bien reçu votre demande et un conseiller vous contactera très prochainement.
    Merci de votre confiance et bonne journée.
  </Say>
</Response>`;

  res.type('text/xml').send(twiml);
});

function escapeXml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

module.exports = router;
