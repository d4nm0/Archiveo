#!/usr/bin/env python3
"""Archivéo — compte les résultats dans les bases à API ouverte et ouvre les autres dans le navigateur.

Usage :
    python3 archiveo_compte.py NOM [PRENOM] [--annee 1885] [--lieu Moselle] [--no-open]

Ne requiert que Python 3 (aucune bibliothèque à installer).
Les bases à protection anti-robot (Geneanet, Filae, FranceArchives, MémorialGenWeb…) ne sont PAS interrogées
automatiquement : elles sont ouvertes dans des onglets pré-remplis, à toi de lire le nombre de résultats.
"""
import argparse, json, re, sys, urllib.parse, urllib.request, webbrowser, xml.etree.ElementTree as ET

UA = "Archiveo/0.1 (outil personnel de généalogie)"

def get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json, text/xml, */*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")

def q(s): return urllib.parse.quote(s)

# ---------- Sources avec API : renvoient un nombre ----------
def matchid(nom, prenom, annee, lieu):
    """Fichier des décès INSEE (depuis 1970) via deces.matchid.io — API publique JSON."""
    url = f"https://deces.matchid.io/deces/api/v1/search?q={q((prenom+' '+nom).strip())}&size=1"
    data = json.loads(get(url))
    return data["response"]["total"], f"https://deces.matchid.io/search?q={q((prenom+' '+nom).strip())}"

def gallica(nom, prenom, annee, lieu):
    """Presse et livres BnF — API SRU officielle (gallica.bnf.fr/SRU)."""
    terme = f'"{(prenom+" "+nom).strip()}"'
    url = ("https://gallica.bnf.fr/SRU?operation=searchRetrieve&version=1.2&maximumRecords=1"
           f"&query={q('text all ' + terme)}")
    root = ET.fromstring(get(url))
    n = root.find(".//{http://www.loc.gov/zing/srw/}numberOfRecords")
    return int(n.text), f"https://gallica.bnf.fr/services/engine/search/sru?operation=searchRetrieve&version=1.2&query={q('text all ' + terme)}"

def openarch(nom, prenom, annee, lieu):
    """Open Archives (Pays-Bas, Belgique) — API publique (api.openarch.nl)."""
    url = f"https://api.openarch.nl/1.0/records/search.json?name={q((prenom+' '+nom).strip())}&lang=fr&number_show=1"
    data = json.loads(get(url))
    return int(data["response"]["number_found"]), f"https://www.openarchieven.nl/search.php?name={q((prenom+' '+nom).strip())}&lang=fr"

API = [("Fichier des décès INSEE (matchID)", matchid),
       ("Gallica (BnF)", gallica),
       ("Open Archives (Benelux)", openarch)]

# ---------- Sources sans API : onglets pré-remplis ----------
def onglets(nom, prenom, annee, lieu):
    n, p, l = q(nom), q(prenom), q(lieu)
    pn = q((prenom+" "+nom).strip())
    liens = [
        ("Geneanet", f"https://www.geneanet.org/fonds/individus/?go=1&nom={n}&prenom={p}&place__0__={l}"),
        ("FamilySearch", f"https://www.familysearch.org/search/record/results?q.surname={n}&q.givenName={p}&q.anyPlace={l}"),
        ("FranceArchives", f"https://francearchives.gouv.fr/fr/search?q={pn}"),
        ("RetroNews", f"https://www.retronews.fr/search#allTerms={pn}"),
        ("Google Livres", f"https://www.google.com/search?tbm=bks&q=%22{pn}%22+{l}"),
    ]
    if not annee or 1867 <= annee <= 1900:
        liens.append(("Grand Mémorial (matricules 14-18)", f"https://francearchives.gouv.fr/fr/grand-memorial?q={pn}"))
    if not annee or annee <= 1945:
        liens.append(("Mémoire des Hommes", "https://www.memoiredeshommes.sga.defense.gouv.fr/"))
        liens.append(("Arolsen Archives", f"https://collections.arolsen-archives.org/fr/search?s={pn}"))
    if not annee or annee <= 1920:
        liens.append(("Base Léonore", f"https://www.leonore.archives-nationales.culture.gouv.fr/ui/?q={n}"))
        liens.append(("Filae", f"https://www.filae.com/recherche/?nom={n}&prenom={p}"))
    return liens

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("nom"); ap.add_argument("prenom", nargs="?", default="")
    ap.add_argument("--annee", type=int, default=0, help="année de naissance approximative")
    ap.add_argument("--lieu", default="", help="ville, département ou région")
    ap.add_argument("--no-open", action="store_true", help="ne pas ouvrir les onglets")
    a = ap.parse_args()

    print(f"\n=== {a.prenom} {a.nom}".strip() + (f" · né(e) vers {a.annee}" if a.annee else "") + (f" · {a.lieu}" if a.lieu else "") + " ===\n")
    print("Bases interrogées automatiquement (API) :")
    for label, fn in API:
        try:
            n, url = fn(a.nom, a.prenom, a.annee, a.lieu)
            print(f"  {label:40s} {n:>8} résultat(s)   {url}")
        except Exception as ex:
            print(f"  {label:40s} {'—':>8}  indisponible ({type(ex).__name__})")

    liens = onglets(a.nom, a.prenom, a.annee, a.lieu)
    print(f"\nSources à consulter dans le navigateur ({len(liens)} onglets) :")
    for label, url in liens:
        print(f"  {label:40s} {url}")
        if not a.no_open:
            webbrowser.open_new_tab(url)
    print("\nAstuce : --no-open pour n'afficher que les liens ; les sites protégés affichent eux-mêmes leur nombre de résultats.")

if __name__ == "__main__":
    main()
