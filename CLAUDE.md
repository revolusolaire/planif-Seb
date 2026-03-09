# CLAUDE.md — AI Assistant Guide for planif-Seb

This file provides context, conventions, and workflows for AI assistants (Claude Code and similar tools) working on this repository. Keep it updated as the project evolves.

---

## Project Overview

**planif-Seb** is a planning/scheduling application (French: *planification*). This file will be updated once the project's stack, purpose, and architecture are established.

> **Status**: Repository initialized — no source code committed yet. Update this file after bootstrapping the project.

---

## Repository Structure

```
planif-Seb/
├── CLAUDE.md          # This file — AI assistant guide
└── (project files)    # To be added
```

Update this tree whenever significant directories or files are added.

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
