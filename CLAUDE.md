# GROUPE — consignes de séance

**Avant tout travail, lire [REPRENDRE-ICI.md](REPRENDRE-ICI.md) en entier.** Il dit en quoi
consiste l'application, où l'on en est, ce qui reste et **qui** doit le faire.

Les références, dans l'ordre d'autorité :

1. `docs/02-addendum-v3-securite-performance.md` — **normatif**, remplace la v2 sur les points qu'il cite ;
2. `docs/01-cahier-des-charges-v2.md` — la spécification fonctionnelle ;
3. `docs/03-rapport-evaluation-code.md` — défauts déjà identifiés, à ne pas reproduire ;
4. `docs/04-charte-graphique.md` — « Ivoire & Encre ».

Le plan de réalisation : `PLAN-REALISATION-GROUPE.xlsx`, généré par
`outils/plan/generer_plan.py` (le **script** est la source, le classeur sa sortie).

**À la fin de chaque bloc de travail** :

- **nettoyer** : supprimer toute donnée de test, fichier de brouillon, script ponctuel ou code
  mort laissé par le bloc (règle du propriétaire, 16/10) — voir « Propreté » ci-dessous ;
- mettre à jour les statuts dans `outils/plan/generer_plan.py` et régénérer le classeur ;
- mettre à jour `REPRENDRE-ICI.md` (§§ 3 et 4) et ajouter une entrée à `JOURNAL-DE-BORD.md` ;
- écrire `PASSATION-<JJ-MM-AAAA>.txt` (un par jour ; on complète celui du jour s'il existe) ;
- commiter sur la branche du bloc, pousser, ouvrir la PR, CI verte, **fusionner dans `main`**.

Règles qui priment sur tout le reste :

- **Une branche par bloc de travail**, jamais de poussée directe sur `main`.
- **Isolation des écoles** : tout modèle métier porte `BelongsToTenant` ; le `tenant_id` vient
  du sous-domaine résolu côté serveur, **jamais** de la requête. RLS PostgreSQL en seconde barrière.
- **Aucun identifiant interne exposé** : `public_id` dans les URL et les réponses.
- **Aucun secret** dans le dépôt, dans une variable `VITE_*`, ni dans la conversation.
- **Index, curseur, pas de N+1** : une migration sans ses index est refusée.
- **PostgreSQL partout, y compris dans les tests** (jamais SQLite).
- Écrire en français, commentaires qui disent **pourquoi**.
- Une tâche marquée « Vous » dans le plan n'est passée à Terminé que lorsque le propriétaire
  l'a dit (« N° terminé »).

**Propreté du code (règle du propriétaire, 16/10)** :

- Aucun fichier `scratch_*`, `check_*`, `test_*.php` à la racine, aucun `dd()`, `dump()`,
  `var_dump()` ni `console.log` de mise au point laissé dans le code.
- Les données de test vivent **uniquement** dans `database/factories` et dans les seeders de
  développement, jamais dans les migrations. Les seeders de démonstration refusent de tourner
  en production (`app()->isProduction()` → arrêt), et **aucun compte au mot de passe connu**
  (« password », « 123456 »…) n'est créé hors de l'environnement local.
- Les tests créent leurs données et les effacent (transaction annulée à la fin de chaque test).

**Design (demande du propriétaire, 16/10)** : avant d'écrire la première page du front, présenter
des **propositions visuelles** (maquettes HTML ouvrables dans le navigateur et captures) et
attendre le choix du propriétaire. Aucune page n'est codée sur une direction non validée.
