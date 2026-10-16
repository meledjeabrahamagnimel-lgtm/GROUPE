# Reprendre ici

*Écrit pour qui ouvre une séance sur ce projet — le propriétaire ou l'assistant — et doit être
utile dans la minute. Mis à jour le 16 octobre 2026.*

**Dans Claude Code : taper `/reprendre`** — l'agent lit ce fichier, la passation, le journal et le
plan, vérifie le dépôt et fait le point. `/fin-de-bloc` clôt un bloc.

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
| Outil de l'agent | **Claude Code** sur le PC du propriétaire (décidé le 16/10) |

## 3. Où l'on en est — 16 octobre 2026

**Branche de référence :** `main`. Le dépôt ne contient encore **aucun code métier** : le
squelette Laravel et la documentation.

Fait :

- Cahier des charges retrouvé et **fusionné dans `main`** (PR #1).
- Décisions de départ prises (pile web, SMS gratuit, réinitialisation des mineurs).
- Outils de suivi créés (PR #2) ; plan Excel déposé par le propriétaire le 16/10.
- Règles de **propreté du code** et de **validation du design avant le front** (PR #3).
- **Passage à Claude Code sur le PC du propriétaire décidé** (option A, 16/10) ; `CLAUDE.md`
  réécrit pour donner à l'agent son rôle et sa méthode ; commandes `/reprendre` et `/fin-de-bloc`.

⚠️ Le classeur `PLAN-REALISATION-GROUPE.xlsx` présent sur `main` date du 15/10 (avant les lignes
0.8, 1.0 et 13.4). **Première action de l'agent dans Claude Code :** `python outils/plan/generer_plan.py`
puis commiter le classeur régénéré.

**Prochain bloc pour l'agent :** **1.0 — propositions de design** (maquettes à valider), puis
le reste de la section 1, le socle technique, sur la branche `bloc/1-socle-technique`.

## 4. Ce qui reste — et qui le fait

### Chez vous (le propriétaire), par ordre d'urgence

| N° | Quoi | Comment |
|---|---|---|
| **0.5** | **Dépôt GESTION-DE-SITES public avec des comptes de démonstration** | GitHub › GESTION-DE-SITES › Settings › General › Danger Zone › *Change visibility* › Private. Changer les mots de passe de ces comptes s'ils existent sur un serveur. |
| **0.8** | Installer Claude Code | Node 20 ; `npm install -g @anthropic-ai/claude-code` ; `git clone` du dépôt dans `C:\laragon\www\GROUPE` ; `pip install openpyxl` ; dans le dossier : `claude`, se connecter, taper `/reprendre`. |
| **0.7** | Poste local : PostgreSQL 16, Redis, Node 20, PHP 8.3 (pdo_pgsql, redis) | Dans Laragon. L'agent vous guidera depuis Claude Code (`ENVIRONNEMENT-DE-DEV.md`, ligne 1.7). |
| **1.0** | Choisir une direction de design | Quand l'agent présentera les maquettes. |
| **1.6** | Protéger `main` | Après la CI du bloc 1 : Settings › Branches › ruleset sur `main`. |
| 0.6 | Nom de domaine | Y réfléchir ; rien à acheter avant la section 12. |
| 3.5, 8.1 | Comptes de test gratuits (SMS, paiement) | Au moment des sections 3 et 8. Les clés vont dans **votre** `.env`, jamais dans la conversation. |
| 7.2, 8.5, 10.1 | Règles des bulletins, règles de paie, prix des packs | À trancher avant les sections 7, 8 et 10. |

Quand une tâche est faite, écrire simplement **« 0.5 terminé »** : l'agent met le plan à jour.

### Chez l'agent

Sections 1 à 12 du plan, dans l'ordre. L'ordre compte : la base de données (identifiants,
partitionnement) et l'isolation des écoles se posent **avant** la première table métier ; les
changer ensuite impose de réécrire les tables.

### Le classeur Excel

`PLAN-REALISATION-GROUPE.xlsx` est **généré** par `outils/plan/generer_plan.py`. Avec Claude
Code, l'agent le régénère et le commite lui-même à chaque bloc. Ne pas le modifier à la main :
la modification serait écrasée à la régénération suivante — demander plutôt à l'agent.

## 5. Comment l'agent travaille

- **Qui :** Claude, assistant de développement d'Anthropic, utilisé comme agent dans **Claude Code**
  (lecture du dépôt, code, tests, branches, PR, fusions). Son rôle et sa méthode sont écrits dans
  `CLAUDE.md`, lu automatiquement à chaque démarrage : toute nouvelle séance agit de la même façon.
- **Un bloc = une branche** (`bloc/<n°>-<sujet>`), poussée, PR, CI verte, fusion dans `main`.
- À chaque bloc : nettoyage, plan Excel régénéré, ce fichier et le journal mis à jour, passation du jour.
- Il ne passe une tâche « Vous » à Terminé que sur votre parole.

## 6. Démarrer une séance

```bash
cd C:/laragon/www/GROUPE
git checkout main && git pull
claude            # puis taper /reprendre
```
