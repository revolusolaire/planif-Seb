const express = require('express');
const router = express.Router();
const smsService = require('../services/sms');
const voiceService = require('../services/voice');

// POST /webhook/lead
// Appelé par Make/Zapier quand un nouveau lead entre dans Google Sheets.
// Body attendu : { nom, telephone, email }
//
// Configuration Make/Zapier :
//   Trigger  : Google Sheets → "New Spreadsheet Row"
//   Action   : Webhooks → POST vers https://votre-domaine.com/webhook/lead
//   Body JSON: { "nom": "{{Nom}}", "telephone": "{{Téléphone}}", "email": "{{Email}}" }
router.post('/lead', async (req, res) => {
  const { nom, telephone, email } = req.body;

  if (!nom || !telephone) {
    return res.status(400).json({ error: 'Les champs "nom" et "telephone" sont requis.' });
  }

  try {
    await smsService.sendWelcome(nom, telephone);
    await voiceService.initiateCall(nom, telephone);

    console.log(`Lead traité : ${nom} (${telephone})`);
    res.status(200).json({ message: 'SMS et appel vocal initiés avec succès.' });
  } catch (err) {
    console.error('Erreur lors du traitement du lead :', err.message);
    res.status(500).json({ error: 'Erreur lors de l\'envoi du SMS ou de l\'appel.' });
  }
});

module.exports = router;
