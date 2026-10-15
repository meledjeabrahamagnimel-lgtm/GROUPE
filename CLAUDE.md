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
