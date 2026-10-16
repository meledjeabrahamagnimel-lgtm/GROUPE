---
description: Reprendre le projet au début d'une séance (lit le contexte et fait le point)
---

Reprends le projet GROUPE là où il en est. Dans l'ordre :

1. Lis en entier `REPRENDRE-ICI.md`.
2. Lis la `PASSATION-*.txt` la plus récente et la première entrée de `JOURNAL-DE-BORD.md`.
3. Lis la liste `PLAN` de `outils/plan/generer_plan.py` : repère les lignes « Attend vous »,
   « À trancher » et la première section qui n'est pas terminée.
4. Vérifie l'état réel du dépôt : `git status`, `git branch --show-current`,
   `git log --oneline -5`, `git fetch && git status -sb` (main est-il à jour ?).
5. Si le projet contient du code Laravel : `php artisan migrate:status` et, si c'est rapide,
   `php artisan test`. Ne rien corriger à ce stade : constater.

Puis réponds au propriétaire, en français, en moins de vingt lignes :

- **Où l'on en est** (une ou deux phrases) ;
- **Ce qui l'attend, lui** : les tâches « Vous » ouvertes, par ordre d'urgence, avec leur N° ;
- **Le prochain bloc que tu proposes**, avec les N° du plan et la branche que tu créeras ;
- toute anomalie constatée (branche inattendue, fichiers non commités, tests rouges).

N'engage **aucun** travail avant son accord.

Contexte supplémentaire donné par le propriétaire : $ARGUMENTS
