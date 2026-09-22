# Cahier des Charges — Plateforme de Gestion Scolaire Multitenant

> **Document de référence pour l'IA de développement**
> Version : 2.0 — Juillet 2026
> Statut : Spécification complète (web + mobile)

---

## Table des matières

1. [Présentation du projet](#1-présentation-du-projet)
2. [Types d'établissement : Élève vs Étudiant](#2-types-détablissement--élève-vs-étudiant)
3. [Architecture multitenant, URLs & Protection des routes](#3-architecture-multitenant-urls--protection-des-routes)
4. [Pages publiques & Vitrine SaaS](#4-pages-publiques--vitrine-saas)
5. [Inscription de l'établissement & Choix de pack](#5-inscription-de-létablissement--choix-de-pack)
6. [Page de bienvenue par école](#6-page-de-bienvenue-par-école)
7. [Page de sélection de rôle & Connexion](#7-page-de-sélection-de-rôle--connexion)
8. [Hiérarchie des rôles & Permissions](#8-hiérarchie-des-rôles--permissions)
9. [Espace Super-Admin](#9-espace-super-admin)
10. [Espace Directeur](#10-espace-directeur)
11. [Espace Secrétariat](#11-espace-secrétariat)
12. [Espace Comptabilité](#12-espace-comptabilité)
13. [Espace Ressources Humaines](#13-espace-ressources-humaines)
14. [Espace Professeur](#14-espace-professeur)
15. [Espace Étudiant / Élève](#15-espace-étudiant--élève)
16. [Espace Parent](#16-espace-parent)
17. [Module Messagerie Interne](#17-module-messagerie-interne)
18. [Module Classement & Meilleurs Élèves](#18-module-classement--meilleurs-élèves)
19. [Module Pointage & Gestion automatique des absences](#19-module-pointage--gestion-automatique-des-absences)
20. [Moteur de Calcul des Moyennes](#20-moteur-de-calcul-des-moyennes)
21. [Module Paiements](#21-module-paiements)
22. [Application Mobile Flutter](#22-application-mobile-flutter)
23. [Sécurité renforcée & Attaques courantes](#23-sécurité-renforcée--attaques-courantes)
24. [Performance & Optimisation](#24-performance--optimisation)
25. [Gestion des erreurs & Page de maintenance](#25-gestion-des-erreurs--page-de-maintenance)
26. [Design Responsive](#26-design-responsive)
27. [Stack Technique Recommandée](#27-stack-technique-recommandée)
28. [Bonnes pratiques générales](#28-bonnes-pratiques-générales)

---

## 1. Présentation du projet

### 1.1 Description générale

Application de gestion scolaire **multitenant SaaS** (web + mobile Flutter) destinée à tout type d'établissement d'enseignement : collèges, lycées, universités, grandes écoles. Chaque établissement souscrit un abonnement et obtient un espace isolé avec sa propre URL, son propre branding, ses propres données.

### 1.2 Objectifs

- Centraliser toutes les informations scolaires dans une seule plateforme
- Adapter automatiquement le vocabulaire et les champs selon le type d'établissement (Élève / Étudiant)
- Permettre à chaque acteur d'accéder à son espace dédié (web et mobile)
- Automatiser les calculs (moyennes, bulletins, paies) et le **pointage/les absences**
- Faciliter la communication inter-rôles via messagerie interne
- Offrir une page vitrine publique propre à chaque école
- Garantir une sécurité, une performance et une disponibilité de niveau production

### 1.3 Principes fondamentaux

- **Isolation totale des données** entre tenants
- **URL personnalisée** par établissement, routes protégées/obfusquées
- **Branding personnalisable**, avec des couleurs par défaut issues de la charte de l'application
- **Calcul et pointage automatiques** (moyennes, absences, présence)
- **Traçabilité** complète (logs, horodatage)
- **Application rapide** : aucun temps de chargement perceptible, pagination et index systématiques
- **Disponible sur web et mobile (Flutter)**

---

## 2. Types d'établissement : Élève vs Étudiant

### 2.1 Distinction fondamentale

La plateforme doit différencier deux catégories d'apprenants selon le niveau de l'établissement :

| Catégorie | Niveau | Identifiant utilisé |
|-----------|--------|---------------------|
| **Élève** | Premier cycle (collège) et second cycle (lycée) | **Matricule** délivré par l'État (Éducation Nationale) |
| **Étudiant** | Enseignement supérieur (université, grande école, institut) | **Identifiant** délivré par l'État ou par l'école (numéro étudiant / INE) |

Le vocabulaire, les champs de formulaire, et les libellés d'interface s'adaptent automatiquement selon le type d'entité choisi à la création de l'établissement.

### 2.2 Paramétrage du type d'entité (à la création de l'établissement)

Ajout obligatoire dans le formulaire d'inscription de l'établissement (super-admin ou inscription publique) — voir section 5.

**Champ : Type d'entité** (liste déroulante, obligatoire)

| Valeur | Libellé affiché | Cycle |
|--------|-----------------|-------|
| `college` | Collège (1er cycle secondaire) | Élève |
| `lycee` | Lycée (2nd cycle secondaire) | Élève |
| `college_lycee` | Collège & Lycée (établissement mixte) | Élève |
| `universite` | Université | Étudiant |
| `grande_ecole` | Grande École / Institut supérieur | Étudiant |
| `formation_pro` | Centre de formation professionnelle | Étudiant |

Ce choix détermine :
- Le terme utilisé partout dans l'interface de ce tenant : "Élève" ou "Étudiant"
- Le champ d'identification requis à l'inscription (matricule d'État vs identifiant étudiant)
- La structure des niveaux disponibles (6ème → Terminale pour collège/lycée ; L1 → Doctorat pour supérieur)
- Les champs additionnels du dossier d'inscription (voir 2.3)

### 2.3 Champs d'inscription spécifiques

#### Élève (collège / lycée)

| Champ | Type | Obligatoire |
|-------|------|-------------|
| Matricule national (fourni par l'État) | Texte, unique par élève | Oui |
| Nom, Prénom(s) | Texte | Oui |
| Date et lieu de naissance | Date / Texte | Oui |
| Sexe | Liste | Oui |
| Nom du tuteur/parent | Texte | Oui |
| Contact du tuteur/parent | Téléphone | Oui |
| Classe | Liste (dépend du niveau) | Oui |
| Établissement précédent | Texte | Non |
| Photo | Upload | Non |
| Mot de passe | Texte (généré ou choisi) | Oui |

#### Étudiant (université / grande école)

| Champ | Type | Obligatoire |
|-------|------|-------------|
| Identifiant national / numéro étudiant (INE) | Texte, unique par étudiant | Oui |
| Nom, Prénom(s) | Texte | Oui |
| Date et lieu de naissance | Date / Texte | Oui |
| Sexe | Liste | Oui |
| Filière | Liste | Oui |
| Niveau (L1, L2, M1…) | Liste | Oui |
| Contact personnel | Téléphone / Email | Oui |
| Diplôme précédent | Texte / Upload | Non |
| Photo | Upload | Non |
| Mot de passe | Texte (généré ou choisi) | Oui |

### 2.4 Rôle du matricule / identifiant

Le **matricule** (élève) ou l'**identifiant** (étudiant), combiné au **mot de passe**, constitue le couple d'authentification unique pour se connecter à la plateforme — il remplace l'email comme identifiant de connexion pour ce rôle. Ce couple sert aussi de clé de vérification lors de l'inscription en ligne (voir section 15.3) pour rattacher un compte à un dossier déjà pré-enregistré par le secrétariat, le cas échéant.

- Le matricule/identifiant est **unique par tenant** (unicité vérifiée à l'inscription)
- Non modifiable une fois attribué (sauf correction administrative avec traçabilité)
- Affiché sur tous les documents officiels générés (bulletin, certificat, reçu)

---

## 3. Architecture multitenant, URLs & Protection des routes

### 3.1 Stratégie d'URL par école

```
https://lycee-excellence.votreplateforme.com
https://igs-abidjan.votreplateforme.com
```

- Wildcard DNS `*.votreplateforme.com`
- Certificat SSL wildcard (Let's Encrypt / Cloudflare)
- Middleware de résolution de tenant à partir du sous-domaine (voir exemple de code section 3.2 de la v1 — conservé)

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

### 3.2 Protection et obfuscation des URLs

**Objectif** : empêcher un utilisateur malveillant de déduire des informations sensibles (identifiants internes, structure de la base) en lisant l'URL, et empêcher l'énumération d'IDs (IDOR).

**Mesures obligatoires**

- **Ne jamais exposer d'IDs numériques auto-incrémentés dans les URLs.** Utiliser des **UUID v4** ou des identifiants encodés (ex : Hashids, ou slugs aléatoires de type `nanoid`) pour toute ressource référencée en URL.
  - Mauvais : `/etudiant/1042/bulletin`
  - Bon : `/etudiant/8f2a1c3e-4b7d-4e2a-9f1a-2d3c4e5f6a7b/bulletin`
- **Routes signées et à durée limitée** pour les ressources sensibles téléchargeables (bulletins PDF, reçus, documents du dossier) : utiliser des **URLs signées temporaires** (type AWS S3 pre-signed URL, ou JWT à courte durée intégré dans l'URL), expirant après quelques minutes.
- **Chiffrement des paramètres sensibles** : si un identifiant doit transiter en query string, le chiffrer (AES-256-GCM) côté serveur avant de l'exposer, et le déchiffrer à la réception. Alternative plus simple et recommandée : ne jamais mettre d'ID sensible en query string, toujours en paramètre de route encodé (UUID).
- **Masquage de la stack technique** : supprimer les headers révélateurs (`X-Powered-By`, version de Laravel/Node, etc.)
- **Rate limiting par IP et par utilisateur** sur toutes les routes sensibles (login, reset mot de passe, téléchargement de documents) pour empêcher l'énumération par force brute.
- **Vérification systématique de propriété** : chaque requête sur une ressource doit vérifier que `tenant_id` ET l'utilisateur courant sont bien autorisés à accéder à cette ressource précise (pas seulement l'authentification, mais l'autorisation fine).

### 3.3 Base de données multitenant

Conservé de la v1 : base partagée avec colonne `tenant_id` sur toutes les tables, scope global ORM appliqué systématiquement (voir section 23.2 pour le renforcement anti-injection).

---

## 4. Pages publiques & Vitrine SaaS

*(Contenu inchangé par rapport à la v1 — voir Annexe C pour le rappel synthétique)*

Page marketing du SaaS (`https://votreplateforme.com`) : hero animé, section fonctionnalités, aperçu classement/podium, témoignages, tarifs, CTA final. Animations scroll-triggered (Framer Motion / GSAP), compteurs animés, chargement paresseux (lazy load).

---

## 5. Inscription de l'établissement & Choix de pack

### 5.1 Flux d'inscription complet

```
[Vitrine] → [Sélection de pack] → [Formulaire multi-étapes] → [Paiement] → [Confirmation] → [Page de bienvenue de l'école]
```

### 5.2 Page de sélection de pack

| Pack | Durée | Fonctionnalités |
|------|-------|-----------------|
| **Démo** | 1 mois | Gratuit, accès complet limité à 50 apprenants, filigrane "Démo" |
| **Starter** | 3 mois | Jusqu'à 200 apprenants |
| **Annuel** | 12 mois | Jusqu'à 1000 apprenants, réduction ~20% |
| **Pro** | 24 mois | Illimité + support prioritaire, réduction ~30% |
| **Enterprise** | Durée totale / sur devis | Multi-campus, API, SLA garanti |

### 5.3 Formulaire d'inscription multi-étapes

**Étape 1 — Informations de l'établissement**
- Nom officiel
- **Type d'entité** (liste déroulante — voir section 2.2) : détermine Élève ou Étudiant pour tout le tenant
- Pays, ville, adresse, téléphone, email
- Génération automatique du slug
- Upload du logo

**Étape 2 — Personnalisation**
- Couleur primaire / secondaire (color picker)
- **Par défaut, les couleurs de l'application (charte graphique de la plateforme) sont pré-appliquées** ; l'école peut les personnaliser ensuite, mais rien n'est laissé vide ou incohérent si elle ne modifie rien
- Description courte de l'école
- Aperçu en temps réel du branding

**Étape 3 — Compte Directeur**
- Nom, prénom, email, mot de passe, téléphone

**Étape 4 — Paiement** *(sauf Démo)*
- Orange Money, Wave, CinetPay, Stripe

**Étape 5 — Confirmation**
- URL de l'école, identifiants du directeur, email de confirmation

---

## 6. Page de bienvenue par école

*(Contenu inchangé de la v1)*

`https://[slug].votreplateforme.com` — page publique sans connexion : en-tête avec logo et couleurs du tenant (couleurs par défaut de l'application si non personnalisées), section héro animée, présentation, filières, pied de page, bouton "Se connecter".

---

## 7. Page de sélection de rôle & Connexion

*(Contenu inchangé de la v1)*

`https://[slug].votreplateforme.com/login` — cartes : Élève/Étudiant *(libellé adapté au type d'entité du tenant)*, Parent, Enseignant, Administration. Rôles sensibles (Directeur, Super-Admin) jamais affichés publiquement. Le vrai contrôle est fait côté serveur après authentification.

---

## 8. Hiérarchie des rôles & Permissions

```
Super-Admin (propriétaire SaaS)
  └── Directeur (par école)
        ├── Secrétariat
        ├── Comptabilité
        └── RH / Direction
              └── Professeur
                    ├── Étudiant / Élève
                    └── Parent
```

> **Modules retirés de cette version** : Espace Vie Scolaire (fusionné dans Secrétariat pour les absences/discipline, voir section 19) et Module Conseil Estudiantin & Activités (supprimé — pas de gestion d'activités par les étudiants dans cette version).

### Matrice des permissions de messagerie

| Émetteur | Peut écrire à |
|----------|--------------|
| Étudiant/Élève | Professeurs de ses classes, Secrétariat, Comptabilité, Directeur |
| Parent | Secrétariat, Comptabilité, Directeur, Professeurs de son enfant |
| Professeur | Secrétariat, Directeur, RH, Étudiants/Élèves de ses classes, Parents |
| Secrétariat | Tous |
| Comptabilité | Professeurs, Directeur, Parents (rappels) |
| Directeur | Tous |
| Super-Admin | Directeurs uniquement |

---

## 9. Espace Super-Admin

### 9.1 URL d'accès

```
https://admin.votreplateforme.com
```

### 9.2 Tableau de bord global

*(Inchangé de la v1)* : nombre d'établissements, MRR, utilisateurs actifs, alertes d'expiration, log des actions critiques.

### 9.3 Gestion des tenants (établissements)

**Liste des établissements**

Tableau avec colonnes :

| Colonne | Détail |
|---------|--------|
| Nom de l'école | |
| Type d'entité | Collège / Lycée / Université / Grande École… |
| **Directeur(s)** | **Nom et prénom du ou des directeurs rattachés au tenant** (nouveau champ, affiché avec avatar + email, plusieurs directeurs possibles si co-direction) |
| Slug / URL | |
| Plan | |
| Date d'expiration | |
| Statut | Actif / Suspendu / Bloqué / Démo |
| Nb d'apprenants | |
| Actions | Voir, Modifier, Suspendre, Bloquer, Avertir, Supprimer |

- Filtres : statut, plan, type d'entité, date d'expiration
- Recherche par nom, slug, ou nom de directeur
- **Pagination côté serveur** (voir 9.4)

**Actions sur chaque tenant** *(inchangées de la v1)* : Voir, Modifier, Suspendre, Bloquer, Avertir, Réinitialiser MDP directeur, Réactiver, Supprimer.

### 9.4 Page "Apprenants" — liste de tous les élèves/étudiants de chaque école

Nouvelle page dédiée, accessible depuis la fiche d'un tenant : `/admin/tenants/[id]/apprenants`

**Objectif** : permettre au super-admin de consulter rapidement les effectifs de n'importe quelle école, sans ramer même sur de très gros volumes.

**Proposition technique pour que ça ne rame pas :**

- **Pagination côté serveur obligatoire** (pas de chargement de la liste complète côté client). Taille de page par défaut : 25, 50 ou 100 au choix, avec navigation par curseur (`cursor-based pagination` via un ID/timestamp) plutôt que `OFFSET` classique au-delà de quelques milliers de lignes — l'`OFFSET` devient lent sur de gros volumes, le curseur reste performant.
- **Index composés en base** sur `(tenant_id, nom)`, `(tenant_id, matricule)`, `(tenant_id, classe_id)`, `(tenant_id, statut)` pour que les filtres et le tri restent rapides quel que soit le nombre d'apprenants.
- **Recherche différée (debounce 300ms)** côté front pour éviter une requête à chaque frappe clavier.
- **Chargement virtualisé du tableau** (ex : `react-virtual` / `TanStack Virtual`) pour n'afficher dans le DOM que les lignes visibles à l'écran, même si la page contient des centaines de résultats.
- **Cache de requêtes** (ex : TanStack Query / SWR) pour éviter de re-fetcher les mêmes pages déjà vues.

**Colonnes du tableau**

| Colonne |
|---------|
| Photo |
| Nom, Prénom |
| Matricule / Identifiant |
| Classe / Filière & Niveau |
| Statut (actif, suspendu, diplômé, transféré) |
| Statut de paiement |
| Date d'inscription |

**Filtres disponibles**
- Par classe / filière
- Par niveau
- Par statut
- Par statut de paiement
- Recherche texte (nom, matricule)

**Export** : bouton "Exporter" (CSV/Excel) limité aux résultats filtrés, généré en tâche asynchrone si > 5000 lignes (pour ne pas bloquer l'interface).

### 9.5 Reste du module Super-Admin

*(Gestion des abonnements, Paramétrage plateforme, Création d'école manuelle — inchangés de la v1)*

---

## 10. Espace Directeur

*(Inchangé de la v1)* : Tableau de bord, Analytics scolaires, Analytics financières, Absentéisme (désormais alimenté automatiquement par le module Pointage — voir section 19), Validation, Documents officiels, Messagerie, Classement des meilleurs élèves/étudiants.

---

## 11. Espace Secrétariat

### 11.1 Pages *(mises à jour)*

**Tableau de bord**, **Gestion des inscriptions** (avec les champs différenciés Élève/Étudiant — section 2.3), **Gestion des classes & groupes**, **Emplois du temps**.

**Gestion des absences — RÔLE MODIFIÉ**

> **Important : la secrétaire ne saisit plus les absences manuellement.**
>
> Les absences sont désormais **générées automatiquement** par le module Pointage (section 19) : dès qu'un cours commence, si un élève/étudiant n'a pas pointé (biométrie, case à cocher, ou QR code), une absence est automatiquement enregistrée pour ce cours.
>
> **Ce que la secrétaire peut faire :**
> - Consulter la liste des absences générées automatiquement (vue calendrier par classe)
> - **Annuler/justifier une heure d'absence** lorsqu'un justificatif valide est fourni (certificat médical, mot des parents, etc.) — l'annulation est tracée (qui, quand, motif, justificatif joint)
> - Elle ne peut pas créer une absence de toutes pièces ni la modifier sans motif enregistré

**Documents officiels, Annuaire, Messagerie, Calendrier scolaire, Classement** *(inchangés)*.

> Modules supprimés de cet espace : Gestion des activités et Habilitation du conseil estudiantin (le module Conseil Estudiantin & Activités est retiré de cette version).

---

## 12. Espace Comptabilité

*(Inchangé de la v1)* : Tableau de bord financier, Frais de scolarité, Salaires des professeurs (alimentés par le module Pointage pour les heures réalisées), Journal des dépenses, Bilan, Messagerie.

---

## 13. Espace Ressources Humaines

*(Inchangé de la v1)* : Dossiers du personnel, Congés, Absences du personnel, Remplacements, Évaluations annuelles, Formations, Messagerie.

---

## 14. Espace Professeur

### 14.1 Pages *(mises à jour)*

**Tableau de bord, Mon profil, Mes classes, Saisie des notes, Emploi du temps, Cahier de texte numérique** *(inchangés)*.

**Pointage — désormais dans le module dédié (section 19)**

> Le pointage du professeur (confirmation de présence à son cours) n'est plus une simple sous-page de l'espace professeur : c'est un **module autonome partagé** entre professeurs et étudiants/élèves. Depuis son espace, le professeur accède à "Pointage" qui ouvre ce module (biométrique, QR code généré par le prof pour la classe, ou liste manuelle).

**Fiche de paie** *(inchangée, alimentée automatiquement par les données du module Pointage)*.

**Messagerie, Classement** *(inchangés)*.

---

## 15. Espace Étudiant / Élève

> Le libellé de cet espace s'affiche "Espace Élève" ou "Espace Étudiant" selon le type d'entité du tenant (voir section 2).

### 15.1 Pages existantes *(inchangées de la v1)*

Tableau de bord, Mon profil, Mes notes & bulletin, Mes absences *(désormais générées automatiquement, avec statut justifié/non justifié)*, Mon emploi du temps, Cahier de texte, Documents, Classement, Messagerie.

### 15.2 Paiement de la scolarité *(existant, inchangé)*

Voir solde, payer en ligne, historique des paiements avec reçus PDF.

### 15.3 NOUVELLE PAGE — Inscription en ligne & Paiement (dans l'espace Étudiant/Élève)

**Objectif** : permettre à un élève/étudiant déjà titulaire d'un compte (ou à un nouvel apprenant en auto-inscription si l'école l'autorise) de finaliser son inscription administrative pour l'année/le trimestre en cours, payer les frais correspondants, et télécharger immédiatement son reçu.

**URL** : `/etudiant/inscription` (ou `/eleve/inscription`)

**Flux**

1. **Étape 1 — Vérification d'identité**
   - Saisie du matricule (élève) ou identifiant (étudiant) + informations de vérification (nom, date de naissance) si le dossier a été pré-créé par le secrétariat
   - Ou saisie complète des champs d'inscription (section 2.3) si auto-inscription libre activée par l'école

2. **Étape 2 — Choix de la formule d'inscription**
   - Sélection du niveau/classe (ou confirmation si déjà pré-rempli)
   - Affichage du montant des frais de scolarité correspondant (configuré par l'administration)
   - Choix : paiement intégral ou échelonné (si l'école l'autorise)

3. **Étape 3 — Paiement**
   - Choix de la méthode : Orange Money, Wave, CinetPay, carte bancaire
   - Redirection/popup vers la passerelle
   - Confirmation en temps réel via webhook

4. **Étape 4 — Reçu**
   - Génération automatique et immédiate d'un **reçu de paiement PDF** (numéro unique, logo de l'école, montant, date, mode de paiement, nom et matricule de l'apprenant, cachet numérique/QR code de vérification)
   - Bouton **"Télécharger le reçu"**
   - Le reçu est aussi archivé dans "Mes Documents" et consultable/téléchargeable à tout moment ultérieurement
   - Email de confirmation avec le reçu en pièce jointe

**Statut d'inscription**

Une fois le paiement effectué (ou l'acompte minimum requis), le statut de l'apprenant passe automatiquement à "Inscrit" pour la période concernée, visible par le secrétariat et la comptabilité sans action manuelle supplémentaire.

### 15.4 NOUVELLE PAGE — Mon Dossier

**Objectif** : centraliser tous les documents administratifs et personnels de l'élève/étudiant (extrait de naissance, CNI, certificats, diplômes antérieurs, photos d'identité, etc.) dans un espace structuré et consultable par lui-même et par le secrétariat.

**URL** : `/etudiant/dossier` (ou `/eleve/dossier`)

**Fonctionnalités**

- **Bouton "Ajouter un document"** (bouton libre, ouvre une modale avec 3 champs) :
  - **Titre** (texte court, ex : "Extrait de naissance")
  - **Description** (texte libre, ex : "Copie légalisée délivrée le 12/01/2024")
  - **Fichier** (zone de dépôt / upload, formats acceptés : PDF, JPG, PNG — taille max configurable, ex : 10 Mo)
- Chaque document ajouté apparaît dans la liste avec : titre, description, type de fichier, date d'ajout, taille, et actions (Voir, Télécharger, Supprimer *si autorisé*)

**Deux modes d'affichage (bascule en haut de page)**

1. **Mode Tableau** : liste compacte avec colonnes Titre | Description | Date d'ajout | Type | Taille | Actions — trié par date, pagination si nombreux documents
2. **Mode Carte** : grille de cartes visuelles, chaque carte affiche une miniature (aperçu image ou icône PDF), le titre, et un menu d'actions au survol

**Bouton "Récapitulatif du dossier"**

- Génère un **document PDF récapitulatif** listant tous les documents déposés (titre, description, date) avec, si souhaité, les fichiers eux-mêmes fusionnés en annexe ou sous forme de liens/QR codes de téléchargement
- Utile pour impression ou transmission à une administration externe

**Téléchargement**

- Chaque document individuel est téléchargeable à tout moment via une **URL signée temporaire** (voir section 3.2) pour éviter tout accès non autorisé
- Téléchargement groupé possible : sélection multiple → "Télécharger la sélection" → archive ZIP générée à la volée

**Accès et permissions**
- L'élève/étudiant : ajoute, consulte, télécharge ses propres documents ; suppression possible sauf documents verrouillés par le secrétariat (ex : documents officiels validés)
- Le secrétariat : consulte et peut ajouter des documents au dossier de n'importe quel apprenant de son école (ex : ajout d'un document reçu physiquement), et peut verrouiller un document pour empêcher sa suppression

---

## 16. Espace Parent

*(Inchangé de la v1, avec vocabulaire adapté Élève/Étudiant)* : Tableau de bord, Suivi de l'enfant, Notes & bulletin, Absences, Emploi du temps, Paiement des frais de scolarité, Documents, Classement, Messagerie.

---

## 17. Module Messagerie Interne

*(Inchangé de la v1)* : messages directs, messages de groupe, circulaires, réclamations avec suivi de statut.

---

## 18. Module Classement & Meilleurs Élèves/Étudiants

*(Inchangé de la v1)* : page de classement filtrable (trimestre, filière, niveau, classe), podium animé top 3, tableau complet, widget liste déroulante sur tous les tableaux de bord (top 5 avec photo/nom/moyenne, médailles).

---

## 19. Module Pointage & Gestion automatique des absences

### 19.1 Principe

Le pointage constitue un **module autonome** de la plateforme (pas une simple page dans un espace) car il est utilisé à la fois par les professeurs et par les élèves/étudiants, et il alimente automatiquement deux autres modules : la gestion des absences et le calcul de la paie des professeurs.

### 19.2 Modes de pointage disponibles (au choix de l'école, configurable dans les paramètres du tenant)

| Mode | Description | Disponibilité |
|------|-------------|----------------|
| **Biométrique (empreinte digitale)** | Capteur d'empreinte sur l'appareil mobile (API biométrique native Flutter : `local_auth`) ou terminal biométrique dédié connecté en local | Mobile prioritairement |
| **Manuel (case à cocher)** | Le professeur coche présent/absent pour chaque apprenant dans la liste de sa classe, au moment du cours | Web + Mobile |
| **QR Code** | Un QR code unique est généré pour chaque session de cours (par le professeur ou automatiquement par le système à l'heure de début). Chaque élève/étudiant scanne ce code avec l'application mobile pour confirmer sa présence | Mobile (scan) + Web (génération/affichage du QR) |

### 19.3 Fonctionnement détaillé

**Pointage professeur**
- À l'heure prévue du cours, le professeur reçoit une notification "Confirmez votre présence"
- Il pointe via biométrie, QR code personnel, ou bouton manuel
- L'heure exacte de pointage est enregistrée et comparée à l'heure planifiée (retard éventuel calculé)
- Ces données alimentent directement le module Comptabilité → Fiche de paie (heures réalisées vs prévues)

**Pointage élève/étudiant**
- Le professeur génère un QR code de session dès le début du cours (affiché à l'écran ou projeté)
- Chaque apprenant scanne le code depuis l'app mobile pour confirmer sa présence, **ou** pointe par biométrie si l'établissement a équipé les salles d'un terminal, **ou** le professeur pointe manuellement (case à cocher) pour toute la classe en cas de problème technique
- **Dès la fin de la fenêtre de pointage** (ex : 10 minutes après le début du cours), le système compare la liste des inscrits au cours et la liste des pointages reçus
- **Tout apprenant n'ayant pas pointé est automatiquement marqué absent pour ce cours** — aucune saisie manuelle requise de la part de la secrétaire

### 19.4 Interface de gestion des absences (secrétariat / vie scolaire fusionnée dans secrétariat)

- Vue calendrier des absences générées automatiquement, par classe et par apprenant
- Total d'heures d'absence par apprenant, par matière, par période
- **Action possible : "Justifier / Annuler cette absence"** avec upload du justificatif, motif, et traçabilité (qui a validé, quand)
- Notification automatique au parent dès qu'une absence est enregistrée

### 19.5 Interface du module Pointage (autonome)

- Accessible séparément dans le menu de chaque rôle concerné (Professeur, Étudiant/Élève) sous l'entrée **"Pointage"**
- Vue du jour : sessions de cours du jour avec statut de pointage
- Historique personnel : taux de présence, retards cumulés
- Pour le professeur : bouton "Générer QR code de session" avec minuteur de validité (ex : 15 minutes)

---

## 20. Moteur de Calcul des Moyennes

*(Inchangé de la v1)* : moyenne pondérée par coefficient, moyenne générale du trimestre, rang automatique, bulletin PDF généré avec cachet et QR code de vérification.

---

## 21. Module Paiements

*(Inchangé de la v1, avec extension au flux d'inscription en ligne section 15.3)* : Orange Money, Wave, CinetPay, Stripe. Webhooks sécurisés, idempotence, aucune donnée bancaire stockée en clair.

---

## 22. Application Mobile Flutter

### 22.1 Objectif

Développer, en complément du web, une application mobile native (iOS + Android) avec **Flutter**, offrant un design fluide, propre et facile à manipuler, couvrant l'essentiel des usages quotidiens des différents rôles.

### 22.2 Priorités fonctionnelles mobiles

| Fonctionnalité | Priorité |
|-----------------|----------|
| **Module Pointage** (biométrique, QR code, manuel) | Critique — c'est l'usage principal attendu sur mobile |
| Notifications push (absences, notes, messages, paiements) | Critique |
| Consultation des notes / bulletin | Haute |
| Messagerie | Haute |
| Emploi du temps | Haute |
| Paiement en ligne & reçus | Haute |
| Mon Dossier (upload/consultation documents) | Moyenne |
| Classement / Podium | Moyenne |

### 22.3 Architecture technique Flutter

- **State management** : Riverpod ou Bloc
- **Navigation** : GoRouter (deep-linking pris en charge, utile pour les notifications push qui ouvrent une page précise)
- **Authentification biométrique** : package `local_auth`
- **Scan QR code** : package `mobile_scanner`
- **Génération QR code** (côté professeur) : package `qr_flutter`
- **Notifications push** : Firebase Cloud Messaging (FCM)
- **Stockage sécurisé local** (tokens) : `flutter_secure_storage`
- **Appels API** : `dio` avec intercepteurs pour le refresh automatique des tokens JWT
- **Design system** : composants Flutter personnalisés respectant la charte graphique de la plateforme (couleurs par défaut) et surchargeables par les couleurs du tenant courant, avec Material 3 comme base
- **Mode hors-ligne partiel** : mise en cache locale (Hive ou Drift) pour la consultation de l'emploi du temps et des dernières notes, avec synchronisation dès que la connexion revient — utile en cas de réseau instable

### 22.4 Design attendu

- Interface épurée, une action principale claire par écran
- Animations de transition fluides et légères (pas d'effets qui ralentissent le rendu)
- Thème clair adapté aux couleurs de chaque école (le logo et les couleurs du tenant s'appliquent automatiquement après connexion)
- Composants adaptatifs (taille d'écran, mode portrait uniquement pour simplifier au départ, extensible en mode tablette ensuite)
- Accessibilité : contrastes suffisants, tailles de police ajustables

### 22.5 Publication

- Build via Flutter avec configuration multi-environnement (dev / staging / prod)
- Publication sur Google Play Store et Apple App Store sous le nom de la plateforme (une seule app multitenant, l'utilisateur choisit/saisit l'école à la première connexion ou scanne un QR code fourni par l'école)

---

## 23. Sécurité renforcée & Attaques courantes

> Le niveau de sécurité de cette plateforme doit être renforcé ("doublé") par rapport à une application standard, car elle héberge des données personnelles sensibles (mineurs, données financières, documents d'identité).

### 23.1 Injection SQL

- **Utilisation exclusive d'un ORM avec requêtes préparées** (Prisma, SQLAlchemy, Eloquent avec query builder) — jamais de concaténation de chaînes SQL brutes
- Si une requête brute est strictement nécessaire, utiliser systématiquement des **requêtes paramétrées** (bind parameters), jamais d'interpolation de variables utilisateur
- Validation stricte des types et formats en entrée (Zod, Joi, ou validation Laravel Form Request) avant toute requête
- Tests automatisés d'injection (ex : intégrer `sqlmap` en environnement de test CI/CD, jamais en production)

### 23.2 Cross-Site Scripting (XSS)

- Échappement systématique de tout contenu utilisateur affiché (les frameworks front modernes comme React échappent par défaut — ne jamais utiliser `dangerouslySetInnerHTML` sans sanitization)
- Sanitization des champs riches (cahier de texte, description d'activité) avec une librairie dédiée (`DOMPurify`)
- **Content Security Policy (CSP)** stricte définie au niveau des headers HTTP, limitant les sources de scripts autorisées
- Cookies de session en `HttpOnly` + `Secure` + `SameSite=Strict` (empêche le vol de session via XSS)

### 23.3 Cross-Site Request Forgery (CSRF)

- Token CSRF sur tous les formulaires et requêtes de modification (POST/PUT/PATCH/DELETE)
- Vérification de l'origine (`Origin` / `Referer`) sur les endpoints sensibles

### 23.4 Phishing & usurpation

- **SPF, DKIM et DMARC** configurés sur le domaine d'envoi d'emails pour empêcher l'usurpation d'adresse d'expéditeur
- Tous les emails transactionnels (reçus, réinitialisation de mot de passe) incluent le nom exact de l'établissement et un lien qui pointe **toujours** vers le sous-domaine officiel du tenant — jamais de lien raccourci ou externe
- Sensibilisation intégrée : bannière rappelant que la plateforme ne demande jamais le mot de passe par email ou téléphone

### 23.5 Authentification & gestion de session

- Mots de passe hashés avec **bcrypt (coût ≥ 12)** ou **Argon2id** (recommandé, plus résistant au GPU cracking)
- **Authentification à deux facteurs (2FA)** disponible et fortement recommandée pour les rôles à privilèges élevés (Super-Admin, Directeur, Comptabilité)
- JWT signés en **RS256** (clé asymétrique), durée de vie courte (access token 15 min), refresh token stocké en base et révocable
- **Rate limiting** sur les tentatives de connexion : blocage progressif (5 essais → 15 min, puis exponentiel) + captcha après 3 échecs
- Détection de connexions suspectes (changement de pays/IP inhabituel) → notification à l'utilisateur

### 23.6 Injection d'objets / Broken Access Control (IDOR)

- Vérification systématique côté serveur que la ressource demandée appartient bien au `tenant_id` ET à l'utilisateur/rôle courant, sur **chaque** endpoint sans exception
- Tests d'intrusion automatisés (ex : OWASP ZAP en CI/CD) vérifiant qu'un utilisateur A ne peut jamais accéder aux données d'un utilisateur B ou d'un autre tenant

### 23.7 Upload de fichiers malveillants

- Validation du **type MIME réel** (analyse des premiers octets du fichier, pas seulement l'extension)
- **Scan antivirus automatique** de chaque fichier uploadé (ClamAV ou service cloud type VirusTotal API) avant stockage définitif
- Stockage hors du répertoire public web, servi uniquement via URLs signées temporaires
- Limitation stricte de taille et de types de fichiers acceptés par contexte

### 23.8 Déni de service (DoS/DDoS)

- Protection en amont via **Cloudflare** (WAF + protection DDoS incluse même sur plan gratuit)
- Rate limiting global par IP sur l'API
- Limitation du nombre de requêtes lourdes (exports, génération PDF) par utilisateur et par minute

### 23.9 Sécurité de l'infrastructure

- **Web Application Firewall (WAF)** activé (Cloudflare WAF ou équivalent) filtrant les patterns d'attaque connus
- Mises à jour de sécurité automatiques des dépendances (Dependabot / Renovate + audit `npm audit` / `pip-audit` en CI/CD)
- Secrets (clés API, mots de passe DB) jamais en dur dans le code — gestion via variables d'environnement et coffre-fort de secrets (ex : Doppler, AWS Secrets Manager)
- Sauvegardes automatiques quotidiennes de la base de données, chiffrées, avec test de restauration régulier
- Journalisation (logs) de toutes les actions sensibles, conservée et surveillée (ex : via un SIEM léger ou simplement des alertes sur patterns suspects)

### 23.10 Audit de sécurité

- Recommandation d'un **audit de sécurité externe (pentest)** avant la mise en production, puis annuellement
- Programme de bug bounty envisageable une fois la plateforme mature

---

## 24. Performance & Optimisation

### 24.1 Objectifs de performance

- Temps de chargement initial de page < 2 secondes
- Navigation entre pages internes quasi instantanée (< 300ms perçu)
- Aucune latence perceptible au clic sur un bouton ou à l'affichage d'un tableau, même avec plusieurs milliers de lignes de données

### 24.2 Indexation de la base de données

Index à créer systématiquement sur :
- Toutes les clés étrangères (`tenant_id`, `user_id`, `classe_id`, `matiere_id`, etc.)
- Les colonnes utilisées dans les filtres fréquents (`statut`, `matricule`, `email`, `date`)
- **Index composés** pour les requêtes combinant plusieurs filtres (ex : `(tenant_id, classe_id, trimestre_id)` pour les notes)
- Analyse régulière des requêtes lentes (`EXPLAIN ANALYZE` en PostgreSQL) pour ajuster les index au fil du temps

### 24.3 Stratégies front-end

- **Pagination systématique** de toute liste dépassant 50 éléments (jamais de chargement complet côté client)
- **Virtualisation des tableaux** longs (TanStack Virtual / react-window)
- **Lazy loading** des images et composants non visibles immédiatement
- **Code splitting** par route (Next.js le fait nativement) pour ne charger que le JS nécessaire à la page courante
- **Mise en cache des requêtes** (TanStack Query / SWR) avec invalidation ciblée
- **Optimistic UI** sur les actions courantes (like, marquer comme lu) pour un ressenti instantané

### 24.4 Stratégies back-end

- **Cache serveur** (Redis) pour les données peu changeantes : classements, statistiques du tableau de bord, configuration du tenant
- **Requêtes N+1 évitées** systématiquement (eager loading / `include` de l'ORM)
- **Jobs asynchrones** (queue Redis + BullMQ, ou équivalent) pour toute opération lourde : génération de bulletins PDF en masse, exports, envoi d'emails groupés — jamais bloquant pour l'utilisateur
- **CDN** pour tous les assets statiques (images, logos, fichiers du dossier) via Cloudflare

### 24.5 Monitoring de performance

- Outils : Sentry Performance, ou New Relic / Datadog pour surveiller en continu les temps de réponse
- Alertes automatiques si un endpoint dépasse un seuil de latence défini (ex : 1 seconde)

---

## 25. Gestion des erreurs & Page de maintenance

### 25.1 Principe

**Aucune erreur technique brute** (stack trace, erreur Laravel/Node par défaut) ne doit jamais être visible par un utilisateur final, en production.

### 25.2 Comportement en cas de panne

- Si une page, un module ou un service tombe en erreur en production :
  1. L'utilisateur voit une **page de maintenance ou d'erreur générique** propre, avec le branding de l'application (ou de l'école si le contexte le permet), un message rassurant ("Un incident technique est survenu, nos équipes ont été alertées"), et un bouton pour revenir à l'accueil ou réessayer
  2. **Le Super-Admin reçoit immédiatement un email d'alerte** contenant :
     - L'endroit précis de l'erreur (route/endpoint, module concerné, tenant impacté)
     - L'horodatage exact
     - Le message d'erreur technique complet (réservé à cet email, jamais affiché à l'utilisateur)
     - Un lien direct vers les logs détaillés (Sentry ou équivalent)

### 25.3 Mise en œuvre technique

- **Gestionnaire d'erreurs global** (middleware Express / Exception Handler Laravel / Error Boundary React) qui intercepte toute exception non gérée
- Toute exception est :
  1. Loggée avec contexte complet dans un outil de suivi d'erreurs (**Sentry** recommandé)
  2. Déclenche une **alerte email automatique** au super-admin (via un webhook Sentry → service d'email, ou directement dans le gestionnaire d'erreurs)
  3. Retourne à l'utilisateur une réponse générique (code HTTP approprié + page/composant d'erreur propre)
- **Mode maintenance planifiée** : le super-admin peut activer manuellement une page de maintenance globale ou par tenant depuis son espace (section 9), avec message personnalisable et durée estimée affichée

### 25.4 Page d'erreur générique (front)

- Design cohérent avec la charte de l'application
- Illustration légère (pas d'animation lourde)
- Message clair, non technique
- Bouton "Retour à l'accueil" et "Contacter le support"
- Code d'erreur discret en petit (pour référence support), sans détail technique

---

## 26. Design Responsive

### 26.1 Principe

L'application web doit s'adapter parfaitement à **tous les types d'écrans** : téléphone (iPhone/Android), tablette, ordinateur portable, écran de bureau large — sans aucun débordement de contenu, sans scroll horizontal indésirable, sans élément coupé.

### 26.2 Approche technique

- **Mobile-first** : conception des interfaces en partant du plus petit écran, puis extension progressive (`min-width` breakpoints avec Tailwind CSS : `sm`, `md`, `lg`, `xl`, `2xl`)
- **Unités relatives** systématiques (`rem`, `%`, `vw/vh`, `flex`, `grid`) plutôt que des tailles fixes en pixels pour les conteneurs
- **Tableaux responsives** : sur mobile, transformation en liste de cartes empilées plutôt qu'un tableau qui déborde horizontalement (pattern "responsive table to card")
- **Navigation adaptative** : menu latéral fixe sur desktop → menu hamburger / bottom navigation bar sur mobile
- **Images responsives** avec `srcset` pour servir la bonne résolution selon l'appareil
- **Tests systématiques** sur les résolutions courantes : 360×800 (Android moyen), 390×844 (iPhone), 768×1024 (tablette), 1366×768 et 1920×1080 (desktop)
- **Touch targets** suffisamment grands sur mobile (min 44×44px) pour tous les boutons et liens cliquables

### 26.3 Cohérence web / mobile Flutter

Les deux plateformes (web responsive et app Flutter native) partagent la même charte graphique, la même structure de navigation logique, et accèdent à la même API — garantissant une expérience cohérente quel que soit le point d'entrée choisi par l'utilisateur.

---

## 27. Stack Technique Recommandée

### 27.1 Front-end web

- **Framework** : Next.js 14+ (App Router)
- **Styling** : Tailwind CSS
- **Animations** : Framer Motion (interfaces), GSAP (vitrine)
- **Composants UI** : shadcn/ui ou Radix UI
- **Gestion d'état** : Zustand
- **Formulaires** : React Hook Form + Zod
- **Graphiques** : Recharts
- **Tableaux virtualisés** : TanStack Table + TanStack Virtual
- **Cache de requêtes** : TanStack Query

### 27.2 Mobile

- **Framework** : Flutter (voir section 22 pour le détail complet)

### 27.3 Back-end

- **Runtime** : Node.js (Express/Fastify) ou PHP (Laravel) selon l'équipe — le cahier des charges reste agnostique, mais toutes les recommandations de sécurité (section 23) s'appliquent quel que soit le choix
- **ORM** : Prisma (Node) ou Eloquent (Laravel) — toujours avec requêtes préparées
- **Base de données** : PostgreSQL
- **Cache & Queue** : Redis + BullMQ (ou Laravel Queue + Horizon)
- **Authentification** : JWT + refresh tokens, 2FA (TOTP)
- **Temps réel** : Socket.io ou Laravel Reverb/Pusher
- **File storage** : AWS S3 / Cloudflare R2 avec URLs signées
- **Email** : Resend ou SendGrid (avec SPF/DKIM/DMARC configurés)
- **SMS** : Twilio ou Africa's Talking
- **PDF** : Puppeteer / DomPDF
- **Monitoring d'erreurs** : Sentry
- **Monitoring de performance** : Sentry Performance ou Datadog

### 27.4 Infrastructure

- **Hébergement** : VPS (Hetzner/DigitalOcean) ou cloud managé
- **DNS, SSL wildcard, CDN, WAF, protection DDoS** : Cloudflare
- **Reverse proxy** : Nginx ou Caddy
- **CI/CD** : GitHub Actions avec étapes d'audit de sécurité automatiques (`npm audit`, tests OWASP ZAP)

---

## 28. Bonnes pratiques générales

- **Isolation stricte des données multitenant** vérifiée à chaque requête (middleware + tests automatisés)
- **Toutes les URLs de ressources sensibles** utilisent des identifiants non-devinables (UUID) et/ou des liens signés temporaires
- **Aucune erreur technique brute** exposée en production ; alerte immédiate au super-admin en cas d'incident
- **Performance mesurée en continu**, pagination et index systématiques, jamais de chargement de liste complète côté client
- **Sécurité en profondeur** ("defense in depth") : chaque couche (réseau, application, base de données, session) applique ses propres protections indépendamment des autres
- **Responsive et cohérence multi-plateforme** (web + Flutter) avec la même charte graphique et la même logique métier
- **Documentation technique tenue à jour** au fil du développement, pour que cette spécification reste la source de vérité du projet

---

## Annexe A — Récapitulatif des pages par espace *(mis à jour)*

### Super-Admin
- `/admin` — Tableau de bord global
- `/admin/tenants` — Liste des établissements (avec directeur(s), pagination, filtres)
- `/admin/tenants/[id]` — Détail & actions
- `/admin/tenants/[id]/apprenants` — Liste des élèves/étudiants de l'école (filtres + pagination + export)
- `/admin/tenants/new` — Créer une école
- `/admin/abonnements` — Gestion des abonnements
- `/admin/parametres` — Configuration plateforme
- `/admin/logs` — Logs de sécurité
- `/admin/maintenance` — Activer/gérer le mode maintenance

### Espace Directeur
- `/directeur` — Dashboard · `/directeur/analytics` · `/directeur/finances` · `/directeur/absenteisme` · `/directeur/validation` · `/directeur/documents` · `/directeur/messages` · `/directeur/classement`

### Espace Secrétariat
- `/secretariat` — Dashboard · `/secretariat/inscriptions` · `/secretariat/classes` · `/secretariat/emplois-du-temps` · `/secretariat/absences` (consultation + justification) · `/secretariat/documents` · `/secretariat/annuaire` · `/secretariat/calendrier` · `/secretariat/messages` · `/secretariat/classement`

### Espace Comptabilité
- `/comptabilite` · `/comptabilite/scolarites` · `/comptabilite/salaires` · `/comptabilite/depenses` · `/comptabilite/bilan` · `/comptabilite/messages`

### Espace RH
- `/rh` · `/rh/personnel` · `/rh/conges` · `/rh/absences-personnel` · `/rh/remplacements` · `/rh/evaluations` · `/rh/formations`

### Espace Professeur
- `/professeur` · `/professeur/profil` · `/professeur/classes` · `/professeur/notes` · `/professeur/emploi-du-temps` · `/professeur/cahier-de-texte` · `/professeur/pointage` *(module autonome)* · `/professeur/paie` · `/professeur/messages` · `/professeur/classement`

### Espace Étudiant / Élève
- `/etudiant` (ou `/eleve`) — Dashboard
- `/etudiant/profil`
- `/etudiant/notes` — Notes & bulletin
- `/etudiant/absences`
- `/etudiant/emploi-du-temps`
- `/etudiant/cahier-de-texte`
- `/etudiant/documents`
- `/etudiant/inscription` — **Inscription en ligne, paiement, téléchargement du reçu (nouveau)**
- `/etudiant/dossier` — **Mon Dossier : documents administratifs, mode tableau/carte, récapitulatif (nouveau)**
- `/etudiant/pointage` *(module autonome)*
- `/etudiant/classement`
- `/etudiant/messages`

### Espace Parent
- `/parent` · `/parent/suivi/[id]` · `/parent/notes/[id]` · `/parent/absences/[id]` · `/parent/emploi-du-temps/[id]` · `/parent/paiement` · `/parent/documents` · `/parent/classement` · `/parent/messages`

---

## Annexe B — Glossaire *(mis à jour)*

| Terme | Définition |
|-------|-----------|
| Tenant | Un établissement scolaire souscripteur |
| Slug | Identifiant URL de l'école |
| Élève | Apprenant de premier ou second cycle (collège/lycée), identifié par un matricule national |
| Étudiant | Apprenant de l'enseignement supérieur, identifié par un identifiant national ou école |
| Matricule | Identifiant unique délivré par l'État à un élève |
| Identifiant étudiant / INE | Identifiant unique délivré par l'État ou l'école à un étudiant |
| Trimestre | Période d'évaluation |
| Coefficient | Pondération d'une matière/note |
| Bulletin | Relevé officiel des notes |
| Pointage | Confirmation automatisée de présence (biométrie, QR code, manuel) |
| Reçu | Document PDF généré après paiement, avec numéro unique et QR code de vérification |
| Dossier | Espace de stockage des documents administratifs de l'apprenant |
| IDOR | Insecure Direct Object Reference — faille d'accès non autorisé à une ressource via son identifiant |
| WAF | Web Application Firewall |
| Pack | Abonnement souscrit par l'école |
| MRR | Monthly Recurring Revenue |

---

## Annexe C — Historique des versions

- **v1.0** : Spécification initiale (8 espaces, messagerie, classement)
- **v2.0** : Ajout de la distinction Élève/Étudiant, inscription en ligne + paiement + reçu, page Dossier, module Pointage automatisé remplaçant la saisie manuelle des absences, suppression des modules Vie Scolaire et Conseil Estudiantin & Activités, protection/obfuscation des URLs, sécurité renforcée détaillée (OWASP), performance et indexation, gestion des erreurs et maintenance avec alerte email, design responsive complet, application mobile Flutter

---

*Fin du cahier des charges v2.0*
