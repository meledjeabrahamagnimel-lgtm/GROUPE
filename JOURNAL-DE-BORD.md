# Journal de bord — GROUPE

*Ce qui a été fait, séance par séance, et pourquoi. Le plus récent en haut. Pour savoir où l'on
en est maintenant : `REPRENDRE-ICI.md`.*

---

## 15/10/2026 — Démarrage : cahier des charges, décisions, outils de suivi

**Agent :** Claude (Anthropic).

### Ce qui a été fait

1. **Recherche du cahier des charges.** Six dépôts passés en revue. Le cahier n'était pas sur
   `main` de GROUPE mais sur la branche `claude/api-security-performance-djs6mo`, dans `docs/` :
   cahier v2, addendum v3 (normatif), rapport d'évaluation, charte graphique.
2. **Proposition d'architecture** présentée au propriétaire : modules par domaine (Core, Tenancy,
   Auth, Identite, SuperAdmin, Abonnements, Onboarding, Messagerie, Notifications, Documents,
   Paiements, Securite, Referentiel, Scolarite, EmploiDuTemps, Pointage, Evaluation, Classement,
   CahierDeTexte, Comptabilite, Paie, RH, Pilotage). Principe : **les espaces sont des écrans,
   les données appartiennent aux modules**.
3. **Fusion de la spec dans `main`** — PR #1.
4. **Décisions du propriétaire :**
   - pages web en **Inertia + React + Tailwind**, pour rester dans Laravel ;
   - SMS **gratuit** pour l'instant : pilote `log`, puis sandbox Africa's Talking ;
   - réinitialisation du mot de passe d'un **mineur** : code au téléphone du parent, sinon mot de
     passe temporaire du secrétariat (proposition retenue, sans objection) ;
   - nom de domaine : expliqué, à choisir plus tard ;
   - création des outils de suivi demandée : plan Excel (modèle : `PLAN-CORRECTION-SELFLOW.xlsx`),
     fichiers récapitulatifs, passations ; **une branche par bloc, poussée puis fusionnée**.
5. **Outils de suivi créés** (ce bloc) : `PLAN-REALISATION-GROUPE.xlsx` et son générateur
   `outils/plan/generer_plan.py`, `REPRENDRE-ICI.md`, ce journal, `PASSATION-15-10-2026.txt`,
   `CLAUDE.md`.

### Trouvé en chemin

- **Sécurité, hors projet :** le dépôt **public** `GESTION-DE-SITES` expose des comptes de
  démonstration (dont un super-admin) avec le mot de passe `password`. Signalé au propriétaire
  (plan, ligne 0.5).
- **Mise en garde technique notée pour la section 2 :** avec PgBouncer en *transaction pooling*,
  la variable de tenant utilisée par la RLS doit être posée **par transaction**
  (`set_config(..., true)`), sinon elle fuit d'un client à l'autre.
- L'agent ne peut pas pousser de fichier **binaire** depuis sa session : le contenu du plan vit
  donc dans un script texte versionné, et le classeur est déposé par le propriétaire.

### Ce qui reste

Voir `REPRENDRE-ICI.md` § 4. Prochain bloc de l'agent : **section 1, socle technique**.
