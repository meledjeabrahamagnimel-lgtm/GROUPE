# -*- coding: utf-8 -*-
"""
Reconstruit docs/maquettes/assets/polices.css : Fraunces 600 et Public Sans 400 à 700, en woff2
intégrés (base64), pour que les maquettes s'ouvrent hors ligne avec les vraies polices.

Pourquoi un script plutôt que le fichier lui-même : polices.css fait ~100 ko de base64, illisible
en revue de code ; on versionne la recette, pas le résultat. Lancer une fois après un git pull :

    python outils/maquettes/generer_polices.py

Sécurité de la chaîne d'approvisionnement : les deux paquets npm sont téléchargés depuis le
registre officiel et leur empreinte SHA-512 est comparée à celle publiée par npm (épinglée
ci-dessous). Une empreinte différente arrête le script : rien n'est écrit.

Polices sous licence SIL Open Font License 1.1. Aucun appel à Google Fonts (charte § 3).
"""
import base64
import hashlib
import io
import tarfile
import urllib.request
from pathlib import Path

PAQUETS = {
    "fraunces": (
        "https://registry.npmjs.org/@fontsource/fraunces/-/fraunces-5.3.0.tgz",
        "LEHTOBiZufQzAvnAe2rZ8ZknbDS28Q9kzwb0L+gZJEmjLGr8hhZ/5NuHXwDuHBWhVXYoiGGXmrb0H6Ko/RrHTg==",
        "Fraunces", [600],
    ),
    "public-sans": (
        "https://registry.npmjs.org/@fontsource/public-sans/-/public-sans-5.3.0.tgz",
        "kjODI0S3zdv0mBYCIQ8TbBayaiqszpc2UbhJiO3bjIqVVXzcWfHSt2o3WBCLOY3juaGaQoy4MoWCcgmfI5hCuA==",
        "Public Sans", [400, 500, 600, 700],
    ),
}

ENTETE = """/* Polices de la charte « Ivoire & Encre », intégrées pour que les maquettes s'ouvrent hors ligne.
 * Fichier GÉNÉRÉ par outils/maquettes/generer_polices.py — ne pas modifier à la main.
 * Dans l'application, les mêmes woff2 seront servis depuis le domaine (bloc 1.4).
 * Fraunces et Public Sans : SIL Open Font License 1.1 (paquets @fontsource 5.3.0, sous-ensemble latin). */"""


def telecharger(url: str, integrite: str) -> bytes:
    with urllib.request.urlopen(url, timeout=60) as r:  # URL fixe, jamais fournie par l'utilisateur
        donnees = r.read()
    recu = base64.b64encode(hashlib.sha512(donnees).digest()).decode()
    if recu != integrite:
        raise SystemExit(f"Empreinte inattendue pour {url} : arrêt, aucun fichier écrit.")
    return donnees


def main() -> None:
    lignes = [ENTETE]
    for nom, (url, integrite, famille, graisses) in PAQUETS.items():
        archive = tarfile.open(fileobj=io.BytesIO(telecharger(url, integrite)), mode="r:gz")
        for g in graisses:
            membre = archive.extractfile(f"package/files/{nom}-latin-{g}-normal.woff2")
            b64 = base64.b64encode(membre.read()).decode()
            lignes.append(
                f"@font-face{{font-family:'{famille}';font-style:normal;font-weight:{g};"
                f"font-display:swap;src:url(data:font/woff2;base64,{b64}) format('woff2');}}"
            )
    racine = Path(__file__).resolve().parents[2]
    sortie = racine / "docs" / "maquettes" / "assets" / "polices.css"
    sortie.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    print(f"{sortie.relative_to(racine)} écrit ({sortie.stat().st_size // 1024} ko).")


if __name__ == "__main__":
    main()
