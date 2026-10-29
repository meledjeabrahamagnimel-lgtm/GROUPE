/* Dérivation de l'accent d'une école — règle normative de la charte § 2.4.
 *
 * L'école ne fournit qu'UNE couleur. On en déduit :
 *   1. --accent-ink  : blanc ou --ink, celui qui atteint 4,5:1 sur l'accent ;
 *   2. --accent-tint : accent éclairci jusqu'à un contraste ≤ 1,3:1 avec --surface ;
 *   3. refus si aucune des deux encres n'atteint 4,5:1, avec proposition de la variante la plus
 *      proche qui passe.
 * En variante sombre, l'accent est éclairci jusqu'à 4,5:1 sur le fond sombre (§ 2.3).
 *
 * Ce fichier est un PROTOTYPE pour les maquettes. Dans l'application, ce calcul est fait par le
 * serveur (PHP) à la saisie de la couleur (bloc 4.4), puis les trois variables sont posées sur
 * <html> par le middleware de tenant : le navigateur ne calcule rien.
 */
(function () {
  'use strict';

  var ENCRE = '#1C1A17';
  var BLANC = '#FFFFFF';
  var FOND_SOMBRE = '#16150F';

  function versRgb(hex) {
    var h = hex.replace('#', '');
    if (h.length === 3) h = h.split('').map(function (c) { return c + c; }).join('');
    return [0, 2, 4].map(function (i) { return parseInt(h.substr(i, 2), 16); });
  }
  function versHex(rgb) {
    return '#' + rgb.map(function (v) {
      var s = Math.max(0, Math.min(255, Math.round(v))).toString(16);
      return s.length === 1 ? '0' + s : s;
    }).join('').toUpperCase();
  }
  // Luminance relative WCAG 2.x.
  function luminance(hex) {
    var c = versRgb(hex).map(function (v) {
      v /= 255;
      return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
  }
  function contraste(a, b) {
    var la = luminance(a), lb = luminance(b);
    return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
  }
  function melange(hex, vers, t) {
    var a = versRgb(hex), b = versRgb(vers);
    return versHex(a.map(function (v, i) { return v + (b[i] - v) * t; }));
  }

  /** Renvoie {ok, accent, ink, tint, ratio, proposition}. */
  function deriver(accent) {
    var cBlanc = contraste(accent, BLANC);
    var cEncre = contraste(accent, ENCRE);
    if (cBlanc < 4.5 && cEncre < 4.5) {
      // Variante la plus proche qui passe : on assombrit pas à pas jusqu'à 4,5:1 avec le blanc.
      var p = accent;
      for (var t = 0.02; t <= 1; t += 0.02) {
        p = melange(accent, '#000000', t);
        if (contraste(p, BLANC) >= 4.5) break;
      }
      return { ok: false, accent: accent, proposition: p, ratio: Math.max(cBlanc, cEncre) };
    }
    var ink = cBlanc >= 4.5 ? BLANC : ENCRE;
    var tint = accent;
    for (var k = 0.5; k <= 1; k += 0.01) {
      tint = melange(melange(accent, '#808080', 0.25), BLANC, k); // désaturé puis éclairci
      if (contraste(tint, BLANC) <= 1.3) break;
    }
    return { ok: true, accent: accent, ink: ink, tint: tint, ratio: Math.max(cBlanc, cEncre) };
  }

  /** Variante sombre : accent éclairci jusqu'à 4,5:1 sur le fond sombre ET avec l'encre posée
   *  dessus (sinon le texte d'un bouton primaire deviendrait illisible). */
  function deriverSombre(accent) {
    var a = accent;
    for (var t = 0; t <= 1; t += 0.02) {
      a = melange(accent, BLANC, t);
      if (contraste(a, FOND_SOMBRE) >= 4.5 && contraste(a, ENCRE) >= 4.5) break;
    }
    return {
      accent: a,
      ink: contraste(a, ENCRE) >= contraste(a, BLANC) ? ENCRE : BLANC,
      tint: melange(a, FOND_SOMBRE, 0.82)
    };
  }

  function appliquer(accent) {
    var d = deriver(accent);
    var msg = document.querySelector('.pres-message');
    if (!d.ok) {
      if (msg) {
        msg.textContent = 'Couleur ' + accent + ' refusée : ni le blanc ni l\u2019encre n\u2019atteignent 4,5:1 '
          + '(meilleur : ' + d.ratio.toFixed(2).replace('.', ',') + ':1). Variante proposée : ' + d.proposition
          + ' — appliquée pour la démonstration.';
        msg.classList.add('visible');
      }
      d = deriver(d.proposition);
    } else if (msg) {
      msg.classList.remove('visible');
    }
    var racine = document.documentElement.style;
    racine.setProperty('--accent', d.accent);
    racine.setProperty('--accent-ink', d.ink);
    racine.setProperty('--accent-tint', d.tint);

    // L'espace super-admin n'appartient à aucune école : il garde l'accent de la plateforme.
    var s = deriverSombre(d.accent);
    var sPlateforme = deriverSombre('#143D36');
    document.querySelectorAll('.sombre').forEach(function (el) {
      var v = el.closest('[data-plateforme]') ? sPlateforme : s;
      el.style.setProperty('--accent', v.accent);
      el.style.setProperty('--accent-ink', v.ink);
      el.style.setProperty('--accent-tint', v.tint);
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    var boutons = document.querySelectorAll('[data-accent]');
    boutons.forEach(function (b) {
      b.addEventListener('click', function () {
        boutons.forEach(function (x) { x.setAttribute('aria-pressed', 'false'); });
        b.setAttribute('aria-pressed', 'true');
        appliquer(b.getAttribute('data-accent'));
      });
    });
    var libre = document.querySelector('#accent-libre');
    if (libre) libre.addEventListener('input', function () {
      boutons.forEach(function (x) { x.setAttribute('aria-pressed', 'false'); });
      appliquer(libre.value.toUpperCase());
    });
    // Paramètre ?accent=7A1F33 : utilisé pour les captures automatiques.
    var q = new URLSearchParams(location.search).get('accent');
    appliquer(q ? '#' + q.replace('#', '') : '#143D36');
  });

  window.GroupeAccent = { deriver: deriver, deriverSombre: deriverSombre, contraste: contraste };
})();
