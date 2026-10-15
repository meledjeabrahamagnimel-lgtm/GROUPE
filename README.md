# Plateforme de gestion scolaire multitenant

Application SaaS multitenant (web + mobile Flutter) de gestion scolaire, destinée aux collèges,
lycées, universités et grandes écoles. Chaque établissement dispose d'un espace isolé, de sa
propre URL et de son propre branding.

**État du projet** : spécification. Le code applicatif n'est pas encore écrit — le dépôt contient
le squelette Laravel 13 et la documentation de référence.

## Documentation

| Document | Contenu |
|---|---|
| [`docs/01-cahier-des-charges-v2.md`](docs/01-cahier-des-charges-v2.md) | Cahier des charges fonctionnel complet (source, conservé pour traçabilité) |
| [`docs/02-addendum-v3-securite-performance.md`](docs/02-addendum-v3-securite-performance.md) | **Normatif.** Protection des API, gestion des secrets, stratégie d'identifiants, performance, CI/CD et mise en production |
| [`docs/03-rapport-evaluation-code.md`](docs/03-rapport-evaluation-code.md) | Évaluation des propositions techniques de la v2 : ce qui est validé, amendé, écarté |
| [`docs/04-charte-graphique.md`](docs/04-charte-graphique.md) | Charte « Ivoire & Encre » : jetons, typographie, composants, accessibilité |

L'addendum v3 **remplace** certaines sections du cahier v2 ; le tableau de correspondance
figure en tête de ce document.

## Pile technique

| Couche | Choix |
|---|---|
| Back-end | Laravel 13 / PHP 8.3 |
| Base de données | PostgreSQL 16 (partitionnement, RLS, index partiels) |
| Cache, sessions, files d'attente | Redis 7 |
| Front-end web | Blade + Vite + Tailwind CSS 4 |
| Mobile | Flutter (iOS + Android) |
| Infrastructure | VPS + Nginx, Cloudflare (DNS, SSL joker, CDN, WAF) |
| CI/CD | GitHub Actions |

## Principes non négociables

Ces règles conditionnent l'architecture et sont vérifiées automatiquement :

1. **Isolation multitenant à trois barrières** — scope d'ORM, Row-Level Security PostgreSQL,
   suite de tests d'isolation par endpoint.
2. **Refus par défaut** — toute route est authentifiée et autorisée sauf inscription explicite
   en liste blanche.
3. **Identifiants séparés** — `id` numérique interne pour les jointures, `public_id` UUID pour
   l'exposition, identifiant métier (matricule/INE) pour l'humain.
4. **Aucun secret dans le dépôt** — le `.env` de production est généré au déploiement depuis
   GitHub Environments.
5. **Performance vérifiée, pas espérée** — budgets de requêtes SQL et de latence appliqués en CI
   sur un jeu de données de 100 000 apprenants.
6. **Aucune erreur technique brute en production** — page générique pour l'utilisateur, alerte
   détaillée au super-admin.

> Une exigence de sécurité ou de performance qui n'est pas vérifiée automatiquement par un test
> ou par la CI n'existe pas.

## Mise en route (développement)

```bash
composer setup
composer dev
```

Avant la première migration, appliquer les correctifs de configuration listés dans
[`docs/03-rapport-evaluation-code.md`](docs/03-rapport-evaluation-code.md) §4 — notamment le
passage de SQLite à PostgreSQL, qui conditionne le partitionnement et la Row-Level Security.
