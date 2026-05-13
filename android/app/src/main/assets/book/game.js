// game.js — moteur de jeu pour Les Jardins de Verre-Lune
(function () {
  'use strict';

  const STATE_KEY = 'verre-lune-state-v1';

  const SKILLS_LIST = [
    'Observation', 'Agilité', 'Discrétion', 'Soin des animaux',
    'Mémoire des légendes', 'Bricolage', 'Orientation'
  ];

  const STATE_KEYWORDS = ['FATIGUÉ', 'BLESSÉ LÉGER', 'ACCOMPAGNÉ'];
  const STATE_LABELS = {
    'FATIGUÉ': 'Fatigué',
    'BLESSÉ LÉGER': 'Blessé léger',
    'ACCOMPAGNÉ': 'Accompagné'
  };

  const DEFAULT_STATE = {
    skills: [],
    objects: [],
    keywords: [],
    currentSection: null,
    visitedSections: [],
    startedAt: null,
  };

  function loadState() {
    try {
      const raw = localStorage.getItem(STATE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        return Object.assign({}, DEFAULT_STATE, parsed);
      }
    } catch (e) { console.warn('localStorage indisponible :', e); }
    return JSON.parse(JSON.stringify(DEFAULT_STATE));
  }

  function saveState(state) {
    try {
      localStorage.setItem(STATE_KEY, JSON.stringify(state));
    } catch (e) { console.warn('Sauvegarde impossible :', e); }
  }

  function resetState() {
    try { localStorage.removeItem(STATE_KEY); } catch (e) {}
  }

  function hasState() {
    try {
      return !!localStorage.getItem(STATE_KEY);
    } catch (e) { return false; }
  }

  function listFromAttr(article, attr) {
    if (!article) return [];
    const v = article.getAttribute(attr);
    return v ? v.split('|').filter(Boolean) : [];
  }

  function applyGrants(article, state) {
    const objs = listFromAttr(article, 'data-grants-objects');
    const kws = listFromAttr(article, 'data-grants-keywords');
    const rmKws = listFromAttr(article, 'data-removes-keywords');
    objs.forEach(o => {
      if (!state.objects.includes(o)) state.objects.push(o);
    });
    kws.forEach(k => {
      if (!state.keywords.includes(k)) state.keywords.push(k);
    });
    rmKws.forEach(k => {
      state.keywords = state.keywords.filter(x => x !== k);
    });
  }

  function meetsRequirements(li, state) {
    const reqSkills = (li.getAttribute('data-requires-skill') || '').split('|').filter(Boolean);
    const reqObjs = (li.getAttribute('data-requires-object') || '').split('|').filter(Boolean);
    const reqKws = (li.getAttribute('data-requires-keyword') || '').split('|').filter(Boolean);
    if (reqSkills.length && !reqSkills.every(s => state.skills.includes(s))) return false;
    if (reqObjs.length && !reqObjs.every(o => state.objects.includes(o))) return false;
    if (reqKws.length && !reqKws.every(k => state.keywords.includes(k))) return false;
    return true;
  }

  function updateChoices(state) {
    document.querySelectorAll('ul.choices li').forEach(li => {
      const hasAnyReq = li.hasAttribute('data-requires-skill')
                     || li.hasAttribute('data-requires-object')
                     || li.hasAttribute('data-requires-keyword');
      if (!hasAnyReq) {
        li.classList.remove('locked');
        return;
      }
      if (meetsRequirements(li, state)) {
        li.classList.remove('locked');
      } else {
        li.classList.add('locked');
        li.querySelectorAll('a').forEach(a => {
          a.addEventListener('click', e => { e.preventDefault(); });
        });
      }
    });
  }

  function escapeHtml(s) {
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  function normalizeKeyword(s) {
    return String(s || '').trim().toUpperCase();
  }

  function isStateKeyword(k) {
    return STATE_KEYWORDS.includes(normalizeKeyword(k));
  }

  function emptySheetValue() {
    return '<em class="sheet-empty">aucun pour l\'instant</em>';
  }

  function leafIcon() {
    return '<span class="sheet-leaf" aria-hidden="true">'
      + '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">'
      + '<path d="M20 4c-9 0-15 5-15 12 0 2 1 4 3 4 7 0 12-6 12-16z"></path>'
      + '<path d="M5 20c4-6 8-9 13-12"></path>'
      + '</svg></span>';
  }

  function objectKindLabel(info) {
    if (!info || !info[0]) return '';
    return info[0] === 'principal' ? 'objet-clé' : 'secondaire';
  }

  function renderAdventureSheet(state, article) {
    const sheet = document.getElementById('adventure-sheet');
    if (!sheet) return;

    const sectionName = article ? article.getAttribute('data-section-name') : '';
    const context = document.getElementById('sheet-context');
    if (context) {
      context.textContent = sectionName || 'Aventure en cours';
    }

    const skills = document.getElementById('sheet-skills');
    if (skills) {
      skills.innerHTML = state.skills.length
        ? state.skills.map(s => '<span class="sheet-chip">' + escapeHtml(s) + '</span>').join('')
        : emptySheetValue();
    }

    const objects = document.getElementById('sheet-objects');
    if (objects) {
      const infos = window.OBJECT_INFO || {};
      objects.innerHTML = state.objects.length
        ? state.objects.map(o => {
            const kind = objectKindLabel(infos[o]);
            return '<div class="sheet-object">'
              + leafIcon()
              + '<span class="sheet-object-main">'
              + '<span class="sheet-object-name">' + escapeHtml(o) + '</span>'
              + (kind ? '<span class="sheet-object-kind">' + escapeHtml(kind) + '</span>' : '')
              + '</span>'
              + '</div>';
          }).join('')
        : emptySheetValue();
    }

    const keywords = document.getElementById('sheet-keywords');
    if (keywords) {
      const storyKeywords = state.keywords.filter(k => !isStateKeyword(k));
      keywords.innerHTML = storyKeywords.length
        ? storyKeywords.map(k => '<span class="sheet-keyword">' + escapeHtml(k) + '</span>').join('')
        : emptySheetValue();
    }

    const states = document.getElementById('sheet-states');
    if (states) {
      states.innerHTML = STATE_KEYWORDS.map(key => {
        const active = state.keywords.some(k => normalizeKeyword(k) === key);
        return '<span class="sheet-state' + (active ? ' is-active' : '') + '">'
          + '<span class="sheet-state-box" aria-hidden="true"></span>'
          + escapeHtml(STATE_LABELS[key])
          + '</span>';
      }).join('');
    }
  }

  function setupAdventureSheetControls() {
    const fab = document.querySelector('.fab-sheet');
    const layer = document.getElementById('adventure-sheet-layer');
    const sheet = document.getElementById('adventure-sheet');
    if (!fab || !layer || !sheet) return;

    let lastFocused = null;
    let closeTimer = null;

    function isOpen() {
      return !layer.hidden && layer.classList.contains('is-open');
    }

    function motionDelay(ms) {
      return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : ms;
    }

    function focusableElements() {
      return Array.from(sheet.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'))
        .filter(el => !el.disabled && el.getAttribute('aria-hidden') !== 'true');
    }

    function openSheet() {
      clearTimeout(closeTimer);
      lastFocused = document.activeElement;
      layer.hidden = false;
      sheet.setAttribute('aria-hidden', 'false');
      sheet.scrollTop = 0;
      document.body.classList.add('sheet-open');
      requestAnimationFrame(() => {
        layer.classList.add('is-open');
        const first = sheet.querySelector('.sheet-close') || sheet;
        first.focus();
      });
    }

    function closeSheet() {
      if (layer.hidden) return;
      layer.classList.remove('is-open');
      sheet.setAttribute('aria-hidden', 'true');
      document.body.classList.remove('sheet-open');
      closeTimer = setTimeout(() => {
        layer.hidden = true;
        if (lastFocused && document.contains(lastFocused)) lastFocused.focus();
      }, motionDelay(180));
    }

    fab.addEventListener('click', openSheet);
    layer.querySelectorAll('[data-sheet-close]').forEach(el => {
      el.addEventListener('click', closeSheet);
    });

    const menuBtn = document.getElementById('sheet-menu-main');
    if (menuBtn) {
      menuBtn.addEventListener('click', function () {
        if (confirm('Retour au menu ? Ta progression sera sauvegardée.')) {
          window.location.href = 'index.htm';
        }
      });
    }

    document.addEventListener('keydown', function (e) {
      if (!isOpen()) return;
      if (e.key === 'Escape') {
        e.preventDefault();
        closeSheet();
        return;
      }
      if (e.key !== 'Tab') return;

      const focusables = focusableElements();
      if (!focusables.length) {
        e.preventDefault();
        sheet.focus();
        return;
      }
      const first = focusables[0];
      const last = focusables[focusables.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    });

    const grabber = sheet.querySelector('[data-sheet-grabber]');
    if (grabber) {
      let startY = null;
      let pointerId = null;
      grabber.addEventListener('pointerdown', function (e) {
        startY = e.clientY;
        pointerId = e.pointerId;
        grabber.setPointerCapture(pointerId);
      });
      grabber.addEventListener('pointerup', function (e) {
        if (startY !== null && e.clientY - startY > 50) closeSheet();
        startY = null;
        pointerId = null;
      });
      grabber.addEventListener('pointercancel', function () {
        startY = null;
        pointerId = null;
      });
    }
  }

  // -------- Rendu des pages dédiées --------

  function renderSkillsPage(state) {
    const list = document.getElementById('skills-list');
    if (!list) return;
    const descs = window.SKILL_DESCRIPTIONS || {};
    list.innerHTML = '';
    SKILLS_LIST.forEach(s => {
      const li = document.createElement('li');
      const acq = state.skills.includes(s);
      li.className = acq ? 'acquired' : 'locked-skill';
      li.innerHTML = '<strong>' + escapeHtml(s) + '</strong>'
        + (descs[s] ? ' — ' + escapeHtml(descs[s]) : '');
      list.appendChild(li);
    });
    const status = document.getElementById('skills-status');
    if (status) {
      status.textContent = state.skills.length
        ? 'Tu as choisi ' + state.skills.length + ' compétence(s). Les ' + (SKILLS_LIST.length - state.skills.length) + ' autres restent à acquérir lors d\'une autre partie.'
        : 'Tu n\'as pas encore choisi tes compétences. Commence une nouvelle partie pour choisir.';
    }
  }

  function renderObjectsPage(state) {
    const list = document.getElementById('objects-list');
    if (!list) return;
    const infos = window.OBJECT_INFO || {};
    list.innerHTML = '';
    if (!state.objects.length) {
      list.innerHTML = '<li><em>Tu ne portes encore aucun objet. Avance dans l\'aventure pour en trouver.</em></li>';
      return;
    }
    state.objects.forEach(o => {
      const li = document.createElement('li');
      li.className = 'acquired';
      const info = infos[o];
      const desc = info ? info[1] : '';
      li.innerHTML = '<strong>' + escapeHtml(o) + '</strong>'
        + (desc ? ' — ' + escapeHtml(desc) : '');
      list.appendChild(li);
    });
  }

  function renderKeywordsPage(state) {
    const list = document.getElementById('keywords-list');
    if (!list) return;
    list.innerHTML = '';
    if (!state.keywords.length) {
      list.innerHTML = '<li><em>Tu n\'as encore noté aucun mot-clé. Tes choix dans l\'aventure t\'en feront acquérir.</em></li>';
      return;
    }
    state.keywords.forEach(k => {
      const li = document.createElement('li');
      li.className = 'acquired';
      li.textContent = k;
      list.appendChild(li);
    });
  }

  // -------- Page d'accueil --------

  function renderHomePage(state) {
    const continueBtn = document.getElementById('continue-btn');
    const newGameBtn = document.getElementById('newgame-btn');
    const statusDiv = document.getElementById('home-status');
    if (continueBtn && state.currentSection) {
      continueBtn.style.display = '';
      continueBtn.href = 'sect' + state.currentSection + '.htm';
      continueBtn.textContent = 'Continuer';
    } else if (continueBtn) {
      continueBtn.style.display = 'none';
    }
    if (statusDiv && state.currentSection) {
      statusDiv.innerHTML = 'Une aventure est en cours, avec <strong>' + state.skills.length
        + ' compétence(s)</strong>, <strong>' + state.objects.length
        + ' objet(s)</strong> et <strong>' + state.keywords.length + ' mot(s)-clé(s)</strong>.';
    } else if (statusDiv) {
      statusDiv.textContent = 'Aucune aventure en cours. Choisis « Nouvelle partie » pour commencer.';
    }
    if (newGameBtn) {
      newGameBtn.addEventListener('click', function (e) {
        e.preventDefault();
        if (state.currentSection) {
          if (!confirm('Tu as une aventure en cours. Vraiment commencer une nouvelle partie ?')) return;
        }
        resetState();
        window.location.href = 'setup.htm';
      });
    }
  }

  // -------- Page de setup (choix des compétences) --------

  function renderSetupPage() {
    const list = document.getElementById('setup-skill-list');
    if (!list) return;
    const descs = window.SKILL_DESCRIPTIONS || {};
    list.innerHTML = '';
    SKILLS_LIST.forEach((s, i) => {
      const li = document.createElement('li');
      li.innerHTML =
        '<label>'
        + '<input type="checkbox" value="' + escapeHtml(s) + '" />'
        + '<strong>' + escapeHtml(s) + '</strong>'
        + (descs[s] ? '<small>' + escapeHtml(descs[s]) + '</small>' : '')
        + '</label>';
      list.appendChild(li);
    });

    function updateUI() {
      const checked = list.querySelectorAll('input[type=checkbox]:checked');
      list.querySelectorAll('li').forEach(li => {
        const cb = li.querySelector('input');
        if (cb.checked) li.classList.add('selected');
        else li.classList.remove('selected');
      });
      list.querySelectorAll('input[type=checkbox]').forEach(cb => {
        cb.disabled = (!cb.checked && checked.length >= 2);
      });
      const startBtn = document.getElementById('start-btn');
      if (startBtn) startBtn.disabled = (checked.length !== 2);
    }

    list.addEventListener('change', updateUI);
    updateUI();

    const form = document.getElementById('setup-form');
    if (form) {
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        const chosen = Array.from(list.querySelectorAll('input[type=checkbox]:checked')).map(c => c.value);
        if (chosen.length !== 2) {
          alert('Choisis exactement 2 compétences.');
          return;
        }
        const state = JSON.parse(JSON.stringify(DEFAULT_STATE));
        state.skills = chosen;
        state.startedAt = new Date().toISOString();
        state.currentSection = 1;
        state.visitedSections = [];
        saveState(state);
        window.location.href = 'sect1.htm';
      });
    }
  }

  // -------- Initialisation par type de page --------

  function init() {
    const state = loadState();
    const article = document.querySelector('article[data-section]');

    if (article) {
      const num = parseInt(article.getAttribute('data-section'), 10);
      state.currentSection = num;
      if (!state.visitedSections.includes(num)) state.visitedSections.push(num);
      if (!state.startedAt) state.startedAt = new Date().toISOString();
      applyGrants(article, state);
      updateChoices(state);
      saveState(state);
    }

    renderAdventureSheet(state, article);
    setupAdventureSheetControls();
    renderHomePage(state);
    renderSkillsPage(state);
    renderObjectsPage(state);
    renderKeywordsPage(state);
    renderSetupPage();

    // Boutons globaux
    const resetBtn = document.getElementById('global-reset');
    if (resetBtn) {
      resetBtn.addEventListener('click', function (e) {
        e.preventDefault();
        if (confirm('Vraiment effacer ta sauvegarde et recommencer ?')) {
          resetState();
          window.location.href = 'index.htm';
        }
      });
    }

    // Marqueur des sections visitées dans le toc
    if (document.querySelector('.toc-grid')) {
      document.querySelectorAll('.toc-grid a').forEach(a => {
        const m = a.getAttribute('href').match(/sect(\d+)/);
        if (m && state.visitedSections.includes(parseInt(m[1], 10))) {
          a.classList.add('visited');
        }
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
