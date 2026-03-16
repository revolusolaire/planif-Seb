# CLAUDE.md — AI Assistant Guide for planif-Seb

This file provides context, conventions, and workflows for AI assistants (Claude Code and similar tools) working on this repository. Keep it updated as the project evolves.

---

## Project Overview

**planif-Seb** is an automated lead management system. When a new lead is added to a Google Sheet, the system automatically sends a welcome SMS and initiates an AI voice call via Twilio.

**Stack**: Node.js, Express, Twilio (SMS + Voice), Make/Zapier (Google Sheets trigger)

> **Status**: Initial implementation complete — webhook server with SMS and AI voice call.

---

## Repository Structure

```
planif-Seb/
├── CLAUDE.md               # This file — AI assistant guide
├── .env.example            # Required environment variables (template)
├── package.json
└── src/
    ├── server.js           # Express app entry point
    ├── routes/
    │   ├── webhook.js      # POST /webhook/lead — receives lead, triggers SMS + call
    │   └── twiml.js        # GET /twiml/welcome — returns TwiML XML for voice call
    └── services/
        ├── sms.js          # Sends welcome SMS via Twilio
        └── voice.js        # Initiates outbound voice call via Twilio
```

---

## Git Workflow

### Branches
- **`main`** — production-ready code only; never commit directly
- **`develop`** — integration branch; merge feature branches here
- **`claude/<ticket-or-description>`** — AI-assisted work branches
- **`feature/<description>`** — human-led feature branches
- **`fix/<description>`** — bug fix branches

### Commit Convention
Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short description>

[optional body]
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`

Examples:
```
feat(planning): add weekly schedule view
fix(auth): handle token expiry edge case
docs: update CLAUDE.md with project structure
```

### Push Protocol
```bash
git push -u origin <branch-name>
```
- Branch names for AI sessions must follow: `claude/<session-suffix>`
- Never force-push to `main` or `develop`

---

## Development Workflows

### Starting Work
1. Pull latest from the base branch
2. Create a feature/fix branch with a descriptive name
3. Make focused, atomic commits
4. Open a PR against `develop` (or `main` for hotfixes)

### Before Committing
- Run linter and formatter
- Run tests and ensure they pass
- Do not commit secrets, credentials, or `.env` files

### PR Guidelines
- Keep PRs small and focused
- Include a summary of changes in the PR description
- Reference related issues when applicable

---

## Coding Conventions

These will be refined once the tech stack is chosen. General principles:

### General
- Write self-documenting code; comments explain *why*, not *what*
- Prefer explicit over implicit
- Keep functions small and single-purpose
- Handle errors explicitly; do not swallow exceptions silently
- Validate at system boundaries (user input, external APIs), trust internal code

### Security
- Never commit secrets, API keys, or credentials
- Use environment variables for all configuration that varies by environment
- Validate and sanitize all user input
- Follow OWASP Top 10 guidelines

### Testing
- Write tests alongside new features (not as an afterthought)
- Prefer unit tests for business logic, integration tests for API/DB interactions
- Aim for meaningful coverage, not 100% coverage for its own sake

---

## Environment Configuration

Use a `.env` file for local development (never commit it). Provide a `.env.example` with all required keys and placeholder values.

```bash
cp .env.example .env
# Fill in your local values
```

---

## AI Assistant Instructions

When working on this codebase as an AI assistant:

1. **Read before editing** — always read existing files before modifying them
2. **Minimal changes** — only change what is necessary for the task; avoid unasked-for refactors
3. **No over-engineering** — prefer simple, direct solutions over elaborate abstractions
4. **No invented URLs** — never guess or fabricate URLs; use only those explicitly provided
5. **Confirm destructive actions** — ask before deleting files, dropping data, or force-pushing
6. **Update this file** — when project structure, stack, or conventions change, update CLAUDE.md
7. **Use conventional commits** — all commits must follow the convention above
8. **Stay on assigned branch** — push only to the branch designated for the current session

### Setup and Run

```bash
npm install
cp .env.example .env
# Remplir les valeurs dans .env
node src/server.js
```

### Test local

```bash
# Tester le webhook (nouveau lead)
curl -X POST http://localhost:3000/webhook/lead \
  -H "Content-Type: application/json" \
  -d '{"nom":"Jean Dupont","telephone":"+15141234567","email":"jean@example.com"}'

# Tester le TwiML vocal
curl http://localhost:3000/twiml/welcome?nom=Jean
```

### Variables d'environnement requises

| Variable | Description |
|---|---|
| `PORT` | Port du serveur (défaut: 3000) |
| `TWILIO_ACCOUNT_SID` | SID du compte Twilio |
| `TWILIO_AUTH_TOKEN` | Token d'authentification Twilio |
| `TWILIO_PHONE_NUMBER` | Numéro Twilio expéditeur (format E.164) |
| `BASE_URL` | URL publique du serveur pour le callback TwiML |

### Déploiement

Déployer sur Railway, Render, ou tout serveur Node.js. Configurer `BASE_URL` avec l'URL publique, puis mettre à jour Make/Zapier avec cette URL.

### Configuration Make/Zapier

- **Trigger** : Google Sheets → "New Spreadsheet Row"
- **Action** : Webhooks → POST vers `https://votre-domaine.com/webhook/lead`
- **Body JSON** :
  ```json
  { "nom": "{{Nom}}", "telephone": "{{Téléphone}}", "email": "{{Email}}" }
  ```

### What to update in this file as the project grows
- [ ] Test commands (unit/integration)
- [ ] Linting/formatting setup
- [ ] Deployment process details
