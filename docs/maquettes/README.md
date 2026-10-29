# Maquettes — bloc 1.0 « Propositions de design »

Trois directions de composition, toutes conformes à la charte **« Ivoire & Encre »**
(`docs/04-charte-graphique.md`), à comparer avant d'écrire la moindre page du front
(règle du propriétaire du 16/10, `CLAUDE.md` § 6).

## Ouvrir les maquettes

1. Une seule fois après `git pull`, reconstruire les polices (Python 3, aucune dépendance) :
   `python outils/maquettes/generer_polices.py`
   — le script télécharge les deux paquets officiels, **vérifie leur empreinte SHA-512** et écrit
   `assets/polices.css`. Sans cette étape, les pages s'ouvrent quand même, avec des polices de
   remplacement (Georgia, police système).
2. Double-cliquer sur **`docs/maquettes/index.html`** : la page s'ouvre dans le navigateur, sans
   serveur ni connexion internet (aucun appel externe).

| Fichier | Direction | En une phrase |
|---|---|---|
| `A-registre.html` | **A — Registre** | Institutionnelle et dense : menu latéral fixe, chiffres alignés comme dans un registre. |
| `B-cahier.html` | **B — Cahier** | Éditoriale et aérée : menu en haut, une colonne, grands titres ; la plus proche du mobile. |
| `C-pupitre.html` | **C — Pupitre** | Outil compact : rail d'icônes, modules, connexion en un écran, super-admin en sombre. |

Chaque direction montre les **six mêmes écrans** : page de bienvenue d'une école, choix de
connexion, tableau de bord élève, tableau du super-admin, version téléphone, page de maintenance
évolutive.

## Ce qui est commun aux trois (et ne se rediscute pas)

- Jetons de couleur, typographie (Fraunces pour les titres, Public Sans pour l'interface,
  chiffres à chasse fixe), base de 4 px, rayons 10 / 12 px, **bordures sans ombre**.
- Couleurs de statut (succès, attente, alerte) jamais remplacées par l'école, toujours
  accompagnées d'un libellé.
- Cibles cliquables ≥ 44 px, focus clavier visible, un seul bouton primaire par écran.
- Connexion publique limitée à quatre espaces : jamais « Directeur » ni « Super-admin ».
- Super-admin toujours aux couleurs de la plateforme, jamais à celles d'une école.

## Le test de la charte (barre en haut de chaque page)

La barre permet de remplacer la couleur de l'école. `assets/accent.js` applique la **règle
normative § 2.4** : l'encre posée sur l'accent (blanc ou encre) est choisie pour atteindre 4,5:1,
la teinte légère est dérivée, et une couleur qui n'atteint 4,5:1 avec **aucune** des deux encres
est **refusée**, avec la variante la plus proche proposée (bouton « Gris moyen » : 4,40:1 au
mieux, proposition `#767676`).

Contrastes contrôlés pendant ce bloc (formule WCAG 2.x, script exécuté) :

| Accent | Encre sur accent | Teinte / surface | Variante sombre : sur fond / encre |
|---|---|---|---|
| `#143D36` plateforme | 12,00:1 | 1,30:1 | 5,01:1 / 4,76:1 |
| `#1F6B3A` vert | 6,52:1 | 1,29:1 | — |
| `#7A1F33` bordeaux | 10,14:1 | 1,28:1 | 4,87:1 / 4,62:1 |
| `#F2C230` jaune | 10,36:1 (encre sombre) | 1,29:1 | 10,92:1 / 10,36:1 |

Constat utile pour le bloc 4.4 : avec deux encres (blanc et `#1C1A17`), seules les couleurs de
**luminosité moyenne** sont refusées. La règle protège donc sans gêner la plupart des écoles.

Dans l'application, ce calcul sera fait **par le serveur** à la saisie de la couleur ; le
navigateur ne recevra que les trois variables déjà calculées, posées sur `<html>`.

## Fichiers

```
docs/maquettes/
├── index.html            comparaison et mode d'emploi
├── A-registre.html       direction A
├── B-cahier.html         direction B
├── C-pupitre.html        direction C
└── assets/
    ├── jetons.css        jetons de la charte + composants communs (préfigure le bloc 1.4)
    ├── accent.js         dérivation de l'accent d'une école (prototype de la règle § 2.4)
    ├── presentation.js   jeu d'icônes + barre de test de couleur (hors application)
    └── polices.css       GÉNÉRÉ, non versionné : Fraunces 600, Public Sans 400–700 (SIL OFL 1.1)
outils/maquettes/generer_polices.py   recette de polices.css, empreintes épinglées
```

Les captures d'écran (fichiers PNG) ne sont pas versionnées : elles sont fournies à part au
propriétaire et se régénèrent à partir de ces pages.

## Données

Toutes les données sont **fictives** (école, élèves, montants). Les adresses IP des écrans de
sécurité appartiennent aux plages réservées à la documentation (RFC 5737) ; l'email et le
téléphone de contact sont des exemples à remplacer par les vôtres dans l'écran de maintenance.

## Après le choix

La direction retenue (ou le mélange demandé) devient la référence des blocs 1.4 (jetons et
gabarit) et suivants. Les maquettes restent dans le dépôt comme trace de la décision.
