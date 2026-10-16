---
description: Clôturer un bloc de travail (nettoyage, plan, fichiers de suivi, branche, PR, fusion)
---

Clôture le bloc de travail en cours, en suivant le § 3 de `CLAUDE.md` :

1. **Nettoyage** (§ 5 de `CLAUDE.md`) : cherche et supprime `dd(`, `dump(`, `var_dump(`,
   `console.log(` de mise au point, fichiers `scratch_*` / `check_*` / brouillons, données de
   test hors factories et seeders de développement. Liste ce que tu as supprimé.
2. **Tests** : `php artisan test` (PostgreSQL). S'ils échouent, arrête-toi et dis pourquoi.
3. **Plan** : mets à jour les statuts et les dates Début / Fin des lignes concernées dans
   `outils/plan/generer_plan.py`, ajoute les tâches nouvelles (avec « Qui »), puis exécute
   `python outils/plan/generer_plan.py`.
4. **Suivi** : mets à jour `REPRENDRE-ICI.md` (§§ 3 et 4), ajoute une entrée datée en haut de
   `JOURNAL-DE-BORD.md` (fait, trouvé en chemin, reste), écris ou complète
   `PASSATION-<JJ-MM-AAAA>.txt` du jour.
5. **Git** : commit sur la branche du bloc, `git push`, ouvre la PR vers `main`, attends la CI,
   fusionne dans `main`, `git checkout main && git pull`.
6. **Compte rendu** au propriétaire, en français : ce qui a été fait, ce qui l'attend (N° du plan),
   le bloc suivant proposé.

Précisions du propriétaire : $ARGUMENTS
