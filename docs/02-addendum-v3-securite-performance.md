# Addendum v3 — Protection des API, secrets, identifiants, performance et mise en production

> **Statut** : normatif. Ce document complète et, sur certains points, **remplace** le cahier des charges v2 (`01-cahier-des-charges-v2.md`).
> **Version** : 3.0 — Septembre 2026
> **Stack de référence** : Laravel 13 / PHP 8.3 / PostgreSQL 16 / Redis 7 / Flutter (mobile), conformément au dépôt existant.

---

## A. Comment lire ce document

| Section de cet addendum | Effet sur la v2 |
|---|---|
| §29 Protection et non-découvrabilité des API | **Nouvelle section.** Complète §3.2 et §23.6 |
| §30 Gestion des secrets et du fichier `.env` | **Remplace** la 3ᵉ puce de §23.9 |
| §31 Stratégie d'identifiants (ID / UUID / identifiant métier) | **Remplace** la 1ʳᵉ et la 3ᵉ puce de §3.2. Complète §2.4 |
| §32 Performance garantie par construction | **Renforce** §24 et le rend vérifiable automatiquement |
| §33 GitHub, CI/CD et mise en production | **Remplace** la ligne « CI/CD » de §27.4 |
| §34 Corrections apportées aux propositions techniques de la v2 | Voir le rapport détaillé `03-rapport-evaluation-code.md` |

**Principe directeur ajouté aux bonnes pratiques (§28)** : *une exigence de sécurité ou de performance qui n'est pas vérifiée automatiquement par un test ou par la CI n'existe pas.* Chaque règle ci-dessous est accompagnée de son moyen de vérification.

---

## 29. Protection et non-découvrabilité des API

### 29.1 Ce qui est réellement atteignable — et ce qui ne l'est pas

La demande est : *empêcher qu'on puisse déterminer le nom des API à travers des requêtes.*

Il faut poser une limite honnête avant de spécifier : **une API consommée par un client public ne peut pas être secrète.** L'application web sert son propre JavaScript, et l'APK Flutter est décompilable ; quiconque installe l'application lit les URL qu'elle appelle. Toute spécification qui promettrait le contraire produirait une fausse sécurité.

La protection se construit donc sur deux axes distincts, à ne jamais confondre :

| Axe | Objectif | Efficacité |
|---|---|---|
| **Axe 1 — Non-découvrabilité** | Qu'un attaquant **sans compte** ne puisse pas cartographier l'API par balayage (ffuf, dirsearch, Burp Intruder) | Réelle et mesurable |
| **Axe 2 — Inutilité de la découverte** | Que connaître le nom d'un endpoint **ne serve à rien** sans autorisation | **C'est le vrai verrou.** Non négociable |

L'axe 2 prime. Une API dont tous les noms seraient publiés resterait sûre si l'autorisation est correcte ; une API parfaitement obscure mais sans contrôle d'accès fin est compromise dès la première fuite.

### 29.2 Axe 1 — Non-découvrabilité (obligations)

**29.2.1 Aucune surface d'inventaire**

- **Aucune route d'index** : ni `/api`, ni `/api/routes`, ni endpoint renvoyant la liste des ressources disponibles.
- **Aucune documentation OpenAPI/Swagger servie en production.** La documentation est générée en CI et publiée sur un espace privé (GitHub Pages privé ou artefact de build), jamais sur le domaine de production.
- **Outils de développement interdits en production** : Telescope, Horizon (UI), Debugbar, Tinker web, Ignition. S'ils sont nécessaires (Horizon pour les files d'attente), ils sont placés derrière authentification **et** liste blanche d'adresses IP, sur un sous-domaine distinct non lié.
- **`APP_DEBUG=false` obligatoire en production.** C'est le point le plus critique de toute cette section : la page d'erreur de développement de Laravel affiche la route, le contrôleur, la trace, les variables d'environnement et parfois le contenu de la requête. Une seule erreur 500 en mode debug annule tout le reste de cette section.
  - *Vérification* : test automatisé en CI qui échoue si `APP_DEBUG` n'est pas `false` dans la configuration de l'environnement `production` ; sonde de supervision qui alerte si la page d'erreur de production contient une trace.

**29.2.2 Réponses indistinguables**

C'est la mesure qui empêche réellement l'énumération.

- Une route **inexistante**, une route **existante mais interdite au rôle courant**, et une ressource **appartenant à un autre tenant** renvoient **exactement la même réponse** : `404`, corps identique, en-têtes identiques.
  - Conséquence : ne jamais renvoyer `403 Forbidden` sur une ressource dont l'existence est elle-même une information. `403` est réservé aux cas où l'existence de la ressource est déjà connue du demandeur légitimement.
- **Le temps de réponse doit être indistinguable lui aussi.** Un `404` immédiat sur route inexistante et un `404` après trois requêtes SQL sur ressource interdite se distinguent au chronomètre. Les réponses `404` de l'API sont normalisées par un délai plancher (ex. 80 ms) appliqué dans le gestionnaire d'exception.
- **Connexion** : matricule inconnu et mot de passe erroné renvoient le même message *et* consomment le même temps (hachage factice systématique quand l'utilisateur n'existe pas). Sans cela, on énumère les matricules valides d'un établissement.
- **Résolution de tenant** : un sous-domaine inexistant, suspendu, bloqué ou réservé renvoie la même page générique. Le message « École introuvable » de la v2 §3.1 permettait d'énumérer les écoles clientes et est **supprimé** (voir §34 et le rapport d'évaluation).

**29.2.3 Effacement des empreintes techniques**

- Suppression des en-têtes `X-Powered-By`, `Server` (valeur neutralisée dans Nginx via `server_tokens off` et `more_clear_headers`), et de tout en-tête propre au framework.
- Suppression du cookie de session par défaut nommé d'après le framework : `SESSION_COOKIE` porte un nom neutre (ex. `sid`).
- Les pages d'erreur ne portent aucune marque de framework (§25.4 déjà prévu — ici étendu aux réponses API en JSON).
- Le serveur web refuse l'accès à tout chemin commençant par un point (`location ~ /\.` → `deny all`), ainsi qu'à `/vendor`, `/storage/logs`, `/composer.json`, `/composer.lock`, `/package.json`, `/artisan`. La racine web est `public/` **uniquement**.
  - *Vérification* : test d'intégration en CI qui interroge une liste de chemins sensibles et échoue si l'un d'eux ne renvoie pas `404`.

**29.2.4 Détection et blocage du balayage**

- **Limitation de débit générale** sur toute l'API : 60 requêtes/minute par utilisateur authentifié, 20/minute par IP non authentifiée.
- **Limitation renforcée** sur les routes sensibles : connexion (5 essais puis blocage progressif exponentiel + captcha après 3 échecs — §23.5 conservé), réinitialisation de mot de passe, téléchargement de document, export, génération PDF.
- **Détecteur d'énumération** : au-delà de **20 réponses `404` en 60 secondes** pour une même IP ou un même compte, l'IP est bloquée 15 minutes (durée doublée à chaque récidive) et un événement de sécurité est journalisé. C'est cette règle, et non le renommage des routes, qui arrête réellement un balayage par dictionnaire.
- **Cloudflare WAF** en amont avec les règles managées OWASP activées et le mode « Bot Fight » (§23.8 conservé).
  - *Vérification* : test automatisé qui émet 25 requêtes vers des chemins aléatoires et vérifie que la 21ᵉ est bloquée.

**29.2.5 Nommage des routes**

- Toutes les routes API sont préfixées et versionnées : `/api/v1/...`.
- **Les noms de route ne reproduisent jamais les noms de tables ni de modèles.** On expose un vocabulaire métier stable, découplé du schéma : `/api/v1/apprenants`, pas `/api/v1/students` ni `/api/v1/tbl_eleve`.
- Aucun identifiant numérique interne dans les URL (voir §31).
- **Ce que cette mesure vaut réellement** : elle empêche de deviner la structure de la base à partir d'une URL, et elle rend inefficaces les listes de mots génériques. Elle **ne** protège **pas** contre la lecture du bundle JavaScript. Elle est nécessaire, pas suffisante — d'où l'axe 2.

**29.2.6 Restriction d'origine**

- **CORS strict** : seule l'origine du sous-domaine du tenant courant est acceptée ; aucun `Access-Control-Allow-Origin: *` nulle part, y compris sur les routes publiques.
- **CSP stricte** (§23.2 conservé) avec `default-src 'self'`, et sans `unsafe-inline` ni `unsafe-eval`.
- Vérification de `Origin`/`Referer` sur toute requête mutative (§23.3 conservé).

### 29.3 Axe 2 — Rendre la découverte inutile (obligations)

C'est la partie non négociable.

- **Refus par défaut.** Toute route API est authentifiée et autorisée sauf inscription explicite dans une liste blanche de routes publiques (vitrine, page de bienvenue, connexion, webhooks de paiement). La configuration doit faire échouer l'ajout d'une route non couverte, pas l'inverse.
- **Une politique d'autorisation (Policy) par modèle métier, sans exception.** Un `Gate::before` global refuse l'accès si aucune politique n'est enregistrée pour le modèle visé — le défaut est le refus, jamais l'autorisation.
- **Trois vérifications sur chaque accès à une ressource**, dans cet ordre :
  1. le tenant de la ressource est bien le tenant de la requête ;
  2. le rôle de l'utilisateur donne accès à ce type de ressource ;
  3. l'utilisateur a bien un lien avec **cette** ressource précise (son bulletin, son enfant, sa classe).
  La troisième est celle qu'on oublie et qui produit les IDOR.
- **Seconde barrière en base de données** : activation de la *Row-Level Security* PostgreSQL sur toutes les tables métier, avec une politique fondée sur une variable de session positionnée par le middleware de tenant. Ainsi, **même une requête qui oublierait le scope applicatif ne peut pas lire les données d'un autre établissement**. C'est l'application concrète du principe de défense en profondeur de §28.
- **Aucun identifiant fourni par le client n'est utilisé sans revérification.** Le `tenant_id` provient toujours du sous-domaine résolu côté serveur, jamais d'un paramètre, d'un en-tête ou d'un champ de formulaire.
  - *Vérification* : suite de tests d'isolation obligatoire — pour chaque endpoint, un test vérifie qu'un utilisateur du tenant A reçoit `404` sur une ressource du tenant B. Un endpoint sans ce test ne passe pas la revue.

### 29.4 Renforcement pour l'application mobile

- **Attestation d'application** : Play Integrity (Android) et App Attest (iOS) vérifiés côté serveur à l'ouverture de session. Une requête provenant d'un client non attesté est rejetée sur les opérations sensibles (pointage, paiement).
- **Signature de requête** : chaque appel mobile porte un en-tête `X-Signature` = HMAC-SHA256 du corps + horodatage + identifiant de session, avec une clé dérivée à l'ouverture de session et stockée dans `flutter_secure_storage`. Rejeu impossible (horodatage valide 60 s, `nonce` mémorisé dans Redis).
- **Épinglage de certificat** (certificate pinning) dans `dio`.
- Ces trois mesures sont **inapplicables au web** : le navigateur ne peut rien garder de secret. Le web s'appuie sur cookie de session `HttpOnly`/`Secure`/`SameSite=Strict`, CSRF et CSP.

### 29.5 Passerelle à opérations opaques — option évaluée et écartée en usage général

Une approche plus radicale a été envisagée : n'exposer **qu'un seul** endpoint (`POST /api/v1/gw`) recevant un corps chiffré contenant `{op: "<identifiant opaque>", params}`, l'`op` étant résolu côté serveur vers un gestionnaire.

| Avantages | Inconvénients |
|---|---|
| Une seule surface exposée, aucun nom métier en URL | Perte totale du cache HTTP et du CDN sur les lectures |
| Limitation de débit et journalisation centralisées | Perte des codes HTTP sémantiques (supervision dégradée) |
| Le balayage d'URL ne donne rien | Débogage et observabilité nettement plus difficiles |
| | Ne protège toujours pas : la liste des `op` est dans le client |

**Décision** : ne pas l'appliquer globalement — le coût en performance (§24.1 exige l'absence de latence perceptible) et en exploitabilité dépasse le gain, d'autant que le gain contre un attaquant disposant du client est nul.

**Elle est retenue pour un sous-ensemble restreint** d'opérations à fort enjeu, où le volume est faible et le cache inutile : initiation de paiement, réinitialisation de mot de passe, actions destructrices du super-admin (suspension, blocage, suppression de tenant), export de données personnelles. Sur ces opérations, le corps est chiffré (AES-256-GCM) et signé, et la réponse ne révèle rien de la structure interne.

### 29.6 Récapitulatif des vérifications automatiques exigées

| Exigence | Vérification |
|---|---|
| `APP_DEBUG=false` en production | Test CI + sonde de supervision |
| Chemins sensibles inaccessibles | Test d'intégration sur liste de chemins |
| Réponses `404` indistinguables | Test comparant corps, en-têtes et temps de réponse |
| Blocage du balayage | Test émettant 25 requêtes vers des chemins aléatoires |
| Aucune route sans politique d'autorisation | Test parcourant la table de routage |
| Isolation entre tenants | Un test par endpoint, obligatoire en revue |
| En-têtes techniques absents | Test d'intégration sur les en-têtes de réponse |
| Balayage de vulnérabilités | OWASP ZAP en mode baseline sur l'environnement de préproduction, à chaque publication |

---

## 30. Gestion des secrets et du fichier `.env`

> Remplace la 3ᵉ puce de §23.9 de la v2.

### 30.1 Règle fondatrice

**Le fichier `.env` de production n'existe dans aucun dépôt, aucun message, aucun ticket, aucune capture d'écran.** Il est *généré sur le serveur au moment du déploiement*, à partir de secrets chiffrés détenus par GitHub Environments (voir §33).

### 30.2 Empêcher la fuite par le dépôt

- `.gitignore` couvre **tous** les variants, pas seulement deux. Le fichier actuel du dépôt ignore `.env` et `.env.production` mais **laisserait passer `.env.staging`, `.env.local`, `.env.dev`** — défaut à corriger. Motif requis : `.env*` avec exception explicite pour `.env.example`.
- **`gitleaks` en CI**, bloquant, sur chaque *pull request* et sur l'historique complet à chaque fusion vers `main`.
- **GitHub Secret Scanning + Push Protection activés** sur le dépôt : GitHub refuse la poussée d'un commit contenant un jeton reconnu (clés Stripe, AWS, CinetPay…). Gratuit sur dépôt public, inclus dans GitHub Advanced Security sur dépôt privé — à activer dès la création du dépôt.
- **Procédure de fuite** : si un secret atteint un jour l'historique, la seule réponse valable est **la rotation immédiate du secret**, pas la réécriture de l'historique. Un secret poussé est un secret compromis, y compris si le commit est supprimé (les forks et les caches GitHub le conservent).

### 30.3 Empêcher la fuite par le serveur

- `.env` a les permissions **`600`**, propriétaire = l'utilisateur système de déploiement, groupe = celui de PHP-FPM en lecture seule si nécessaire.
- La racine web est `public/` : `.env` est mécaniquement hors de portée. Cette propriété est **vérifiée**, pas supposée — le serveur web refuse en plus tout chemin commençant par un point (§29.2.3).
- **`php artisan config:cache` à chaque déploiement.** Effet de bord essentiel : après mise en cache, `env()` retourne `null` hors des fichiers `config/`. Cela transforme en erreur détectable toute lecture d'environnement faite ailleurs, et **impose** la règle « `env()` uniquement dans `config/` ».
- Aucun endpoint, aucune commande, aucune page ne renvoie le contenu de la configuration. `phpinfo()` interdit.

### 30.4 Le piège `VITE_`

Toute variable préfixée **`VITE_`** est **compilée en clair dans le bundle JavaScript public**. Le `.env.example` du dépôt contient déjà `VITE_APP_NAME`.

- Règle : **aucune valeur sensible ne porte jamais le préfixe `VITE_`.** Clés d'API de paiement, secrets de webhook, identifiants de service : jamais.
- *Vérification* : règle CI qui échoue si une variable `VITE_*` correspond à un motif de secret (`*_KEY`, `*_SECRET`, `*_TOKEN`, `*_PASSWORD`).

### 30.5 Chiffrement et coffre-fort

Trois niveaux, à adopter dans cet ordre selon la maturité du projet :

| Niveau | Mécanisme | Quand |
|---|---|---|
| 1 — Minimum viable | **GitHub Environments + Secrets** chiffrés ; `.env` généré au déploiement | Dès le premier déploiement |
| 2 — Renforcé | **`php artisan env:encrypt`** : un `.env.<environnement>.encrypted` versionnable, déchiffré au déploiement avec une clé unique détenue en secret GitHub | Dès la mise en production |
| 3 — Cible | **Coffre-fort dédié** (Infisical auto-hébergé, Doppler ou AWS Secrets Manager) avec rotation, journal d'accès et révocation | À la deuxième école cliente |

Le niveau 3 apporte ce que GitHub Secrets ne donne pas : l'historique de qui a lu quel secret et quand, et la rotation sans redéploiement.

### 30.6 Cloisonnement et rotation

- **Un jeu de secrets par environnement.** Les secrets de production ne sont lisibles par aucun développeur : l'environnement GitHub `production` est protégé par *required reviewers*, et ses secrets ne sont injectés que dans les exécutions approuvées.
- **Rotation planifiée** : `APP_KEY` (annuelle, avec procédure de re-chiffrement des données chiffrées en base), mots de passe de base de données (trimestrielle), clés de signature JWT (semestrielle, avec période de recouvrement à deux clés), jetons de passerelles de paiement (selon le fournisseur).
- **Rotation d'urgence** : procédure écrite, testée une fois avant la mise en production, exécutable en moins de 30 minutes.
- Toute clé privée (JWT RS256, signature de documents) est stockée dans le coffre-fort, jamais dans le dépôt, et jamais transmise par messagerie.

### 30.7 Correctifs à apporter au `.env.example` du dépôt

Le fichier actuel est celui du squelette Laravel et contredit le cahier des charges sur cinq points :

| Actuel | Requis | Raison |
|---|---|---|
| `DB_CONNECTION=sqlite` | `pgsql` | §27.3 exige PostgreSQL ; RLS, index partiels et partitionnement (§32) sont impossibles en SQLite |
| `CACHE_STORE=database` | `redis` | Le cache en base ajoute des requêtes à chaque lecture — contraire à §24.1 |
| `QUEUE_CONNECTION=database` | `redis` | §24.4 prévoit Redis + files d'attente |
| `SESSION_ENCRYPT=false` | `true` | La charge de sessions contient des données d'élèves mineurs |
| `SESSION_DRIVER=database` | `redis` | Une lecture de session par requête, en base, sur chaque page |

À ajouter : `SESSION_COOKIE` (nom neutre), `SESSION_SECURE_COOKIE=true`, `SESSION_SAME_SITE=strict`, `APP_MAINTENANCE_DRIVER=cache`, les variables de tenant (`APP_DOMAIN`, `ADMIN_SUBDOMAIN`), les clés de passerelles de paiement (vides), les clés JWT (chemins vers les clés, pas les clés elles-mêmes).

---

## 31. Stratégie d'identifiants : ID interne, UUID public, identifiant métier

> Remplace la 1ʳᵉ et la 3ᵉ puce de §3.2 de la v2. Complète §2.4.

### 31.1 Le principe : trois identifiants, trois rôles

La v2 demandait de remplacer les identifiants numériques par des UUID. C'est juste pour l'exposition, mais coûteux si on l'applique aussi aux clés primaires. **La bonne réponse est de séparer les rôles** — ce qui est exactement l'intuition exprimée dans la demande : *chacun a sa particularité*.

| | **ID interne** | **UUID public** | **Identifiant métier** |
|---|---|---|---|
| Colonne | `id` | `public_id` | `matricule` / `ine` / `numero` |
| Type | `BIGSERIAL` (8 o) | `uuid` natif PostgreSQL (16 o) | `varchar`, format imposé par l'État ou l'école |
| Rôle | Clé primaire, clés étrangères, jointures, index | Seul identifiant exposé (URL, API, QR code) | Identification humaine et légale |
| Exposé ? | **Jamais** | Oui | Sur les documents officiels uniquement, jamais en URL |
| Unicité | Globale | Globale | **Par tenant** : `UNIQUE (tenant_id, matricule)` |
| Modifiable ? | Non | Non | Correction administrative tracée (§2.4) |

### 31.2 Pourquoi garder un ID numérique interne

C'est une décision de performance, et elle est mesurable :

- **8 octets contre 16.** Un `bigint` occupe la moitié d'un `uuid`. Comme chaque clé étrangère et chaque entrée d'index porte cette valeur, l'écart se multiplie par le nombre de relations.
- **Localité d'insertion.** Une séquence croissante insère toujours en fin d'index B-tree : une seule page chaude, pas de fragmentation. Un UUID v4 est aléatoire : chaque insertion touche une page différente, l'index se fragmente, et le taux de succès du cache s'effondre sur les tables à forte écriture — précisément `pointages`, `notes`, `messages`, `logs`.
- **Index plus petits = plus d'index en mémoire.** Sur la table `pointages` dimensionnée en §32.2 (≈ 108 M lignes/an à 100 écoles), la différence entre clés de 8 et 16 octets se compte en gigaoctets de cache.

Utiliser des UUID comme clés primaires sur ces tables serait la première cause de lenteur du produit — exactement ce que la demande veut éviter.

### 31.3 Pourquoi exposer un UUID et jamais l'ID

- **Anti-IDOR** : `/etudiant/1042/bulletin` invite à essayer `1041`. Un UUID v4 n'est pas devinable (122 bits d'entropie).
- **Anti-fuite de volumétrie** : un identifiant séquentiel révèle le nombre d'inscrits, le rythme d'inscription et l'ancienneté d'un dossier. C'est une information commerciale et personnelle qui n'a pas à circuler.
- L'UUID public ne dispense évidemment **pas** de la vérification d'autorisation (§29.3) : il rend l'énumération impraticable, il ne remplace pas le contrôle.

### 31.4 UUID v4 ou ULID / UUID v7 — arbitrage

Les identifiants triables par le temps (ULID, UUID v7) ont une meilleure localité d'insertion. Mais **ils encodent l'horodatage de création et le rendent lisible par quiconque reçoit l'identifiant**.

| Type de ressource | Choix | Motif |
|---|---|---|
| Apprenant, professeur, parent, document du dossier, paiement, reçu, bulletin | **UUID v4** | La date de création est une donnée personnelle ; aucune information ne doit être dérivable de l'identifiant |
| Session de cours, pointage, notification, entrée de journal | **ULID** | L'horodatage n'est pas sensible (il est déjà affiché), et la localité d'insertion compte sur ces tables à fort volume |

Par défaut, en cas de doute : **UUID v4**.

### 31.5 Règles de mise en œuvre

- Le `public_id` est **`NOT NULL`, `UNIQUE`, indexé**, et généré à la création de l'enregistrement.
- Stockage en type **`uuid` natif PostgreSQL**, jamais en `varchar(36)` : 16 octets contre 37, et comparaison entière au lieu de comparaison de chaîne.
- **La résolution de route se fait par `public_id`, toujours scopée par `tenant_id`.** Un `public_id` valide appartenant à un autre établissement doit produire un `404` identique à celui d'un identifiant inexistant (§29.2.2).
- **Aucune réponse d'API ne contient jamais `id`.** Les ressources sérialisées exposent `public_id` sous le nom `id` ; le champ interne est exclu au niveau de la couche de sérialisation, pas au cas par cas.
  - *Vérification* : test qui parcourt les réponses des endpoints principaux et échoue si une clé `id` contient une valeur numérique.
- **Les clés étrangères utilisent l'`id` interne**, jamais le `public_id` : les jointures restent sur 8 octets.

### 31.6 Identifiants métier et numéros de documents

- **Matricule (élève) / INE (étudiant)** : `UNIQUE (tenant_id, matricule)`. Ils servent à l'authentification (§2.4) et figurent sur les documents officiels, mais **ne sont jamais utilisés comme segment d'URL** — ils sont souvent séquentiels, donc devinables, et constituent une donnée personnelle.
- **Numéros de documents** (reçu, bulletin, certificat) : séquence **par tenant et par année scolaire**, format lisible et vérifiable : `REC-2026-000148`. Ils sont imprimés sur le document et servent à la vérification par QR code.
  - L'URL de téléchargement n'utilise **ni** ce numéro **ni** le matricule : elle utilise le `public_id` **et** une URL signée à durée limitée (§3.2 de la v2, conservé).
  - La séquence est générée sous verrou transactionnel pour éviter les trous et les doublons en cas de paiements simultanés.
- **QR code de vérification** d'un bulletin ou d'un reçu : il pointe vers une URL publique contenant un jeton de vérification à usage non authentifié qui affiche **uniquement** l'authenticité du document (émetteur, date, numéro, empreinte), jamais les notes ni les données personnelles.

### 31.7 Tableau d'application par entité

| Entité | `id` interne | `public_id` | Identifiant métier |
|---|---|---|---|
| Tenant (établissement) | ✔ | ✔ (UUID v4) | `slug` (unique global, liste de sous-domaines réservés) |
| Apprenant | ✔ | ✔ (UUID v4) | matricule / INE, unique par tenant |
| Professeur, personnel | ✔ | ✔ (UUID v4) | matricule RH, unique par tenant |
| Parent | ✔ | ✔ (UUID v4) | — |
| Classe, filière, matière | ✔ | ✔ (UUID v4) | code, unique par tenant |
| Note, bulletin | ✔ | ✔ (UUID v4) | n° de bulletin pour le bulletin |
| Paiement, reçu | ✔ | ✔ (UUID v4) | n° de reçu + référence de la passerelle |
| Document du dossier | ✔ | ✔ (UUID v4) | — |
| Session de cours | ✔ | ✔ (ULID) | — |
| Pointage | ✔ | ✔ (ULID) | — |
| Message | ✔ | ✔ (ULID) | — |
| Journal d'audit | ✔ | ✔ (ULID) | — |

---

## 32. Performance garantie par construction

> Renforce §24 de la v2 et la rend vérifiable. Objectif inchangé : **aucune lenteur perceptible**, dès la première ligne de schéma.

### 32.1 Les quatre règles inviolables

1. **Aucune migration ne crée une table sans ses index.** Une clé étrangère sans index, une colonne de filtre sans index, une colonne de tri sans index : la migration est refusée en revue.
2. **`tenant_id` est en première position de tout index composé.** Tous les scopes commencent par lui ; un index qui ne le porte pas en tête ne sera pas utilisé.
3. **Aucune pagination par `OFFSET` sur une liste métier.** Pagination par curseur exclusivement (`cursorPaginate`). L'`OFFSET` lit et jette toutes les lignes précédentes : à la page 400, il en lit 10 000 pour en rendre 25.
4. **Aucune requête N+1 ne peut atteindre `main`.** Le chargement paresseux est **désactivé** en développement et en test (`Model::preventLazyLoading()`), ce qui fait échouer immédiatement tout accès à une relation non préchargée. C'est le seul dispositif qui tient dans la durée — une convention de revue ne tient pas.

### 32.2 Dimensionnement : où la lenteur apparaîtra réellement

Hypothèses de charge : 1 000 apprenants par école, 6 séances de cours par jour, 180 jours de classe par an.

| Table | Lignes / an / école | À 100 écoles | Conséquence |
|---|---|---|---|
| `pointages` | ≈ 1 080 000 | ≈ **108 M / an** | **Partitionnement obligatoire** |
| `absences` | ≈ 54 000 (5 % des séances) | ≈ 5,4 M / an | Index partiel sur l'année courante |
| `notes` | ≈ 216 000 | ≈ 21,6 M / an | Index composé + archivage annuel |
| `messages` | ≈ 150 000 | ≈ 15 M / an | Partitionnement par date |
| `journal_audit` | ≈ 500 000 | ≈ 50 M / an | Partitionnement + purge à 24 mois |

**C'est `pointages` qui décidera de la performance du produit.** Une table de 100 millions de lignes sans partitionnement rend lente chaque consultation d'assiduité, chaque calcul de paie professeur et chaque bulletin.

**Décisions structurantes, à prendre dès la première migration** (les changer plus tard impose une réécriture complète de la table) :

- **Partitionnement déclaratif PostgreSQL par année scolaire** sur `pointages`, `absences`, `messages` et `journal_audit`. Toutes les requêtes portant sur l'année courante ne touchent qu'une partition.
- **Index partiels** sur l'année scolaire en cours pour les tables non partitionnées.
- **Encodage et collation fixés à la création de la base** (`UTF8`, collation déterministe). Les modifier ultérieurement impose une réindexation totale.
- **Fuseau horaire** : stockage en UTC (`timestamptz`), conversion à l'affichage. Une école à cheval sur deux fuseaux (multi-campus, plan Enterprise §5.2) casse toute logique de pointage en heure locale stockée.

### 32.3 Index requis dès la première migration

| Table | Index |
|---|---|
| Toutes | `tenant_id` (et en tête de chaque index composé) |
| `apprenants` | `(tenant_id, nom)`, `(tenant_id, matricule)` **unique**, `(tenant_id, classe_id)`, `(tenant_id, statut)`, `public_id` unique |
| `notes` | `(tenant_id, apprenant_id, trimestre_id)`, `(tenant_id, classe_id, matiere_id, trimestre_id)` |
| `pointages` | `(tenant_id, session_id)`, `(tenant_id, apprenant_id, date)`, `(tenant_id, professeur_id, date)` |
| `absences` | `(tenant_id, apprenant_id, statut_justification)`, `(tenant_id, classe_id, date)` |
| `paiements` | `(tenant_id, apprenant_id, statut)`, `(tenant_id, date)`, référence passerelle **unique** (idempotence) |
| `messages` | `(tenant_id, destinataire_id, lu, created_at)` |
| `documents` | `(tenant_id, apprenant_id)`, `public_id` unique |
| `sessions_cours` | `(tenant_id, date, classe_id)`, `(tenant_id, professeur_id, date)` |

### 32.4 Budgets de performance, vérifiés en intégration continue

Les objectifs de §24.1 deviennent des seuils qui font échouer la CI :

| Budget | Seuil | Vérification |
|---|---|---|
| Requêtes SQL par endpoint | ≤ **10** | Test qui compte les requêtes et échoue au-delà |
| Latence p95 des endpoints de liste | ≤ **300 ms** sur jeu de données de 100 000 lignes | Test de charge k6 en CI nocturne |
| Latence p95 des endpoints de détail | ≤ **150 ms** | idem |
| Poids JS initial par route | ≤ **180 ko** compressés | Budget Vite, échec du build au-delà |
| Requête la plus lente | ≤ **200 ms** | `auto_explain` actif en préproduction, alerte au-delà |

Le jeu de données de test contient **au minimum 100 000 apprenants répartis sur 50 tenants**, généré par *seeder*. Tester la performance sur 20 lignes ne révèle rien.

### 32.5 Autres mesures back-end

- **Redis dès le premier jour** pour le cache, les sessions et les files d'attente (corrige le `.env.example`, §30.7).
- **Le tenant résolu est mis en cache** (clé `tenant:slug:<slug>`, TTL 5 min, invalidation à toute modification du tenant). Sans cela, chaque requête HTTP lit la table `tenants` — défaut relevé dans le code de la v2 §3.1 (voir rapport d'évaluation).
- **Aucun `COUNT(*)` sur une grande table pour paginer.** La pagination par curseur ne l'exige pas. Les compteurs affichés (effectif d'une classe, nombre d'impayés) sont **dénormalisés** et mis à jour par événement.
- **Aucun `SELECT *` sur les listes** : colonnes explicites. Les photos, les descriptions longues et les champs `text` ne sont chargés que sur la fiche de détail.
- **Tâches asynchrones obligatoires** (§24.4 conservé, étendu) : génération de bulletins, exports > 5 000 lignes, envois groupés, **et l'analyse antivirus des fichiers déposés** (voir rapport d'évaluation — l'analyse synchrone bloquerait l'utilisateur plusieurs secondes).
- **PgBouncer** en *transaction pooling* devant PostgreSQL : PHP-FPM ouvre une connexion par processus, la base sature avant le CPU.
- **`pg_stat_statements` activé** dès la préproduction ; revue mensuelle des dix requêtes les plus coûteuses.

### 32.6 Mesures front-end

Celles de §24.3 sont conservées et complétées :

- **Virtualisation obligatoire** au-delà de 100 lignes affichées (TanStack Virtual).
- **Recherche différée** de 300 ms (§9.4 conservé) **et annulation de la requête précédente** — sans annulation, une frappe rapide produit des réponses qui arrivent dans le désordre.
- **Interface optimiste** sur les actions à faible risque uniquement (marquer comme lu). Jamais sur un paiement ni sur un pointage : afficher un succès non confirmé sur un pointage produirait une absence contestée.
- **Squelettes de chargement** plutôt que des indicateurs tournants : la page ne doit pas se réorganiser à l'arrivée des données (pas de décalage de mise en page).

---

## 33. GitHub, CI/CD et mise en production

> Remplace la ligne « CI/CD » de §27.4.

### 33.1 Réponse à la question posée : oui, mais GitHub n'héberge pas l'application

| GitHub prend en charge | GitHub ne prend pas en charge |
|---|---|
| Hébergement du code, branches, revues | Servir l'application → **VPS** (Hetzner / DigitalOcean) + Nginx + PHP-FPM |
| Intégration continue : tests, lint, analyse statique, audits de dépendances, ZAP | CDN, WAF, protection DDoS, SSL joker → **Cloudflare** |
| Stockage chiffré des secrets (Environments) | Rotation et journal d'accès aux secrets → coffre-fort (§30.5 niveau 3) |
| Déclenchement et orchestration du déploiement | Sauvegardes de la base → tâche planifiée + stockage objet chiffré |
| Dependabot, analyse de secrets, protection de poussée | Supervision applicative → Sentry |

### 33.2 Organisation du dépôt

- **Branches** : `main` (= production, toujours déployable), branches de fonctionnalité courtes, fusion par *pull request*.
- **Protection de `main`** : *pull request* obligatoire, au moins une revue approuvée, tous les contrôles verts, poussée forcée interdite, historique linéaire.
- **Étiquettes de version** (`v1.4.0`) sur chaque déploiement en production, pour savoir exactement ce qui tourne et pouvoir revenir en arrière.
- **`CODEOWNERS`** sur `database/migrations/`, `config/`, `.github/workflows/` et tout ce qui touche à l'authentification : ces chemins exigent la revue d'un responsable.

### 33.3 Chaîne d'intégration continue

Sur chaque *pull request*, bloquants :

1. **Lint** — Laravel Pint.
2. **Analyse statique** — Larastan au niveau maximal.
3. **Tests** — unitaires et fonctionnels sur PostgreSQL (jamais SQLite : les comportements diffèrent sur les contraintes, les types et les transactions).
4. **Tests d'isolation multitenant** — suite dédiée, obligatoire (§29.3).
5. **Budgets de performance** — comptage de requêtes, poids des bundles (§32.4).
6. **Audits de sécurité** — `composer audit`, `npm audit`, **gitleaks**.
7. **Vérification de configuration** — `APP_DEBUG=false`, absence de `VITE_*` sensible, chemins interdits inaccessibles (§29.6).

En nocturne, sur la préproduction : **OWASP ZAP baseline** et **test de charge k6**.

### 33.4 Chaîne de déploiement

- **Deux environnements GitHub** : `staging` (déploiement automatique à chaque fusion sur `main`) et `production` (déploiement manuel, **required reviewers**). Les secrets de production ne sont injectés que dans une exécution approuvée.
- **Déploiement sans interruption** : structure `releases/` + lien symbolique `current`, basculé après la préparation complète. `php-fpm reload` et purge d'OPcache à la bascule. **Retour arrière = rebascule du lien symbolique**, quelques secondes.
- **Le `.env` est écrit sur le serveur à ce moment-là**, depuis les secrets GitHub, en permissions `600` (§30).
- **Migrations rétro-compatibles** (modèle *expand / contract*) : on ajoute d'abord, on déploie, on migre les données, puis on retire au déploiement suivant. Sans cela, le retour arrière est impossible — l'ancien code ne sait pas lire le nouveau schéma.
- **Sauvegarde automatique de la base immédiatement avant toute migration**, avec vérification que la sauvegarde est exploitable.
- **Migrations exécutées une seule fois** même sur plusieurs serveurs (verrou applicatif).

### 33.5 Sauvegardes et restauration

§23.9 prévoyait une sauvegarde quotidienne. **C'est insuffisant pour une plateforme qui traite des paiements** : une panne à 23 h perdrait une journée de transactions.

- **Sauvegarde complète quotidienne + archivage continu des journaux de transaction (WAL)**, permettant une restauration à un instant précis (PITR) avec une perte maximale de quelques minutes.
- Sauvegardes **chiffrées**, stockées hors du serveur d'application, rétention 30 jours.
- **Restauration testée tous les trimestres**, sur un environnement jetable, avec mesure du temps de restauration. Une sauvegarde jamais restaurée n'est pas une sauvegarde.

### 33.6 Alternative allégée

Si l'équipe d'exploitation est réduite, **Laravel Forge** ou **Ploi** pilotent le VPS (Nginx, PHP, certificats, files d'attente, sauvegardes) et se déclenchent depuis GitHub Actions. On conserve toute la chaîne d'intégration continue ci-dessus et on délègue l'administration système. C'est le choix recommandé pour démarrer.

---

## 34. Corrections apportées aux propositions techniques de la v2

Le détail, avec justification et correctif proposé pour chaque point, figure dans **`03-rapport-evaluation-code.md`**. Synthèse des éléments **normatifs** qui en découlent :

- Le middleware de résolution de tenant de §3.1 est **remplacé** : validation de l'en-tête `Host` contre une liste blanche, sous-domaines réservés, vérification du statut d'abonnement, mise en cache, réponse générique, exposition d'un objet restreint.
- Le chiffrement AES-256-GCM de paramètres en *query string* (§3.2) est **retiré** au profit de la règle simple « aucun identifiant sensible en *query string* ».
- `sqlmap` en intégration continue (§23.1) est **retiré** au profit de l'analyse statique et de l'interdiction des requêtes brutes non paramétrées.
- **VirusTotal est écarté** (§23.7) : transmettre à un tiers des pièces d'identité de mineurs est inacceptable. ClamAV auto-hébergé, en tâche asynchrone, fichier en quarantaine jusqu'au verdict.
- **Authentification web par cookie de session** plutôt que par JWT ; le JWT RS256 de §23.5 est **réservé à l'application mobile**.
- **QR code de pointage rendu rotatif** (§19.3) : un code statique est photographiable et transmissible à un camarade absent.
- **L'absence automatique devient provisoire** jusqu'à la clôture de la séance par le professeur (§19.3) : en l'état, une panne de réseau ou de batterie produit une absence injustifiée.
- **La suppression d'un tenant devient logique** (§9.3), avec export préalable et purge différée : les données scolaires ont une durée de conservation légale.

---

*Fin de l'addendum v3.0*
