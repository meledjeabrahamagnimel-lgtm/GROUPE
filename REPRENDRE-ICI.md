# Reprendre ici

*Écrit pour qui ouvre une séance sur ce projet — le propriétaire ou l'assistant — et doit être
utile dans la minute. Mis à jour le 15 octobre 2026.*

`JOURNAL-DE-BORD.md` est la mémoire longue (ce qui a été fait, séance par séance).
`PLAN-REALISATION-GROUPE.xlsx` est le guide (tous les chantiers, qui fait quoi, statut).
Ce fichier-ci dit seulement **en quoi consiste l'application, où l'on en est, et ce qui reste**.

---

## 1. L'application en dix lignes

**GROUPE** est une plateforme **SaaS multitenant de gestion scolaire** (web + mobile Flutter).
Chaque établissement — collège, lycée, université, grande école — souscrit un pack et reçoit
**son adresse** (`lycee-x.<domaine>`), son logo, sa couleur, et des données **totalement isolées**
des autres écoles.

Espaces : **Super-admin** (le propriétaire : écoles, abonnements, supervision, maintenance),
**Directeur** (statistiques, lecture seule), **Secrétariat**, **Comptabilité**, **RH**,
**Professeur**, **Élève / Étudiant** (le vocabulaire suit le type d'école), **Parent**.

Modules transverses : **Pointage** (QR rotatif, biométrie, manuel → absences automatiques),
**Évaluation** (moyennes, bulletins, classement des meilleurs), **Paiements** (Orange Money,
Wave, CinetPay, carte → reçu PDF), **Messagerie**, **Mon Dossier** (documents de l'apprenant).

Exigences transversales : sécurité de premier rang (OWASP, isolation par RLS PostgreSQL, aucune
erreur brute), performance « aucune attente perceptible » (index, curseur, cache, partitionnement),
responsive sur tout écran.

## 2. La pile technique (décidée)

| Couche | Choix |
|---|---|
| Serveur | Laravel 13, PHP 8.3, `nwidart/laravel-modules` |
| Pages web | **Inertia + React + Tailwind** (validé le 15/10 — on reste dans Laravel et ses commandes) |
| Base | PostgreSQL 16 (RLS, partitionnement) — jamais SQLite, même en test |
| Cache, sessions, files | Redis 7 |
| Mobile | Flutter (API `/api/v1`, JWT RS256) |
| SMS | Interface `SmsSender` : pilote `log` en local, Africa's Talking **sandbox** (gratuit) en test |
| Hébergement (plus tard) | VPS + Cloudflare + Laravel Forge ou Ploi |

## 3. Où l'on en est — 15 octobre 2026

**Branche de référence :** `main`. Le dépôt ne contient encore **aucun code métier** : le
squelette Laravel et la documentation.

Fait :

- Cahier des charges retrouvé (il était sur une branche) et **fusionné dans `main`** (PR #1).
- Décisions de départ prises (pile web, SMS gratuit, réinitialisation des mineurs).
- Outils de suivi créés : ce fichier, `JOURNAL-DE-BORD.md`, `PASSATION-15-10-2026.txt`,
  `CLAUDE.md`, le plan Excel et son générateur.

**Prochain bloc pour l'agent : section 1 du plan — le socle technique** (Inertia/React,
modules, `.env.example`, charte, CI GitHub).

## 4. Ce qui reste — et qui le fait

### Chez vous (le propriétaire), par ordre d'urgence

| N° | Quoi | Comment |
|---|---|---|
| **0.5** | **Dépôt GESTION-DE-SITES public avec des comptes de démonstration** | GitHub › GESTION-DE-SITES › Settings › General › Danger Zone › *Change visibility* › Private. Changer les mots de passe de ces comptes s'ils existent sur un serveur. |
| **0.4** | Déposer le plan Excel dans le dépôt | GitHub › GROUPE › *Add file* › *Upload files* › glisser `PLAN-REALISATION-GROUPE.xlsx` › *Commit changes*. (L'agent ne peut pas pousser de fichier binaire depuis sa session ; à chaque mise à jour il vous le redonne, ou vous le régénérez : `python outils/plan/generer_plan.py`.) |
| **0.7** | Poste local : PostgreSQL 16, Redis, Node 20, PHP 8.3 (pdo_pgsql, redis) | Dans Laragon. Procédure détaillée livrée au bloc 1 (`ENVIRONNEMENT-DE-DEV.md`). |
| **1.6** | Protéger `main` | Après le bloc 1 : Settings › Branches › ruleset sur `main` (PR obligatoire, CI verte, pas de force-push). |
| 0.6 | Nom de domaine | Y réfléchir ; rien à acheter avant la section 12. |
| 3.5, 8.1 | Comptes de test gratuits (SMS, paiement) | Au moment des sections 3 et 8. Les clés vont dans **votre** `.env`, jamais dans la conversation. |
| 7.2, 8.5, 10.1 | Règles de calcul des bulletins, règles de paie, prix des packs | À trancher avant les sections 7, 8 et 10. |

Quand une tâche est faite, écrire simplement **« 0.5 terminé »** : l'agent met le plan à jour.

### Chez l'agent

Sections 1 à 12 du plan, dans l'ordre. L'ordre compte : la base de données (identifiants,
partitionnement) et l'isolation des écoles se posent **avant** la première table métier ; les
changer ensuite impose de réécrire les tables.

## 5. Comment l'agent travaille

- **Qui :** Claude, assistant de développement d'Anthropic, utilisé comme agent (lecture du dépôt,
  écriture du code, branches, PR, fusions).
- **Un bloc = une branche** (`bloc/<n°>-<sujet>`), poussée, PR, CI verte, fusion dans `main`.
- À chaque bloc : plan Excel régénéré, ce fichier et le journal mis à jour, passation du jour.
- Il ne passe une tâche « Vous » à Terminé que sur votre parole.

## 6. Démarrer une séance

```bash
cd C:/laragon/www/GROUPE
git checkout main && git pull
git log --oneline -5
# à partir du bloc 1 :
php artisan migrate:status
php artisan test
```
