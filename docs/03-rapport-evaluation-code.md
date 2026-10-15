# Rapport d'évaluation — propositions techniques du cahier des charges v2

> **Objet** : évaluer ce qui est bon, ce qui est à corriger et ce qui est à écarter dans les propositions techniques du cahier des charges v2, y compris son unique bloc de code.
> **Date** : septembre 2026
> **Périmètre** : `01-cahier-des-charges-v2.md` + état réel du dépôt (squelette Laravel 13, un seul commit).

---

## 1. Synthèse

Le cahier des charges v2 est **solide sur le fond**. Les axes structurants sont justes et bien hiérarchisés : isolation multitenant, pagination par curseur, index composés, URLs signées, absence d'erreur technique en production, responsive *mobile-first*. Peu de cahiers des charges de cette taille sont aussi cohérents.

Les problèmes se concentrent à trois endroits :

1. **Le seul bloc de code fourni (§3.1) comporte 8 défauts**, dont 3 de sécurité et 1 de performance directement contraire aux objectifs du document lui-même.
2. **Quatre propositions de sécurité sont contre-productives** ou créent un risque nouveau (VirusTotal, `sqlmap` en CI, chiffrement de *query string*, JWT en contexte web).
3. **Deux règles métier du module Pointage ont un défaut de conception** exploitable ou injuste pour l'apprenant.

Aucun de ces points n'est bloquant pour le projet : ils se corrigent à la spécification, avant écriture de code — c'est le bon moment.

| Catégorie | Nombre |
|---|---|
| Propositions validées telles quelles | 14 |
| Propositions à amender | 9 |
| Propositions à écarter | 4 |
| Défauts du code fourni | 8 |
| Écarts entre le dépôt actuel et le cahier | 7 |

---

## 2. Audit du code fourni — middleware de résolution de tenant (§3.1)

Code évalué :

```javascript
app.use(async (req, res, next) => {
  const host = req.hostname;
  const slug = host.split('.')[0];
  const tenant = await Tenant.findOne({ slug });
  if (!tenant) return res.status(404).send('École introuvable');
  req.tenant = tenant;
  next();
});
```

C'est le point d'entrée de **toute** requête de la plateforme et le pivot de l'isolation des données. Il mérite donc l'examen le plus strict.

### C-1 — Incohérence de pile technique · *Gravité : structurelle*

Le code est écrit en Express avec une syntaxe Mongoose (`Tenant.findOne({ slug })`), alors que §27.3 retient Laravel ou Node au choix, que §27.3 impose **PostgreSQL**, et que le dépôt réel est un **squelette Laravel 13**. Ce code n'est transposable ni tel quel ni par simple traduction.

**Correctif** : réécrire en middleware Laravel. Le reste de cet audit porte sur la *logique*, qui est le vrai sujet et qui est transposable.

### C-2 — L'en-tête `Host` est une donnée fournie par le client · *Gravité : élevée*

`req.hostname` dérive de l'en-tête HTTP `Host`, que le client contrôle entièrement. Sans liste blanche au niveau du serveur web, un attaquant peut envoyer un `Host` arbitraire. Conséquences classiques : empoisonnement de cache, et surtout **liens de réinitialisation de mot de passe pointant vers un domaine contrôlé par l'attaquant** — une prise de contrôle de compte directeur en une requête.

**Correctif** :
- Nginx : `server_name` explicite et un `server` par défaut renvoyant `444` pour tout `Host` non reconnu.
- Application : validation que le `Host` se termine bien par le domaine de la plateforme **avant** toute résolution.
- Toutes les URL générées pour les emails proviennent d'une valeur de configuration, jamais de la requête.

### C-3 — Le statut du tenant n'est pas vérifié · *Gravité : élevée (fonctionnelle)*

§9.3 définit les statuts *Actif / Suspendu / Bloqué / Démo* et une date d'expiration. Le middleware les ignore : **une école suspendue pour non-paiement, bloquée, ou dont l'abonnement a expiré continue de fonctionner normalement.** Tout le modèle économique du SaaS repose sur ce contrôle, et il est absent.

**Correctif** : après résolution, vérifier le statut et la date d'expiration, et router vers la page adéquate (suspension, expiration, maintenance) selon le cas — sans jamais révéler lequel à un visiteur non authentifié (voir C-5).

### C-4 — Une requête en base à chaque requête HTTP · *Gravité : élevée (performance)*

Aucune mise en cache. Chaque appel HTTP — y compris chaque ressource statique passant par PHP, chaque appel d'API, chaque image servie par l'application — déclenche une lecture de la table `tenants`. Une page qui charge 30 ressources produit 30 lectures identiques.

C'est **directement contraire à §24.1** (« aucune latence perceptible ») et à §24.4 (« cache serveur pour les données peu changeantes : configuration du tenant »). Le cahier prescrit la solution ailleurs et l'oublie ici.

**Correctif** : cache Redis, clé `tenant:slug:<slug>`, TTL 5 minutes, invalidation explicite à toute modification du tenant. Mettre en cache **aussi les résolutions négatives** (slug inexistant), sans quoi un balayage de sous-domaines génère une lecture en base par tentative — un vecteur de déni de service à très faible coût.

### C-5 — Fuite d'information par le message d'erreur · *Gravité : moyenne*

`404 'École introuvable'` distingue un sous-domaine inexistant d'un sous-domaine existant. On peut donc **énumérer les établissements clients** de la plateforme, apprendre qui utilise le produit, et cibler une école précise. C'est exactement le type de découverte que la demande veut empêcher.

**Correctif** : réponse générique identique pour slug inexistant, réservé, suspendu ou bloqué, avec le même corps, les mêmes en-têtes et un temps de réponse normalisé (§29.2.2 de l'addendum).

### C-6 — `host.split('.')[0]` est trop naïf · *Gravité : moyenne*

Cas non gérés :
- `www.votreplateforme.com` → slug `www`, résolu comme une école nommée « www ».
- `admin.votreplateforme.com` (§9.1, espace super-admin) → résolu comme une école nommée « admin ». **Si quelqu'un parvient à créer une école avec le slug `admin`, il intercepte l'espace super-admin.**
- Domaine personnalisé d'une école (`intranet.lycee-x.ci`) → non prévu, alors que le plan Enterprise le suppose.
- Environnement local ou accès par adresse IP → chaîne sans point, le découpage renvoie l'hôte entier.

**Correctif** : liste de sous-domaines **réservés** interdits à l'inscription (`admin`, `www`, `api`, `app`, `static`, `assets`, `mail`, `cdn`, `status`, `staging`) ; validation stricte du format du slug ; table de correspondance pour les domaines personnalisés ; contrainte d'unicité globale sur `slug`.

### C-7 — L'objet tenant complet est exposé à toute l'application · *Gravité : moyenne*

`req.tenant = tenant` place l'enregistrement entier dans le contexte de la requête. Si cette table contient un jour des identifiants de passerelle de paiement propres à l'école, une clé d'API ou une configuration interne — ce qui est probable, §21 prévoyant des paiements par tenant — ces valeurs deviennent accessibles partout, y compris depuis les vues, avec un risque réel de sérialisation accidentelle vers le client.

**Correctif** : n'exposer qu'un objet restreint (identifiant, slug, nom, type d'entité, couleurs, logo, statut, plan). Les secrets restent dans un dépôt séparé, chiffrés au repos, lus uniquement au moment de l'appel à la passerelle.

### C-8 — Poser `tenant` ne garantit rien · *Gravité : critique*

C'est le point le plus important de cet audit. Le middleware **identifie** le tenant ; il ne **garantit** rien. Une seule requête écrite sans filtre, un jour, dans un contrôleur, expose les données d'un autre établissement. Or §1.3 pose l'« isolation totale des données » comme principe fondamental, et §28 la place en tête des bonnes pratiques.

Un mécanisme qui dépend de la discipline des développeurs finit toujours par céder. Il faut un dispositif qui **échoue par défaut**.

**Correctif — trois barrières indépendantes** :
1. **Scope global d'ORM** appliqué automatiquement par un trait obligatoire sur tout modèle métier, plus un test qui parcourt les modèles et échoue si l'un d'eux ne porte pas le trait.
2. **Row-Level Security PostgreSQL** : politique par table fondée sur une variable de session positionnée par le middleware. Même une requête brute qui oublierait le filtre ne peut pas franchir cette barrière. C'est l'application littérale du principe de défense en profondeur de §28.
3. **Suite de tests d'isolation** : pour chaque endpoint, un test vérifie qu'un utilisateur du tenant A reçoit `404` sur une ressource du tenant B.

### C-9 — Aucune gestion d'erreur · *Gravité : faible*

Si la base est indisponible, l'exception remonte brute — ce qui contredit §25.1 (« aucune erreur technique brute visible en production »), et ce dès la toute première couche de l'application.

**Correctif** : capture de l'exception, journalisation avec contexte, réponse générique, alerte au super-admin conformément à §25.2.

### Synthèse de l'audit

| Réf. | Défaut | Gravité |
|---|---|---|
| C-8 | Le scope n'est pas garanti | **Critique** |
| C-2 | En-tête `Host` non validé | Élevée |
| C-3 | Statut d'abonnement ignoré | Élevée |
| C-4 | Aucune mise en cache | Élevée |
| C-5 | Énumération des écoles clientes | Moyenne |
| C-6 | Découpage de sous-domaine naïf | Moyenne |
| C-7 | Objet tenant complet exposé | Moyenne |
| C-9 | Aucune gestion d'erreur | Faible |
| C-1 | Pile technique incohérente | Structurelle |

---

## 3. Évaluation des autres propositions techniques

### 3.1 Propositions validées telles quelles

| §  | Proposition | Commentaire |
|---|---|---|
| 9.4 | Pagination par curseur au-delà de quelques milliers de lignes | Correct et correctement justifié. L'`OFFSET` lit et jette les lignes précédentes |
| 9.4 / 24.2 | Index composés `(tenant_id, …)` | Bon ordre de colonnes : le préfixe le plus sélectif et toujours présent en tête |
| 9.4 | Recherche différée 300 ms | Standard. À compléter par l'annulation de la requête précédente (§32.6) |
| 9.4 | Virtualisation des tableaux | Nécessaire au-delà de quelques centaines de lignes |
| 3.2 | URLs signées temporaires pour les documents | Laravel le fournit nativement. Indispensable pour §15.4 |
| 23.1 | ORM avec requêtes préparées, jamais de concaténation | La bonne règle, énoncée au bon niveau |
| 23.2 | CSP stricte, cookies `HttpOnly`/`Secure`/`SameSite=Strict` | Correct |
| 23.5 | Argon2id (préféré à bcrypt) | Bon choix. Préciser les paramètres : mémoire 64 Mo, itérations 3, parallélisme 2 |
| 23.5 | Blocage progressif + captcha après 3 échecs | Correct. Ajouter la réponse à temps constant (§29.2.2) |
| 23.7 | Validation du type MIME réel par les premiers octets | Correct — l'extension ne prouve rien |
| 23.7 | Stockage hors de la racine web, servi par URL signée | Correct |
| 21 | Idempotence des webhooks de paiement | Essentiel. Préciser : contrainte d'unicité sur la référence de la passerelle |
| 25.2 | Page générique + alerte détaillée au super-admin | Bonne séparation entre ce que voit l'utilisateur et ce que reçoit l'exploitant |
| 26.2 | Mobile-first, tableaux transformés en cartes, cibles ≥ 44 px | Correct et complet |

### 3.2 Propositions à amender

| § | Proposition | Problème | Correctif |
|---|---|---|---|
| 23.5 | JWT RS256 pour l'authentification | En contexte **web**, un JWT doit être stocké quelque part : `localStorage` est lisible par XSS, un cookie revient à faire une session avec plus de complexité et **sans révocation immédiate** | **Cookie de session côté serveur pour le web** ; JWT RS256 réservé à **Flutter**, où il est justifié |
| 23.7 | Analyse antivirus « avant stockage définitif » | Une analyse ClamAV synchrone bloque l'utilisateur plusieurs secondes — contraire à §24.1 | Dépôt immédiat en **quarantaine**, analyse en tâche asynchrone, fichier rendu disponible après verdict, notification en cas de rejet |
| 23.9 | Sauvegardes quotidiennes | Une panne à 23 h perd une journée de **paiements** | Sauvegarde complète quotidienne **+ archivage continu des WAL** (restauration à un instant précis) et test de restauration trimestriel |
| 19.3 | QR code de session généré par le professeur | Un code statique affiché 10 minutes est **photographiable et transmissible** à un camarade absent. La fraude est triviale | QR **rotatif** (régénéré toutes les 10–15 s, type TOTP), et/ou validation par le réseau de l'établissement |
| 19.3 | Absence automatique si pas de pointage | Sans réseau, sans batterie ou sans smartphone, l'apprenant est marqué absent **à tort**, avec notification immédiate au parent (§19.4) | L'absence est **provisoire** jusqu'à la clôture de la séance par le professeur, qui voit la liste des non-pointés et confirme. La notification part après confirmation |
| 9.3 | Action « Supprimer » un tenant | Suppression physique = perte de données scolaires à durée de conservation légale, et perte des justificatifs de paiement | Suppression **logique**, export préalable obligatoire, purge différée après délai de rétention |
| 3.2 | Chiffrement AES-256-GCM des paramètres en *query string* | Complexité et risque cryptographique inutiles. Le cahier propose lui-même l'alternative dans la même puce | Retenir uniquement : **aucun identifiant sensible en *query string*** |
| 3.2 | « Ne jamais exposer d'IDs numériques » | Juste pour l'**exposition**, mais coûteux si appliqué aux clés primaires | Séparer les rôles : `id` interne numérique, `public_id` UUID exposé (§31 de l'addendum) |
| 5.3 | Couleurs personnalisées par l'école | Rien ne garantit la lisibilité : une école peut choisir un jaune sur fond blanc | L'école ne fournit que l'**accent** ; le texte et la teinte sont dérivés côté serveur avec contraste forcé ≥ 4,5:1, et un accent non rattrapable est refusé |

### 3.3 Propositions à écarter

| § | Proposition | Motif |
|---|---|---|
| 23.7 | **VirusTotal API** | Envoie le fichier à un tiers, qui le conserve et le partage avec sa communauté d'analyse. Il s'agit ici d'**extraits de naissance et de pièces d'identité de mineurs** (§15.4). Inacceptable juridiquement et éthiquement → **ClamAV auto-hébergé uniquement** |
| 23.1 | **`sqlmap` en CI** | Lent, bruyant, et sans valeur réelle si l'ORM est utilisé partout : il teste une faille que l'architecture exclut déjà. Le budget est mieux investi dans l'analyse statique et l'interdiction des requêtes brutes non paramétrées. **OWASP ZAP (§23.6) est conservé** : lui teste des classes de failles réellement présentes |
| 23.1 | Tests d'injection en CI/CD *« jamais en production »* | La restriction est juste, mais la formulation laisse croire qu'un pentest de production serait envisageable sans cadre. À remplacer par : **pentest externe sur environnement de préproduction iso-production**, avec autorisation écrite (§23.10 déjà prévu) |
| 27.3 | Choix ouvert Node **ou** Laravel | Un cahier des charges qui laisse la pile ouverte produit du code inapplicable — c'est précisément l'origine du défaut C-1. Le dépôt **est** un projet Laravel 13 : **trancher pour Laravel** et réécrire les exemples en conséquence |

---

## 4. Écarts entre le dépôt actuel et le cahier des charges

Le dépôt contient le squelette Laravel 13 par défaut, un seul commit, aucun code métier.

| # | Écart | Impact |
|---|---|---|
| D-1 | `DB_CONNECTION=sqlite` | §27.3 exige PostgreSQL. **RLS, index partiels et partitionnement sont impossibles en SQLite.** À corriger avant la première migration |
| D-2 | `CACHE_STORE=database`, `QUEUE_CONNECTION=database`, `SESSION_DRIVER=database` | Chaque lecture de cache et de session devient une requête SQL. Contraire à §24.1 et §24.4 → Redis |
| D-3 | `SESSION_ENCRYPT=false` | La charge de session contient des données d'élèves mineurs → `true` |
| D-4 | `.gitignore` ignore `.env` et `.env.production` mais **pas** `.env.staging` ni `.env.local` | Un secret de préproduction peut être commité sans alerte → motif `.env*` avec exception pour `.env.example` |
| D-5 | Aucun `routes/api.php` | L'API n'est pas installée (`php artisan install:api`). Aucune limitation de débit d'API active |
| D-6 | Aucun répertoire `.github/` | Ni CI, ni protection de branche, ni analyse de secrets. Tout §33 reste à mettre en place |
| D-7 | `README.md` est celui de Laravel par défaut | Aucune trace du projet réel ; §28 demande une documentation tenue à jour |

---

## 5. Plan de correction proposé, par ordre de dépendance

L'ordre compte : les points 1 et 2 sont irréversibles une fois des données en production.

1. **Fondations de base de données** — PostgreSQL, encodage et collation, `timestamptz`, partitionnement des tables à fort volume, stratégie `id` / `public_id`. *Changer ces choix après la mise en production impose une réécriture complète des tables.*
2. **Isolation multitenant** — trait de scope obligatoire, RLS PostgreSQL, suite de tests d'isolation. *À poser avant la première table métier, pas après.*
3. **Middleware de tenant corrigé** — C-2 à C-9.
4. **Socle de sécurité des API** — refus par défaut, politiques d'autorisation, réponses indistinguables, limitation de débit, détecteur de balayage.
5. **Chaîne GitHub** — protection de branche, CI bloquante, analyse de secrets, environnements et déploiement.
6. **Budgets de performance en CI** — comptage de requêtes, jeu de données de 100 000 lignes, seuils de latence.
7. **Design system** — jetons de la direction *Ivoire & Encre*, dérivation de l'accent par tenant avec contraste forcé.

---

*Fin du rapport.*
