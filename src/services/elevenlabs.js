const { ElevenLabsClient } = require('@elevenlabs/elevenlabs-js');

const client = new ElevenLabsClient({
  apiKey: process.env.ELEVENLABS_API_KEY,
});

/**
 * Génère l'audio d'un message de bienvenue via ElevenLabs TTS.
 * Retourne un ReadableStream MP3 à piper directement dans la réponse HTTP.
 *
 * @param {string} nom - Prénom/nom du lead
 * @returns {Promise<ReadableStream>} Stream audio MP3
 */
async function generateWelcomeAudio(nom) {
  const text = `Bonjour ${nom}, bienvenue ! Nous avons bien reçu votre demande et un conseiller vous contactera très prochainement. Merci de votre confiance et bonne journée.`;

  // eleven_multilingual_v2 supporte le français nativement.
  // ELEVENLABS_VOICE_ID : ID de la voix choisie dans votre compte ElevenLabs.
  const audioStream = await client.textToSpeech.convert(
    process.env.ELEVENLABS_VOICE_ID,
    {
      text,
      model_id: 'eleven_multilingual_v2',
      output_format: 'mp3_44100_128',
    }
  );

  return audioStream;
}

module.exports = { generateWelcomeAudio };
