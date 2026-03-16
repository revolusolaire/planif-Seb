require('dotenv').config();
const express = require('express');
const webhookRouter = require('./routes/webhook');
const twimlRouter = require('./routes/twiml');

const app = express();
app.use(express.json());

app.use('/webhook', webhookRouter);
app.use('/twiml', twimlRouter);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Serveur de gestion des leads démarré sur le port ${PORT}`);
});
