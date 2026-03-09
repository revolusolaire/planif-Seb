/* CRM RevoluSolaire — Frontend */

const API = '';  // même origine

let leads = [];
let timerInterval = null;
let debounceTimer = null;
let leadOuvert = null;

// ── Initialisation ──────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  chargerStats();
  chargerLeads();
  // Rafraîchissement automatique toutes les 60 secondes
  setInterval(() => {
    chargerStats();
    chargerLeads();
  }, 60000);
  // Mise à jour des chronomètres toutes les secondes
  timerInterval = setInterval(mettreAJourTimers, 1000);

  // Si URL = /lead/ID, ouvrir directement la fiche
  const m = window.location.pathname.match(/^\/lead\/(\d+)/);
  if (m) ouvrirFiche(parseInt(m[1]));
});

// ── Stats ───────────────────────────────────────────────────────

async function chargerStats() {
  try {
    const data = await apiFetch('/api/stats');
    document.getElementById('stat-total').textContent    = data.total;
    document.getElementById('stat-nouveaux').textContent = data.nouveaux;
    document.getElementById('stat-rappeler').textContent = data.a_rappeler;
    document.getElementById('stat-rdv').textContent      = data.rendez_vous;
    document.getElementById('stat-signes').textContent   = data.signes;
    document.getElementById('stat-perdus').textContent   = data.perdus;
  } catch(e) { console.error('Stats:', e); }
}

// ── Leads ───────────────────────────────────────────────────────

async function chargerLeads() {
  const statut = document.getElementById('filtre-statut').value;
  const search = document.getElementById('search-input').value;
  let url = '/api/leads?limit=200';
  if (statut) url += `&statut=${encodeURIComponent(statut)}`;
  if (search) url += `&search=${encodeURIComponent(search)}`;
  try {
    const data = await apiFetch(url);
    leads = data.leads;
    renderLeads();
  } catch(e) { console.error('Leads:', e); }
}

function renderLeads() {
  const tbody = document.getElementById('leads-tbody');
  if (!leads.length) {
    tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;padding:30px;color:#aaa;">Aucun lead</td></tr>';
    return;
  }
  tbody.innerHTML = leads.map(l => `
    <tr id="row-${l.id}">
      <td><strong>${echap(l.prenom)} ${echap(l.nom)}</strong></td>
      <td><a href="tel:${echap(l.telephone)}">${echap(l.telephone)}</a></td>
      <td>${l.email ? `<a href="mailto:${echap(l.email)}">${echap(l.email)}</a>` : '<span style="color:#bbb">—</span>'}</td>
      <td>${echap(l.campagne) || '<span style="color:#bbb">—</span>'}</td>
      <td style="white-space:nowrap;font-size:13px;">${formatDateHeure(l.date_arrivee)}</td>
      <td><span class="timer ${timerClass(l.delta_secondes)}" data-arrived="${l.date_arrivee}">${formatTimer(l.delta_secondes)}</span></td>
      <td><span class="badge ${badgeClass(l.statut)}">${echap(l.statut)}</span></td>
      <td>
        <button class="btn btn-primary btn-sm" onclick="ouvrirFiche(${l.id})">Ouvrir</button>
        <a class="btn btn-success btn-sm" href="tel:${echap(l.telephone)}">📞</a>
      </td>
    </tr>
  `).join('');
}

function mettreAJourTimers() {
  document.querySelectorAll('.timer[data-arrived]').forEach(el => {
    const arrived = new Date(el.dataset.arrived + 'Z');
    const delta = Math.floor((Date.now() - arrived.getTime()) / 1000);
    el.textContent = formatTimer(delta);
    el.className = `timer ${timerClass(delta)}`;
  });
}

// ── Filtres ─────────────────────────────────────────────────────

function filtrerStatut(statut) {
  document.getElementById('filtre-statut').value = statut;
  chargerLeads();
}

function rechercherDebounce() {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(chargerLeads, 350);
}

// ── Export CSV ──────────────────────────────────────────────────

function exporterCSV() {
  const statut = document.getElementById('filtre-statut').value;
  const search = document.getElementById('search-input').value;
  let url = '/api/leads/export?';
  if (statut) url += `statut=${encodeURIComponent(statut)}&`;
  if (search) url += `search=${encodeURIComponent(search)}&`;
  window.location.href = url;
}

function exporterJSON() {
  const statut = document.getElementById('filtre-statut').value;
  const search = document.getElementById('search-input').value;
  let url = '/api/leads/export/json?';
  if (statut) url += `statut=${encodeURIComponent(statut)}&`;
  if (search) url += `search=${encodeURIComponent(search)}&`;
  window.location.href = url;
}

// ── Sync manuel ─────────────────────────────────────────────────

async function syncManuel() {
  const btn = document.getElementById('btn-sync');
  const status = document.getElementById('sync-status');
  btn.disabled = true;
  btn.textContent = '⏳ Sync…';
  try {
    const data = await apiFetch('/api/sync', { method: 'POST' });
    status.textContent = `✓ ${data.nouveaux_leads} nouveau(x) lead(s)`;
    chargerStats();
    chargerLeads();
  } catch(e) {
    status.textContent = '✗ Erreur';
  }
  btn.disabled = false;
  btn.textContent = '🔄 Sync maintenant';
  setTimeout(() => { status.textContent = ''; }, 5000);
}

// ── Modal fiche lead ─────────────────────────────────────────────

async function ouvrirFiche(id) {
  leadOuvert = id;
  const overlay = document.getElementById('modal-overlay');
  document.getElementById('modal-content').innerHTML = '<p style="padding:20px;text-align:center;">Chargement…</p>';
  overlay.classList.remove('hidden');
  await rafraichirFiche(id);
}

async function rafraichirFiche(id) {
  try {
    const l = await apiFetch(`/api/leads/${id}`);
    const delta = Math.floor((Date.now() - new Date(l.date_arrivee + 'Z').getTime()) / 1000);
    const appelsHtml = l.appels.length
      ? l.appels.map(a => `
          <div class="appel-item resultat-${cssClass(a.resultat)}">
            <div class="appel-item-header">
              <span class="appel-item-resultat">${echap(a.resultat)}</span>
              <span class="appel-item-date">${formatDateHeure(a.date_appel)}${a.duree_minutes ? ` · ${a.duree_minutes} min` : ''}</span>
            </div>
            ${a.notes ? `<div class="appel-item-notes">${echap(a.notes)}</div>` : ''}
          </div>`).join('')
      : '<p style="color:#bbb;font-size:14px;">Aucun appel enregistré</p>';

    document.getElementById('modal-content').innerHTML = `
      <div class="fiche-header">
        <h2>${echap(l.prenom)} ${echap(l.nom)}</h2>
        <div class="fiche-meta">Lead #${l.id} · Arrivé le ${formatDateHeure(l.date_arrivee)} · <strong class="${timerClass(delta)}">${formatTimer(delta)}</strong> depuis l'arrivée</div>
      </div>

      <div class="fiche-grid">
        <div class="fiche-field">
          <label>Téléphone</label>
          <span><a href="tel:${echap(l.telephone)}">${echap(l.telephone)}</a></span>
        </div>
        <div class="fiche-field">
          <label>Email</label>
          <span>${l.email ? `<a href="mailto:${echap(l.email)}">${echap(l.email)}</a>` : '—'}</span>
        </div>
        <div class="fiche-field">
          <label>Entreprise</label>
          <span>${echap(l.entreprise) || '—'}</span>
        </div>
        <div class="fiche-field">
          <label>Statut actuel</label>
          <span class="badge ${badgeClass(l.statut)}">${echap(l.statut)}</span>
        </div>
        <div class="fiche-field">
          <label>Demande</label>
          <span>${echap(l.demande) || '—'}</span>
        </div>
        <div class="fiche-field">
          <label>Horaires pour rappel</label>
          <span>${echap(l.horaires_rappel) || '—'}</span>
        </div>
        <div class="fiche-field">
          <label>Email relance auto</label>
          <span>${l.email_relance_envoye ? '✅ Envoyé' : '⏳ Pas encore'}</span>
        </div>
        <div class="fiche-field">
          <label>Campagne</label>
          <span>${echap(l.campagne) || '—'}</span>
        </div>
      </div>
      ${l.remarques ? `<div style="background:#fffbeb;border-left:4px solid #f59e0b;padding:10px 14px;border-radius:6px;margin-bottom:16px;font-size:14px;"><strong>Remarques :</strong> ${echap(l.remarques)}</div>` : ''}

      <div class="section-title">Changer le statut</div>
      <div class="statut-form">
        <select id="statut-select">
          ${['Nouveau','Appelé','Pas répondu','À rappeler','Rendez-vous','Signé','Perdu']
            .map(s => `<option value="${s}"${s===l.statut?' selected':''}>${s}</option>`).join('')}
        </select>
        <button class="btn btn-primary" onclick="changerStatut(${l.id})">Enregistrer</button>
      </div>

      <div class="section-title">Enregistrer un appel</div>
      <div class="appel-form">
        <select id="appel-resultat">
          <option value="">— Résultat de l'appel —</option>
          <option>Pas répondu</option>
          <option>Messagerie</option>
          <option>Mauvais numéro</option>
          <option>Rappeler</option>
          <option>Intéressé</option>
          <option>RDV pris</option>
          <option>Pas intéressé</option>
        </select>
        <div class="appel-form-row">
          <div>
            <label style="font-size:12px;color:#888;">Durée (min)</label>
            <input type="number" id="appel-duree" min="0" value="0" style="width:100%" />
          </div>
        </div>
        <textarea id="appel-notes" placeholder="Notes sur l'appel…"></textarea>
        <button class="btn btn-success" onclick="enregistrerAppel(${l.id})">💾 Enregistrer l'appel</button>
      </div>

      <div class="section-title">Historique des appels (${l.appels.length})</div>
      ${appelsHtml}
    `;
  } catch(e) {
    document.getElementById('modal-content').innerHTML = '<p style="color:red;">Erreur lors du chargement.</p>';
  }
}

async function changerStatut(id) {
  const statut = document.getElementById('statut-select').value;
  await apiFetch(`/api/leads/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ statut }),
  });
  chargerLeads();
  chargerStats();
  await rafraichirFiche(id);
}

async function enregistrerAppel(id) {
  const resultat = document.getElementById('appel-resultat').value;
  if (!resultat) { alert('Sélectionnez un résultat d\'appel.'); return; }
  const notes = document.getElementById('appel-notes').value;
  const duree = parseInt(document.getElementById('appel-duree').value) || 0;
  await apiFetch('/api/appels', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ lead_id: id, resultat, notes, duree_minutes: duree }),
  });
  chargerLeads();
  chargerStats();
  await rafraichirFiche(id);
}

function fermerModal(event) {
  if (event && event.target !== document.getElementById('modal-overlay')) return;
  document.getElementById('modal-overlay').classList.add('hidden');
  leadOuvert = null;
}

// ── Utilitaires ─────────────────────────────────────────────────

async function apiFetch(url, opts = {}) {
  const resp = await fetch(API + url, opts);
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  return resp.json();
}

function echap(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function formatTimer(seconds) {
  if (seconds < 60) return `${seconds}s`;
  if (seconds < 3600) return `${Math.floor(seconds/60)}m ${seconds%60}s`;
  const h = Math.floor(seconds/3600);
  const m = Math.floor((seconds%3600)/60);
  return `${h}h ${m}m`;
}

function timerClass(seconds) {
  if (seconds < 900) return 'timer-green';   // < 15 min
  if (seconds < 3600) return 'timer-orange'; // < 1h
  return 'timer-red';                         // ≥ 1h
}

function badgeClass(statut) {
  return 'badge badge-' + cssClass(statut);
}

function cssClass(str) {
  return (str || '').replace(/\s/g, '-').replace(/é/g,'é');
}

function formatDateHeure(iso) {
  if (!iso) return '—';
  const d = new Date(iso.endsWith('Z') ? iso : iso + 'Z');
  return d.toLocaleDateString('fr-FR') + ' ' + d.toLocaleTimeString('fr-FR', { hour:'2-digit', minute:'2-digit' });
}
