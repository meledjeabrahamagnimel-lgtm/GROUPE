# -*- coding: utf-8 -*-
"""
Génère PLAN-REALISATION-GROUPE.xlsx — le plan de réalisation qui sert de guide au projet.

Pourquoi un script plutôt que le seul classeur : le classeur est un fichier binaire, illisible
dans une revue de code et impossible à fusionner. Le contenu du plan vit ici, en texte ; le
classeur en est la sortie. Pour mettre le plan à jour : modifier le statut d'une ligne ci-dessous
(ou en ajouter une), puis relancer :

    python outils/plan/generer_plan.py

Mise en forme reprise du classeur PLAN-CORRECTION-SELFLOW.xlsx (onglets « Index » et
« Plan de travail », mêmes couleurs de statut), avec deux colonnes en plus : « Qui » et
« Ce que VOUS devez faire », demandées par le propriétaire le 15/10/2026.

Pas de colonne « Jour prévu » : le plan ordonne les chantiers, il ne les date pas. Les colonnes
Début et Fin se remplissent quand un chantier démarre et se termine réellement.
"""
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

# ---------------------------------------------------------------------------------------------
# Vocabulaire
# ---------------------------------------------------------------------------------------------
AGENT = "Agent"            # l'assistant de développement (Claude)
VOUS = "Vous"              # le propriétaire du projet
DEUX = "Les deux"          # l'agent prépare, le propriétaire valide ou fournit quelque chose

TERMINE = "Terminé"
EN_COURS = "En cours"
A_FAIRE = "À faire"
A_TRANCHER = "À trancher"
ATTENTE_VOUS = "Attend vous"   # bloqué tant que le propriétaire n'a pas agi
SANS_OBJET = "Sans objet"

D = date  # raccourci pour les dates de début / fin

# ---------------------------------------------------------------------------------------------
# Le plan. Une section = (titre, [chantiers]).
# Un chantier = (objet, n°, chantier, ce qu'il faut faire, qui, ce que VOUS devez faire,
#                statut, début, fin)
# ---------------------------------------------------------------------------------------------
PLAN = [
    ("0. DÉMARRAGE — cahier des charges, décisions, outils de suivi", [
        ("Dépôt GROUPE", "0.1", "Retrouver le cahier des charges",
         "Le cahier v2, l'addendum v3, le rapport d'évaluation et la charte étaient sur la branche "
         "claude/api-security-performance-djs6mo, pas sur main. Lus en entier.",
         AGENT, "—", TERMINE, D(2026, 10, 15), D(2026, 10, 15)),
        ("Branche main", "0.2", "Faire de la spec la référence du projet",
         "PR #1 fusionnée : docs/01 à 04 et le README sont sur main. L'IA de votre éditeur les voit.",
         AGENT, "—", TERMINE, D(2026, 10, 15), D(2026, 10, 15)),
        ("Décisions", "0.3", "Trancher les choix de départ",
         "Front web : Laravel + Inertia + React + Tailwind (on reste dans Laravel, mêmes commandes "
         "artisan). SMS : gratuit pour l'instant (pilote « log » puis sandbox Africa's Talking). "
         "Réinitialisation du mot de passe d'un mineur : code au téléphone du parent, sinon mot de "
         "passe temporaire donné par le secrétariat.",
         DEUX, "Fait : vous avez validé le 15/10.", TERMINE, D(2026, 10, 15), D(2026, 10, 15)),
        ("Suivi du projet", "0.4", "Plan Excel, fichiers de reprise et de passation",
         "Ce classeur, REPRENDRE-ICI.md (où l'on en est), JOURNAL-DE-BORD.md (ce qui a été fait, "
         "séance par séance), PASSATION-<date>.txt (fin de séance), CLAUDE.md (consignes lues par "
         "l'agent à chaque séance).",
         AGENT, "Déposer le fichier .xlsx dans le dépôt (voir REPRENDRE-ICI § 4).",
         TERMINE, D(2026, 10, 15), D(2026, 10, 15)),
        ("Dépôt GESTION-DE-SITES", "0.5", "Comptes de démonstration exposés publiquement",
         "Le dépôt est PUBLIC et contient ACCES_COMPTES.md, ACCES.txt, ACCES-ARTISAN.txt, "
         "ACCES_DE_TEST.txt : comptes de démonstration (dont un super-admin) au mot de passe "
         "« password ». N'importe qui peut les lire.",
         VOUS,
         "1) GitHub › GESTION-DE-SITES › Settings › General › tout en bas « Danger Zone » › "
         "Change visibility › Make private. 2) Si ces comptes de démonstration ont été installés "
         "sur un serveur en ligne : changer leurs mots de passe, ou les supprimer. 3) Me dire "
         "« 0.5 terminé ».",
         ATTENTE_VOUS, D(2026, 10, 15), None),
        ("Nom de domaine", "0.6", "Choisir l'adresse de la plateforme",
         "C'est le nom acheté (ex. ecolia.ci) ; chaque école reçoit ensuite un sous-domaine gratuit "
         "(lycee-x.ecolia.ci). Inutile pour développer : en local on utilise *.localhost.",
         VOUS,
         "Réfléchir au nom et vérifier qu'il est libre (sur Hostinger, OVH ou Namecheap). Ne rien "
         "acheter avant la section 12. Me donner le nom quand il est choisi.",
         A_TRANCHER, None, None),
        ("Votre poste", "0.7", "Préparer l'environnement de développement local",
         "Le projet exige PostgreSQL 16 et Redis (le cahier interdit SQLite et MySQL : la "
         "Row-Level Security et le partitionnement n'existent qu'en PostgreSQL).",
         VOUS,
         "Dans Laragon : Menu › Tools › Quick add › postgresql (16) et redis ; vérifier PHP 8.3 "
         "avec les extensions pdo_pgsql, pgsql et redis activées (Menu › PHP › Extensions) ; "
         "Node 20 ou plus. Puis me dire « 0.7 terminé ». Je fournirai la procédure détaillée "
         "dans ENVIRONNEMENT-DE-DEV.md au bloc 1.",
         A_FAIRE, None, None),
    ]),

    ("1. SOCLE TECHNIQUE — une base propre, vérifiée automatiquement", [
        ("Front web", "1.1", "Installer Inertia + React + Tailwind",
         "Laravel reste le cœur : routes, contrôleurs, validation, commandes artisan. Les pages "
         "sont en React. Vite compile ; budget de 180 ko de JavaScript par page.",
         AGENT, "—", A_FAIRE, None, None),
        ("Architecture", "1.2", "Installer nwidart/laravel-modules et créer les modules vides",
         "Core, Tenancy, Auth, Identite, SuperAdmin, puis les modules métier au fil des blocs. "
         "Un module ne lit jamais la table d'un autre : il passe par un service ou un événement.",
         AGENT, "—", A_FAIRE, None, None),
        ("Configuration", "1.3", "Corriger .env.example et .gitignore",
         "PostgreSQL, Redis pour cache / sessions / files, sessions chiffrées, cookie au nom "
         "neutre, SameSite=strict. .gitignore : motif .env* sauf .env.example (défaut D-4).",
         AGENT, "—", A_FAIRE, None, None),
        ("Charte graphique", "1.4", "Jetons « Ivoire & Encre » et polices locales",
         "Variables CSS de la charte, Tailwind branché dessus, Fraunces et Public Sans servies "
         "depuis le site (aucun appel à Google Fonts). Gabarit responsive sans débordement.",
         AGENT, "—", A_FAIRE, None, None),
        ("GitHub", "1.5", "Chaîne d'intégration continue (CI)",
         "À chaque PR : Pint, Larastan, tests sur PostgreSQL, gitleaks (fuite de secrets), "
         "composer audit, npm audit, contrôle APP_DEBUG et VITE_*. Une PR rouge ne se fusionne pas.",
         AGENT, "—", A_FAIRE, None, None),
        ("GitHub", "1.6", "Protéger la branche main",
         "Interdire la poussée directe sur main : tout passe par une PR dont la CI est verte. "
         "Je ne peux pas régler cela moi-même (réglage du dépôt).",
         VOUS,
         "GitHub › GROUPE › Settings › Branches › Add branch ruleset : cible « main », cocher "
         "« Require a pull request before merging » et « Require status checks to pass » (choisir "
         "la CI créée en 1.5), « Block force pushes ». Me dire « 1.6 terminé ».",
         ATTENTE_VOUS, None, None),
        ("Documentation", "1.7", "ENVIRONNEMENT-DE-DEV.md",
         "Installer et lancer le projet pas à pas sur Laragon : PostgreSQL, Redis, Mailpit, "
         "sous-domaines *.localhost, commandes de démarrage.",
         AGENT, "Suivre la procédure sur votre poste et me dire si une étape bloque.",
         A_FAIRE, None, None),
    ]),

    ("2. ISOLATION MULTITENANT — une école ne voit jamais une autre", [
        ("Modèles", "2.1", "Trait BelongsToTenant obligatoire",
         "Scope global automatique ; tenant_id rempli depuis le contexte serveur, jamais depuis la "
         "requête. Un test fait échouer la CI si un modèle métier n'a pas le trait.",
         AGENT, "—", A_FAIRE, None, None),
        ("Identifiants", "2.2", "id interne + public_id exposé",
         "BIGSERIAL pour les jointures ; UUID v4 (personnes, documents, paiements) ou ULID "
         "(pointages, messages, journaux) pour les URL. Aucune réponse ne contient l'id interne.",
         AGENT, "—", A_FAIRE, None, None),
        ("Base de données", "2.3", "Row-Level Security PostgreSQL",
         "Seconde barrière : même une requête qui oublie le filtre ne lit pas une autre école. "
         "Variable posée par transaction (compatible PgBouncer) ; rôle applicatif sans BYPASSRLS.",
         AGENT, "—", A_FAIRE, None, None),
        ("Middleware", "2.4", "Résolution de l'école par le sous-domaine (corrigée)",
         "Host vérifié, sous-domaines réservés (admin, www, api…), cache Redis y compris des "
         "réponses négatives, statut et abonnement contrôlés, même réponse pour toute école "
         "introuvable / suspendue (défauts C-2 à C-9 du rapport).",
         AGENT, "—", A_FAIRE, None, None),
        ("Tests", "2.5", "Suite de tests d'isolation",
         "Pour chaque endpoint : un utilisateur de l'école A reçoit 404 sur une ressource de "
         "l'école B. Un endpoint sans ce test ne passe pas la revue.",
         AGENT, "—", A_FAIRE, None, None),
    ]),

    ("3. AUTHENTIFICATION ET UTILISATEURS", [
        ("Rôles", "3.1", "Rôles, permissions, lien parent ↔ enfant",
         "Directeur, secrétariat, comptabilité, RH, professeur, élève / étudiant, parent. Une "
         "Policy par modèle ; le refus est la règle par défaut.",
         AGENT, "—", A_FAIRE, None, None),
        ("Connexion", "3.2", "Page de choix du type de connexion + connexion",
         "Cartes Élève/Étudiant, Parent, Enseignant, Administration (jamais Directeur ni "
         "Super-admin en public). Matricule / INE ou email + mot de passe. Même message et même "
         "durée que le compte existe ou non ; blocage progressif ; captcha après 3 échecs.",
         AGENT, "—", A_FAIRE, None, None),
        ("Mot de passe", "3.3", "Réinitialisation en deux étapes (email puis SMS)",
         "Lien par email (jeton haché, usage unique, 30 min) puis code SMS (haché, 5 essais, "
         "5 min). Toutes les sessions sont fermées après le changement. SMS derrière une interface "
         "SmsSender : pilote « log » en local.",
         AGENT, "—", A_FAIRE, None, None),
        ("Mot de passe", "3.4", "Cas des mineurs",
         "Code envoyé au téléphone du parent rattaché ; sinon le secrétariat donne un mot de passe "
         "temporaire, à changer à la connexion suivante, et l'action est journalisée.",
         AGENT, "—", A_FAIRE, None, None),
        ("SMS", "3.5", "Compte Africa's Talking en mode sandbox (gratuit)",
         "Pour voir de vrais SMS arriver sur le simulateur, sans payer.",
         VOUS,
         "Créer un compte sur africastalking.com, rester en « Sandbox », copier l'API key et me "
         "dire qu'elle est prête. NE PAS me l'écrire dans la conversation : la mettre vous-même "
         "dans votre .env local (AT_API_KEY=…).",
         A_FAIRE, None, None),
        ("Double authentification", "3.6", "2FA par application (TOTP)",
         "Gratuite (Google Authenticator, Microsoft Authenticator). Obligatoire pour le super-admin, "
         "la direction et la comptabilité.",
         AGENT, "—", A_FAIRE, None, None),
    ]),

    ("4. ESPACE SUPER-ADMIN — piloter et surveiller la plateforme", [
        ("Accès", "4.1", "admin.<domaine> séparé",
         "Comptes super-admin dans une table à part, garde séparée, 2FA obligatoire, liste "
         "blanche d'adresses IP. Toute lecture inter-écoles est explicite et journalisée.",
         AGENT, "—", A_FAIRE, None, None),
        ("Écoles", "4.2", "Liste des écoles et actions",
         "Directeur(s), type d'entité, plan, échéance, statut, effectif. Filtres, recherche, "
         "pagination par curseur. Créer, suspendre, bloquer, avertir, supprimer (logiquement, "
         "export d'abord).",
         AGENT, "—", A_FAIRE, None, None),
        ("Apprenants", "4.3", "Élèves / étudiants de chaque école",
         "Index (tenant_id, …), curseur, recherche différée et annulée, tableau virtualisé, "
         "export en tâche de fond au-delà de 5 000 lignes.",
         AGENT, "—", A_FAIRE, None, None),
        ("Paramétrage", "4.4", "Logo, couleur, règles de chaque école",
         "Une seule couleur fournie par l'école ; le contraste est vérifié et une couleur illisible "
         "est refusée. Type d'entité, trimestres, coefficients.",
         AGENT, "—", A_FAIRE, None, None),
        ("Supervision", "4.5", "Performance, journaux de requêtes, intrusions",
         "Latences par route, erreurs, files d'attente ; journal des requêtes (mots de passe et "
         "jetons masqués, table partitionnée) ; tentatives d'attaque et bannissement automatique.",
         AGENT, "—", A_FAIRE, None, None),
        ("Maintenance", "4.6", "Mode maintenance global ou par école",
         "Page « maintenance évolutive » avec message, durée estimée, email et téléphone de "
         "contact modifiables par vous. Le super-admin garde l'accès.",
         DEUX, "Saisir vos coordonnées de contact dans l'écran quand il sera livré.",
         A_FAIRE, None, None),
        ("Incidents", "4.7", "Aucune erreur brute ; alerte immédiate",
         "L'utilisateur voit une page propre ; vous recevez un email avec le module, la route, "
         "l'école et l'heure. Une même panne n'envoie pas mille emails.",
         AGENT, "—", A_FAIRE, None, None),
        ("Abonnements", "4.8", "Packs, échéances, coupure automatique",
         "Alertes 30 / 7 / 1 jours avant l'échéance ; l'école expirée bascule seule.",
         AGENT, "—", A_FAIRE, None, None),
    ]),

    ("5. RÉFÉRENTIEL SCOLAIRE ET SCOLARITÉ", [
        ("Référentiel", "5.1", "Années, trimestres, cycles, niveaux, filières, classes, matières",
         "Collège / lycée (6e → Terminale) ou supérieur (L1 → Doctorat) selon le type d'entité.",
         AGENT, "—", A_FAIRE, None, None),
        ("Apprenants", "5.2", "Élève ou étudiant selon l'école",
         "Matricule d'État (élève) ou INE / identifiant école (étudiant), unique par école, jamais "
         "dans une URL. Libellés de toute l'interface adaptés.",
         AGENT, "—", A_FAIRE, None, None),
        ("Secrétariat", "5.3", "Inscriptions",
         "Champs différenciés élève / étudiant ; pré-création d'un dossier que l'apprenant "
         "rattache ensuite avec son matricule.",
         AGENT, "—", A_FAIRE, None, None),
        ("Mon Dossier", "5.4", "Documents de l'apprenant",
         "Bouton Ajouter (titre, description, fichier), vue tableau / cartes, récapitulatif PDF, "
         "téléchargement unitaire ou ZIP par URL signée, verrouillage par le secrétariat.",
         AGENT, "—", A_FAIRE, None, None),
        ("Fichiers", "5.5", "Quarantaine et antivirus",
         "Type réel vérifié, fichier en quarantaine, analyse ClamAV en tâche de fond, jamais de "
         "service tiers (pièces d'identité de mineurs).",
         AGENT, "—", A_FAIRE, None, None),
    ]),

    ("6. EMPLOI DU TEMPS ET POINTAGE", [
        ("Emploi du temps", "6.1", "Séances planifiées",
         "Tenu par le secrétariat ; il alimente le pointage et la paie.", AGENT, "—", A_FAIRE, None, None),
        ("Pointage", "6.2", "Module autonome : QR rotatif, manuel, biométrie",
         "QR régénéré toutes les 10 à 15 s (une photo transmise à un absent ne sert à rien) ; "
         "liste à cocher ; biométrie côté mobile.", AGENT, "—", A_FAIRE, None, None),
        ("Absences", "6.3", "Absences automatiques, provisoires puis confirmées",
         "Non-pointé = absent provisoire ; le professeur confirme à la clôture de la séance ; le "
         "parent est notifié après confirmation. Le secrétariat justifie ou annule, jamais ne saisit.",
         AGENT, "—", A_FAIRE, None, None),
        ("Volumétrie", "6.4", "Partitionnement par année scolaire",
         "pointages (≈ 108 M lignes / an à 100 écoles), absences, messages, journaux.",
         AGENT, "—", A_FAIRE, None, None),
    ]),

    ("7. ÉVALUATION ET CLASSEMENT", [
        ("Notes", "7.1", "Saisie des notes par le professeur", "Par classe, matière, trimestre.",
         AGENT, "—", A_FAIRE, None, None),
        ("Règles de calcul", "7.2", "Fournir les règles réelles d'une école",
         "Moyenne pondérée, arrondis, rang ex-æquo, mentions : les règles varient d'une école à "
         "l'autre. Sans un cas réel, le moteur serait une supposition.",
         VOUS,
         "Me transmettre un bulletin réel (anonymisé) d'un collège ou lycée et d'une grande école, "
         "et dire comment le rang se calcule en cas d'égalité.",
         A_TRANCHER, None, None),
        ("Moteur", "7.3", "Moyennes, rang, bulletins PDF",
         "Bulletin PDF avec QR de vérification (n'affiche que l'authenticité, jamais les notes).",
         AGENT, "—", A_FAIRE, None, None),
        ("Classement", "7.4", "Meilleurs par filière, classe, niveau, trimestre",
         "Page dédiée + liste déroulante (photo, nom, moyenne) dans les espaces élève, parent, "
         "professeur et administration. Pré-calculé : affichage instantané.",
         AGENT, "—", A_FAIRE, None, None),
    ]),

    ("8. ARGENT — paiements, comptabilité, paie", [
        ("Passerelles", "8.1", "Comptes marchands en mode test",
         "Orange Money, Wave, CinetPay, Stripe : il faut un compte pour obtenir les clés de test.",
         VOUS,
         "Ouvrir au moins un compte marchand de test (CinetPay regroupe Orange Money, Wave et la "
         "carte : c'est le plus simple pour démarrer) et me dire qu'il est prêt. Les clés vont dans "
         "votre .env, jamais dans la conversation.",
         A_FAIRE, None, None),
        ("Paiements", "8.2", "Paiements et webhooks idempotents",
         "Un paiement confirmé deux fois n'est compté qu'une fois (référence unique).",
         AGENT, "—", A_FAIRE, None, None),
        ("Espace élève", "8.3", "Inscription en ligne, paiement, reçu",
         "Reçu PDF numéroté (REC-2026-000148), QR de vérification, archivé dans Mes documents, "
         "envoyé par email ; statut « Inscrit » automatique.", AGENT, "—", A_FAIRE, None, None),
        ("Comptabilité", "8.4", "Scolarités, impayés, relances, dépenses, bilan",
         "Exports PDF / Excel ; relances automatiques.", AGENT, "—", A_FAIRE, None, None),
        ("Paie", "8.5", "Règles de paie des professeurs",
         "Taux horaire, vacataire / permanent, retenues pour retard ou heure non faite : à fixer.",
         VOUS, "Me décrire comment une école paie aujourd'hui un vacataire et un permanent.",
         A_TRANCHER, None, None),
        ("Paie", "8.6", "Fiche de paie à partir du pointage",
         "Heures prévues / réalisées / non faites, retenues, primes.", AGENT, "—", A_FAIRE, None, None),
    ]),

    ("9. COMMUNICATION ET AUTRES ESPACES", [
        ("Messagerie", "9.1", "Messagerie interne et réclamations",
         "Selon la matrice du cahier § 8 (élève ↔ professeurs et administration, parent ↔ "
         "administration…), avec suivi de statut des réclamations.", AGENT, "—", A_FAIRE, None, None),
        ("Notifications", "9.2", "In-app, email, push", "—", AGENT, "—", A_FAIRE, None, None),
        ("Professeur", "9.3", "Cahier de texte numérique", "—", AGENT, "—", A_FAIRE, None, None),
        ("RH", "9.4", "Personnel, contrats, congés, remplacements, évaluations",
         "—", AGENT, "—", A_FAIRE, None, None),
        ("Directeur", "9.5", "Analytics en lecture seule",
         "Réussite par filière, recouvrement, absentéisme — tables d'agrégats.",
         AGENT, "—", A_FAIRE, None, None),
        ("Parent", "9.6", "Espace parent", "Plusieurs enfants, notes, absences, paiement, messagerie.",
         AGENT, "—", A_FAIRE, None, None),
        ("Secrétariat", "9.7", "Documents officiels, annuaire, calendrier, circulaires",
         "—", AGENT, "—", A_FAIRE, None, None),
    ]),

    ("10. VITRINE ET INSCRIPTION DES ÉCOLES", [
        ("Tarifs", "10.1", "Prix des packs",
         "Démo (1 mois, gratuit, 50 apprenants), Starter, Annuel, Pro, Enterprise : les prix ne "
         "sont pas fixés dans le cahier.", VOUS, "Me donner les prix de chaque pack.",
         A_TRANCHER, None, None),
        ("Vitrine", "10.2", "Page vitrine animée de la plateforme",
         "Animations légères (aucune ne doit ralentir la page).", AGENT,
         "Fournir textes, logo et visuels de la plateforme, ou valider ceux que je propose.",
         A_FAIRE, None, None),
        ("Inscription", "10.3", "Choix du pack → inscription en étapes → paiement → URL de l'école",
         "Le sous-domaine est créé automatiquement à la fin de l'inscription.",
         AGENT, "—", A_FAIRE, None, None),
        ("Page de l'école", "10.4", "Page de bienvenue et connexion propres à chaque école",
         "Logo, couleur, présentation, activités de l'école ; bouton vers le choix de connexion.",
         AGENT, "—", A_FAIRE, None, None),
    ]),

    ("11. APPLICATION MOBILE FLUTTER", [
        ("API", "11.1", "API /api/v1 pour le mobile",
         "JWT RS256 court + refresh révocable, attestation de l'application, signature des "
         "requêtes, épinglage de certificat.", AGENT, "—", A_FAIRE, None, None),
        ("Application", "11.2", "Application Flutter",
         "Pointage (QR, biométrie), notifications, notes, messagerie, emploi du temps, paiements ; "
         "mode hors-ligne partiel.", AGENT, "—", A_FAIRE, None, None),
        ("Comptes", "11.3", "Firebase et magasins d'applications",
         "Firebase (notifications, gratuit) ; Google Play (25 $ une fois) ; Apple (99 $ par an).",
         VOUS, "Créer ces comptes au moment de la publication ; je dirai lesquels et quand.",
         A_FAIRE, None, None),
    ]),

    ("12. MISE EN PRODUCTION", [
        ("Hébergement", "12.1", "Domaine, Cloudflare, serveur",
         "Nom de domaine (0.6), Cloudflare gratuit (DNS *.domaine, SSL, pare-feu), un VPS, piloté "
         "par Laravel Forge ou Ploi.", VOUS,
         "Acheter le domaine et le VPS ; je vous guiderai écran par écran.", A_FAIRE, None, None),
        ("Déploiement", "12.2", "Déploiement sans interruption",
         "Secrets dans GitHub Environments, .env écrit au déploiement, retour arrière en secondes.",
         AGENT, "—", A_FAIRE, None, None),
        ("Sauvegardes", "12.3", "Sauvegarde continue (PITR) et restauration testée",
         "Perte maximale de quelques minutes en cas de panne.", AGENT, "—", A_FAIRE, None, None),
        ("Contrôles", "12.4", "Test de charge (100 000 apprenants), OWASP ZAP, pentest externe",
         "—", DEUX, "Choisir et mandater le prestataire du pentest.", A_FAIRE, None, None),
        ("SMS", "12.5", "Passer le SMS en mode réel (payant)", "Une ligne du .env à changer.",
         VOUS, "Créditer le compte SMS.", A_FAIRE, None, None),
    ]),

    ("13. CONDUITE DU CHANTIER — règles permanentes", [
        ("Git", "13.1", "Une branche par bloc de travail",
         "Chaque bloc : branche → commits → poussée → PR → CI verte → fusion dans main.",
         AGENT, "—", TERMINE, D(2026, 10, 15), None),
        ("Suivi", "13.2", "Mettre à jour le plan et les fichiers de reprise à chaque bloc",
         "Statuts de ce classeur, REPRENDRE-ICI.md, JOURNAL-DE-BORD.md et une PASSATION datée.",
         AGENT, "—", TERMINE, D(2026, 10, 15), None),
        ("Vos retours", "13.3", "Dire « N° terminé » quand une tâche « Vous » est faite",
         "Je passe alors la ligne à Terminé et je mets les fichiers à jour.", VOUS,
         "Écrire simplement : « 0.5 terminé », « 1.6 terminé »…", TERMINE, D(2026, 10, 15), None),
    ]),
]

# ---------------------------------------------------------------------------------------------
# Mise en forme (couleurs reprises de PLAN-CORRECTION-SELFLOW.xlsx)
# ---------------------------------------------------------------------------------------------
ENCRE = "FF25272D"
TITRE = "FF191B20"
GRIS = "FF6B6E76"
BORD = "FFD8DCE3"
SECTION_FOND = "FFF7F5EF"
SECTION_TEXTE = "FFC8102E"

STYLE_STATUT = {
    TERMINE: ("FFEAF5EE", "FF0E5A2E"),
    EN_COURS: ("FFE6EEF8", "FF1D4E89"),
    A_FAIRE: ("FFFDF3E2", "FF8A5300"),
    A_TRANCHER: ("FFFDF3E2", "FF8A5300"),
    ATTENTE_VOUS: ("FFFBE6E4", "FF8C1D18"),
    SANS_OBJET: ("FFEFEFF2", "FF5F6672"),
}
STYLE_QUI = {
    AGENT: ("FFE6EEF8", "FF1D4E89"),
    VOUS: ("FFFBE6E4", "FF8C1D18"),
    DEUX: ("FFF4EFE5", "FF3D3932"),
}

trait = Side(style="thin", color=BORD)
bordure = Border(top=trait, bottom=trait, left=trait, right=trait)
haut = Alignment(vertical="top", wrap_text=True)


def entete(ws, ligne, titres):
    for col, texte in enumerate(titres, start=1):
        c = ws.cell(row=ligne, column=col, value=texte)
        c.font = Font(name="Calibri", size=10, bold=True, color="FFFFFFFF")
        c.fill = PatternFill("solid", fgColor=TITRE)
        c.alignment = Alignment(vertical="center", wrap_text=True)
        c.border = bordure
    ws.row_dimensions[ligne].height = 22


def pastille(c, couleurs):
    fond, texte = couleurs
    c.fill = PatternFill("solid", fgColor=fond)
    c.font = Font(name="Calibri", size=10, bold=True, color=texte)


def construire(chemin: Path, maj: str):
    wb = Workbook()
    idx = wb.active
    idx.title = "Index"
    plan = wb.create_sheet("Plan de travail")

    # ---- Plan de travail ----
    plan["A1"] = "PLAN DE RÉALISATION — GROUPE (plateforme scolaire multitenant)"
    plan["A1"].font = Font(name="Calibri", size=18, bold=True, color=TITRE)
    plan["A2"] = (
        "Guide du projet, de la page de connexion à la mise en production. « Qui » dit qui agit : "
        "l'Agent (l'assistant de développement), Vous (le propriétaire), ou Les deux. Quand une "
        f"tâche « Vous » est faite, dites « N° terminé ». Mis à jour le {maj}."
    )
    plan["A2"].font = Font(name="Calibri", size=10, color=GRIS)
    plan.merge_cells("A2:I2")
    plan["A2"].alignment = Alignment(wrap_text=True, vertical="top")
    plan.row_dimensions[2].height = 30
    entete(plan, 4, ["Écran ou objet", "N°", "Chantier", "Ce qu'il faut faire", "Qui",
                     "Ce que VOUS devez faire", "Statut", "Début", "Fin"])
    for col, largeur in zip("ABCDEFGHI", [26, 6, 40, 80, 10, 55, 13, 11, 11]):
        plan.column_dimensions[col].width = largeur

    ligne = 5
    resume = []
    for titre, chantiers in PLAN:
        debut_section = ligne
        c = plan.cell(row=ligne, column=1, value=titre)
        for col in range(1, 10):
            plan.cell(row=ligne, column=col).fill = PatternFill("solid", fgColor=SECTION_FOND)
        c.font = Font(name="Calibri", size=11, bold=True, color=SECTION_TEXTE)
        plan.merge_cells(start_row=ligne, start_column=1, end_row=ligne, end_column=9)
        ligne += 1
        compte = {"total": 0, TERMINE: 0, "a_faire": 0, A_TRANCHER: 0, "vous": 0}
        for objet, num, chantier, quoi, qui, vous, statut, debut, fin in chantiers:
            valeurs = [objet, num, chantier, quoi, qui, vous, statut, debut, fin]
            for col, v in enumerate(valeurs, start=1):
                cell = plan.cell(row=ligne, column=col, value=v)
                cell.font = Font(name="Calibri", size=10, color=ENCRE, bold=(col == 3))
                cell.alignment = haut
                cell.border = bordure
                if col in (8, 9) and v is not None:
                    cell.number_format = "DD/MM/YYYY"
            pastille(plan.cell(row=ligne, column=5), STYLE_QUI[qui])
            pastille(plan.cell(row=ligne, column=7), STYLE_STATUT[statut])
            compte["total"] += 1
            if statut == TERMINE:
                compte[TERMINE] += 1
            elif statut in (A_FAIRE, EN_COURS, ATTENTE_VOUS):
                compte["a_faire"] += 1
            elif statut == A_TRANCHER:
                compte[A_TRANCHER] += 1
            if qui in (VOUS, DEUX) and statut in (A_FAIRE, ATTENTE_VOUS, A_TRANCHER):
                compte["vous"] += 1
            ligne += 1
        resume.append((titre, debut_section, compte))
        ligne += 1  # ligne vide entre sections

    plan.freeze_panes = "A5"
    plan.auto_filter.ref = f"A4:I{ligne - 2}"
    plan.sheet_view.showGridLines = False

    # ---- Index ----
    idx["A1"] = "INDEX DES SECTIONS"
    idx["A1"].font = Font(name="Calibri", size=18, bold=True, color=TITRE)
    idx["A2"] = ("Où en est chaque section, et à quelle ligne du plan elle commence. "
                 "« Chez vous » = tâches qui attendent une action du propriétaire.")
    idx["A2"].font = Font(name="Calibri", size=10, color=GRIS)
    entete(idx, 4, ["Section", "Ligne", "Chantiers", "Terminés", "À faire", "À trancher",
                    "Chez vous", "Avancement"])
    for col, largeur in zip("ABCDEFGH", [66, 8, 11, 10, 9, 11, 11, 14]):
        idx.column_dimensions[col].width = largeur
    r = 5
    totaux = [0, 0, 0, 0, 0]
    for titre, debut, cpt in resume:
        vals = [titre, debut, cpt["total"], cpt[TERMINE], cpt["a_faire"], cpt[A_TRANCHER], cpt["vous"]]
        for col, v in enumerate(vals, start=1):
            cell = idx.cell(row=r, column=col, value=v)
            cell.font = Font(name="Calibri", size=10, color=ENCRE, bold=(col == 1))
            cell.border = bordure
        idx.cell(row=r, column=1).hyperlink = f"#'Plan de travail'!A{debut}"
        fait, tout = cpt[TERMINE], cpt["total"]
        av = idx.cell(row=r, column=8, value="Terminée" if fait == tout else f"{fait}/{tout}")
        av.border = bordure
        pastille(av, STYLE_STATUT[TERMINE] if fait == tout else STYLE_STATUT[A_FAIRE])
        for i, k in enumerate(["total", TERMINE, "a_faire", A_TRANCHER, "vous"]):
            totaux[i] += cpt[k]
        r += 1
    idx.cell(row=r, column=1, value="TOTAL").font = Font(name="Calibri", size=10, bold=True, color=TITRE)
    for i, v in enumerate(totaux, start=3):
        idx.cell(row=r, column=i, value=v).font = Font(name="Calibri", size=10, bold=True, color=TITRE)
    idx.freeze_panes = "A5"
    idx.sheet_view.showGridLines = False

    wb.save(chemin)
    return totaux


if __name__ == "__main__":
    racine = Path(__file__).resolve().parents[2]
    sortie = racine / "PLAN-REALISATION-GROUPE.xlsx"
    t = construire(sortie, date.today().strftime("%d/%m/%Y"))
    print(f"{sortie.name} : {t[0]} chantiers, {t[1]} terminés, {t[2]} à faire, "
          f"{t[3]} à trancher, {t[4]} chez vous")
