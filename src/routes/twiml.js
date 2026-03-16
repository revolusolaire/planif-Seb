const express = require('express');
const router = express.Router();
const { generateWelcomeAudio } = require('../services/elevenlabs');

// GET /twiml/welcome?nom=Jean
// Endpoint appelé par Twilio lors de l'appel sortant.
// Retourne du TwiML qui demande à Twilio de jouer l'audio généré par ElevenLabs.
router.get('/welcome', (req, res) => {
  const nom = req.query.nom || 'cher client';
  const audioUrl = `${process.env.BASE_URL}/twiml/audio?nom=${encodeURIComponent(nom)}`;

  const twiml = `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Play>${audioUrl}</Play>
</Response>`;

  res.type('text/xml').send(twiml);
});

// GET /twiml/audio?nom=Jean
// Génère et streame l'audio de bienvenue via ElevenLabs.
// Twilio télécharge ce fichier audio depuis <Play> dans le TwiML ci-dessus.
router.get('/audio', async (req, res) => {
  const nom = req.query.nom || 'cher client';

  try {
    const audioStream = await generateWelcomeAudio(nom);

    res.setHeader('Content-Type', 'audio/mpeg');
    audioStream.pipe(res);
  } catch (err) {
    console.error('Erreur ElevenLabs TTS :', err.message);
    res.status(500).send('Erreur lors de la génération audio.');
  }
});

module.exports = router;
