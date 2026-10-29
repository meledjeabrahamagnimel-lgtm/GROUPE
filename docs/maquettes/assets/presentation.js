/* Cadre de présentation des maquettes — NE FAIT PAS partie de l'application.
 * 1. Insère le jeu d'icônes (un seul exemplaire pour les trois directions : les navigateurs
 *    bloquent <use href="fichier.svg#id"> quand la page est ouverte par double-clic).
 * 2. Ajoute la barre de test de la couleur d'école en haut de la page.
 * Icônes : trait de 1,8 px, jeu unique, jamais d'emoji (charte § 5).
 * Chargé AVANT accent.js, qui branche ensuite les boutons de la barre. */
(function () {
  'use strict';

  var ICONES = [
    '<symbol id="i-accueil" viewBox="0 0 24 24"><path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/><path d="M10 21v-6h4v6"/></symbol>',
    '<symbol id="i-notes" viewBox="0 0 24 24"><path d="M4 5a2 2 0 0 1 2-2h14v16H6a2 2 0 0 0-2 2z"/><path d="M4 19V5M9 8h7M9 12h5"/></symbol>',
    '<symbol id="i-agenda" viewBox="0 0 24 24"><rect x="3" y="4.5" width="18" height="16.5" rx="2"/><path d="M3 9.5h18M8 3v3M16 3v3"/></symbol>',
    '<symbol id="i-qr" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><path d="M14 14h3v3h-3zM20.5 14v.01M14 20.5h.01M17.5 20.5h3v-3"/></symbol>',
    '<symbol id="i-portefeuille" viewBox="0 0 24 24"><rect x="3" y="6" width="18" height="14" rx="2"/><path d="M3 10h18M16 15h2"/><path d="M6 6l9-3 1.5 3"/></symbol>',
    '<symbol id="i-dossier" viewBox="0 0 24 24"><path d="M3 6.5A1.5 1.5 0 0 1 4.5 5H9l2 2.5h8.5A1.5 1.5 0 0 1 21 9v9.5a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 18.5z"/></symbol>',
    '<symbol id="i-message" viewBox="0 0 24 24"><path d="M4 5h16v11H9l-5 4z"/></symbol>',
    '<symbol id="i-trophee" viewBox="0 0 24 24"><path d="M8 4h8v5a4 4 0 0 1-8 0z"/><path d="M8 6H5a3 3 0 0 0 3 4M16 6h3a3 3 0 0 1-3 4M12 13v3M8.5 20h7M10 16h4l.5 4h-5z"/></symbol>',
    '<symbol id="i-eleve" viewBox="0 0 24 24"><path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11v5c3 2.5 9 2.5 12 0v-5M22 9v6"/></symbol>',
    '<symbol id="i-parent" viewBox="0 0 24 24"><circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M16 4.5a3.5 3.5 0 0 1 0 7M18 14a6.5 6.5 0 0 1 3.5 6"/></symbol>',
    '<symbol id="i-prof" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="12" rx="1.5"/><path d="M8 20l4-4 4 4M7 8h6M7 11h4"/></symbol>',
    '<symbol id="i-admin" viewBox="0 0 24 24"><path d="M4 21V7l8-4 8 4v14"/><path d="M9 21v-5h6v5M8 10h.01M12 10h.01M16 10h.01M8 13h.01M16 13h.01"/></symbol>',
    '<symbol id="i-recherche" viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></symbol>',
    '<symbol id="i-cloche" viewBox="0 0 24 24"><path d="M6 9a6 6 0 0 1 12 0c0 6 2.5 7.5 2.5 7.5h-17S6 15 6 9"/><path d="M10 20a2 2 0 0 0 4 0"/></symbol>',
    '<symbol id="i-fleche" viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></symbol>',
    '<symbol id="i-bouclier" viewBox="0 0 24 24"><path d="M12 3 4.5 6v6c0 4.5 3.2 7.8 7.5 9 4.3-1.2 7.5-4.5 7.5-9V6z"/><path d="m9 12 2 2 4-4"/></symbol>',
    '<symbol id="i-activite" viewBox="0 0 24 24"><path d="M3 12h4l3-8 4 16 3-8h4"/></symbol>',
    '<symbol id="i-journal" viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h10"/></symbol>',
    '<symbol id="i-maintenance" viewBox="0 0 24 24"><path d="M12 3v9"/><path d="M6.3 7a8 8 0 1 0 11.4 0"/></symbol>',
    '<symbol id="i-reglages" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M12 2.5v3M12 18.5v3M4.6 4.6l2.1 2.1M17.3 17.3l2.1 2.1M2.5 12h3M18.5 12h3M4.6 19.4l2.1-2.1M17.3 6.7l2.1-2.1"/></symbol>',
    '<symbol id="i-courriel" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></symbol>',
    '<symbol id="i-telephone" viewBox="0 0 24 24"><path d="M5 3h4l2 5-2.5 1.5a11 11 0 0 0 6 6L16 13l5 2v4a2 2 0 0 1-2 2A17 17 0 0 1 3 5a2 2 0 0 1 2-2"/></symbol>',
    '<symbol id="i-menu" viewBox="0 0 24 24"><path d="M4 7h16M4 12h16M4 17h16"/></symbol>',
    '<symbol id="i-cadenas" viewBox="0 0 24 24"><rect x="5" y="10.5" width="14" height="10.5" rx="2"/><path d="M8 10.5V7a4 4 0 0 1 8 0v3.5"/></symbol>',
    '<symbol id="i-alerte" viewBox="0 0 24 24"><path d="M12 3 2 20h20z"/><path d="M12 10v4M12 17h.01"/></symbol>',
    '<symbol id="i-horloge" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></symbol>',
    '<symbol id="i-coche" viewBox="0 0 24 24"><path d="m5 12 5 5 9-10"/></symbol>',
    '<symbol id="i-telecharger" viewBox="0 0 24 24"><path d="M12 4v11M7 10l5 5 5-5M5 20h14"/></symbol>',
    '<symbol id="i-grille" viewBox="0 0 24 24"><rect x="3.5" y="3.5" width="7" height="7" rx="1"/><rect x="13.5" y="3.5" width="7" height="7" rx="1"/><rect x="3.5" y="13.5" width="7" height="7" rx="1"/><rect x="13.5" y="13.5" width="7" height="7" rx="1"/></symbol>',
    '<symbol id="i-interdit" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="m5.6 5.6 12.8 12.8"/></symbol>',
    '<symbol id="i-globe" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.5 3 14.5 0 18M12 3c-3 3.5-3 14.5 0 18"/></symbol>',
    '<symbol id="i-actualiser" viewBox="0 0 24 24"><path d="M20 11a8 8 0 1 0-2.3 5.7"/><path d="M20 4v7h-7"/></symbol>',
    '<symbol id="i-chevron" viewBox="0 0 24 24"><path d="m6 9 6 6 6-6"/></symbol>',
    '<symbol id="i-plus" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></symbol>',
    '<symbol id="i-utilisateur" viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></symbol>'
  ];

  var COULEURS = [
    ['#143D36', 'Plateforme'],
    ['#1F6B3A', 'Lycée vert'],
    ['#7A1F33', 'Université bordeaux'],
    ['#F2C230', 'Jaune vif'],
    ['#808080', 'Gris moyen (refusé)']
  ];

  var sprite = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  sprite.setAttribute('aria-hidden', 'true');
  sprite.style.display = 'none';
  sprite.innerHTML = ICONES.join('');
  document.body.insertBefore(sprite, document.body.firstChild);

  var direction = document.body.getAttribute('data-direction');
  if (!direction) return;

  var barre = document.createElement('div');
  barre.className = 'pres-barre';
  barre.setAttribute('role', 'region');
  barre.setAttribute('aria-label', 'Présentation des maquettes (hors application)');
  var html = '<span class="pres-titre">Direction ' + direction + '</span>'
    + '<a href="index.html">Toutes les directions</a><span>Couleur de l\u2019école :</span>';
  COULEURS.forEach(function (c, i) {
    html += '<button data-accent="' + c[0] + '" aria-pressed="' + (i === 0) + '">'
      + '<span class="rond" style="background:' + c[0] + '"></span>' + c[1] + '</button>';
  });
  html += '<label style="display:inline-flex;gap:6px;align-items:center">Autre '
    + '<input type="color" id="accent-libre" value="#143D36" aria-label="Choisir une autre couleur"></label>'
    + '<span class="pres-message" role="status" aria-live="polite"></span>'
    + '<span style="flex-basis:100%;color:#A8A196">Données fictives. Adresses IP de documentation '
    + '(RFC 5737). Aucune donnée réelle.</span>';
  barre.innerHTML = html;
  document.body.insertBefore(barre, sprite.nextSibling);
})();
