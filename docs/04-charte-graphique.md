# Charte graphique — « Ivoire & Encre »

> **Statut** : direction retenue. Elle s'applique au web responsive, à l'application Flutter et aux documents PDF générés.
> **Version** : 1.0 — Septembre 2026
> **Planches de référence** : canvas de conception (9 planches — synthèse, chartes comparées, écrans, mobile, thématisation).

---

## 1. Le principe qui commande tout le reste

Chaque école personnalise ses couleurs (§5.3 étape 2 du cahier des charges). **Une charte ne peut donc pas reposer sur une couleur.** Elle repose sur :

- un **fond neutre chaud** qui ne change jamais,
- une **typographie assumée** qui porte l'identité,
- une **grille et des rayons constants**,
- et **un seul jeton d'accent** que l'école remplace.

Test de validation : remplacer l'accent par le vert d'un lycée, puis par le bordeaux d'une université. Si la page reste lisible et cohérente, la charte tient.

---

## 2. Jetons de couleur

### 2.1 Thème clair (référence)

| Jeton | Valeur | Usage |
|---|---|---|
| `--ground` | `#FAF7F0` | Fond de page (ivoire) |
| `--surface` | `#FFFFFF` | Cartes, tableaux, modales |
| `--surface-alt` | `#F4EFE5` | Zones secondaires, en-têtes de tableau, barre latérale (sable) |
| `--border` | `#E4DCCD` | Séparateurs, contours de carte |
| `--border-strong` | `#D8CEBB` | Contours de champ de formulaire, boutons secondaires |
| `--ink` | `#1C1A17` | Texte principal |
| `--ink-2` | `#6B655C` | Texte secondaire, libellés (contraste 5,4:1 sur `--ground`) |
| `--ink-3` | `#3D3932` | Texte courant sur fond sable |
| `--accent` | `#143D36` | Accent plateforme par défaut — **remplacé par l'école** |
| `--accent-ink` | `#FFFFFF` | Texte posé sur l'accent — **dérivé, jamais choisi** |
| `--accent-tint` | `#E8EFEC` | Fond léger d'accent — **dérivé** |
| `--kola` | `#C1502E` | Accent chaud secondaire (aplats, badges) |
| `--kola-ink` | `#A8431F` | Même teinte, version texte (contraste 5,6:1) |

### 2.2 Couleurs sémantiques — **jamais remplacées par l'école**

| Jeton | Fond | Texte | Usage |
|---|---|---|---|
| succès | `#E4F0E8` | `#235E42` | À jour, présent, validé |
| attente | `#FBF0DA` | `#7A4D00` | Échéance, en attente, suspendu |
| alerte | `#FBE6E4` | `#8C1D18` | Impayé, absent, erreur |

Le statut est la seule information portée par la couleur. C'est possible **parce que** le reste de l'interface est quasi monochrome.

### 2.3 Variante sombre (back-office dense)

Dérivée par inversion des jetons, pas par une seconde charte :

| Jeton | Valeur |
|---|---|
| `--ground` | `#16150F` |
| `--surface` | `#1D1B14` |
| `--surface-alt` | `#26231A` |
| `--border` | `#3A362B` |
| `--ink` | `#F2EDE3` |
| `--ink-2` | `#A8A196` |
| `--accent` | éclairci du tenant, luminosité ajustée pour rester ≥ 4,5:1 sur `--ground` |

### 2.4 Règle de dérivation de l'accent du tenant — **normative**

L'école ne fournit **qu'une seule couleur**. Le serveur calcule le reste :

1. `--accent-ink` = blanc ou `--ink`, selon celui qui atteint un contraste ≥ 4,5:1 sur l'accent.
2. `--accent-tint` = accent désaturé et éclairci jusqu'à un contraste ≤ 1,3:1 avec `--surface`.
3. Si l'accent ne permet d'atteindre 4,5:1 **avec aucune** des deux encres, il est **refusé** au moment de la saisie, avec proposition de la variante la plus proche qui passe.

Sans cette règle, une école peut rendre sa propre plateforme illisible et ouvrir une non-conformité d'accessibilité dont la plateforme est responsable.

Mise en œuvre : les trois variables sont injectées sur l'élément `<html>` par le middleware de tenant. **Aucune classe conditionnelle, aucune feuille de style par école** — donc aucun CSS supplémentaire à télécharger quand une école s'inscrit.

---

## 3. Typographie

| Rôle | Police | Usage |
|---|---|---|
| Titrage | **Fraunces** (600) | Titres de page, en-têtes de documents officiels, vitrine publique |
| Interface | **Public Sans** (400 / 500 / 600 / 700) | Tout le reste : tableaux, formulaires, navigation, corps de texte |
| Chiffres | Public Sans en `tabular-nums`, monospace sur les colonnes alignées | Notes, montants, matricules, dates, horaires |

### Échelle

| Niveau | Taille / interligne | Graisse |
|---|---|---|
| Display | 44 / 46 | 600 Fraunces |
| Titre de page | 30 / 36 | 600 Fraunces |
| Titre de section | 24 / 30 | 600 Fraunces |
| Sous-titre | 20 / 26 | 600 Public Sans |
| Corps | 15 / 23 | 400 |
| Interface dense (tableaux) | 13 / 20 | 400–500 |
| Libellé / légende | 12 / 16 | 600, `letter-spacing: 0.06em`, majuscules |

**Règle des chiffres** : toute colonne de nombres comparables utilise des chiffres à chasse fixe (`font-variant-numeric: tabular-nums`). C'est ce qui rend une colonne de moyennes lisible d'un coup d'œil.

**Hébergement des polices** : fichiers `woff2` servis depuis le domaine de la plateforme. **Aucun appel à Google Fonts en production** — c'est une fuite d'adresse IP des utilisateurs vers un tiers, et une dépendance réseau sur le chemin critique du rendu.

---

## 4. Grille, espacement, rayons

- **Base de 4 px.** Toutes les marges, espacements et hauteurs sont des multiples de 4.
- **Rayons** : 10 px sur les cartes et champs, 12 px sur les grands conteneurs, 999 px sur les pastilles de statut.
- **Élévation** : bordure 1 px `--border`, **pas d'ombre portée**. Une ombre sur fond ivoire devient grise et sale ; la bordure tient mieux et coûte moins cher au rendu.
- **Cibles tactiles** : minimum 44 × 44 px sur tout élément cliquable, y compris sur desktop.
- **Largeur de ligne** : 65–75 caractères maximum sur les blocs de texte courant.

---

## 5. Règles de composants

- **Boutons** : primaire = aplat `--accent` + `--accent-ink` ; secondaire = `--surface` + bordure `--border-strong` ; destructif = `--kola`. Jamais plus d'un bouton primaire visible par écran.
- **Tableaux** : en-tête sur `--surface-alt`, lignes séparées par une bordure 1 px, ligne survolée ou active sur `--ground`. Pas de zébrage — il concurrence les couleurs de statut.
- **Formulaires** : un `<label>` visible pour chaque champ, jamais un simple texte d'aide comme substitut. Message d'erreur sous le champ, en texte, jamais uniquement par la couleur de la bordure.
- **États vides** : une phrase et une action, jamais une illustration lourde.
- **Chargement** : squelettes de contenu, pas d'indicateur tournant. La page ne doit pas se réorganiser à l'arrivée des données.
- **Icônes** : trait de 1,8 px, jeu unique, jamais d'emoji.

---

## 6. Accessibilité — seuils contrôlés

- Texte courant : **4,5:1** minimum. Texte ≥ 24 px : 3:1.
- La couleur n'est jamais le seul porteur d'information : chaque pastille de statut porte un libellé texte.
- Focus clavier visible sur tous les éléments interactifs, jamais supprimé.
- Éléments interactifs natifs (`<button>`, `<a href>`, `<input>` + `<label>`) : un `div` cliquable est invisible au clavier et aux lecteurs d'écran.
- Les valeurs de la §2 ont été vérifiées à ces seuils. **Toute nouvelle paire de couleurs est vérifiée avant intégration.**

---

## 7. Cohérence des trois surfaces

C'est la raison du choix de cette direction : le même système traverse les trois surfaces sans rupture.

| Surface | Application |
|---|---|
| **Web** | Jetons CSS, Tailwind configuré sur ces variables |
| **Flutter** | `ThemeData` construit sur les mêmes valeurs, Material 3 comme base, couleurs du tenant appliquées après connexion (§22.3) |
| **PDF** | Bulletins, reçus, certificats : fond ivoire, titre en Fraunces, chiffres à chasse fixe, accent de l'école en filet d'en-tête. **C'est ce qui donne à un bulletin l'aspect d'un document officiel** plutôt que d'une page web imprimée |

Les trois surfaces lisent la même source de jetons, exportée depuis un fichier unique.
