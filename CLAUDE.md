# CLAUDE.md — AI Assistant Guide for planif-Seb

This file provides context, conventions, and workflows for AI assistants (Claude Code and similar tools) working on this repository. Keep it updated as the project evolves.

---

## Project Overview

**planif-Seb** est un CRM de suivi de leads pour les campagnes publicitaires Meta (Facebook/Instagram) de **RevoluSolaire** (volets solaires). Il synchronise automatiquement les leads depuis Google Sheets, envoie des alertes Telegram, relance par email, et fournit une interface web de suivi complet.

---

## Tech Stack

- **Backend** : Python 3.11+ · FastAPI · SQLAlchemy · SQLite · APScheduler
- **Frontend** : HTML/CSS/JS vanilla (pas de build nécessaire)
- **Intégrations** : Google Sheets API v4 · Telegram Bot API · Gmail SMTP
- **Hébergement** : VPS `72.62.233.55:58645`

---

## Repository Structure

```
planif-Seb/
├── CLAUDE.md               # Ce fichier
├── .env.example            # Template de configuration
├── start.sh                # Script de démarrage
├── backend/
│   ├── main.py             # API FastAPI + serveur frontend
│   ├── database.py         # Modèles SQLAlchemy (Lead, Appel)
│   ├── sheets.py           # Sync Google Sheets → CRM
│   ├── notifications.py    # Alertes Telegram
│   ├── email_service.py    # Emails de relance (Gmail SMTP)
│   ├── scheduler.py        # Tâches planifiées (sync, rappels, emails)
│   └── requirements.txt
└── frontend/
    ├── index.html          # Dashboard CRM
    ├── style.css
    └── app.js
```

## Setup & Run

```bash
# 1. Copier et configurer l'environnement
cp .env.example backend/.env
# Éditer backend/.env avec : TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID,
#   GOOGLE_SHEET_IDS, GOOGLE_CREDENTIALS_FILE, SMTP_PASSWORD

# 2. Déposer le fichier Google credentials
cp ton_fichier.json backend/google_credentials.json

# 3. Démarrer
./start.sh
```

L'app est accessible sur `http://72.62.233.55:58645`

## Workflow des leads

1. Google Sheets synchro toutes les **3 minutes**
2. Nouveau lead → alerte **Telegram immédiate**
3. Non contacté à **15 min** → rappel Telegram
4. Non contacté à **30 min** → rappel Telegram
5. Non contacté à **1h** → rappel Telegram (urgent)
6. Non contacté à **2h** → **email de relance automatique**

## Statuts CRM

`Nouveau` → `Appelé` | `Pas répondu` | `À rappeler` → `Rendez-vous` → `Signé` | `Perdu`

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

### What to update in this file as the project grows
- [ ] Project description and purpose
- [ ] Tech stack (language, framework, database)
- [ ] Repository directory tree
- [ ] Setup and run instructions
- [ ] Test commands
- [ ] Linting/formatting commands
- [ ] Deployment process
- [ ] Key architectural decisions and their rationale
