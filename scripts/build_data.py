import re, json
import os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data") + os.sep
def load(f):
    lines = [l for l in open(D+f, encoding="utf-8").read().splitlines() if l.strip()]
    rows = [re.split(r";(?! )", l) for l in lines]
    return [dict(zip(rows[0], r + [""]*(len(rows[0])-len(r)))) for r in rows[1:]]

REG = {}
for reg, deps in {
 "Auvergne-Rhône-Alpes":"01 03 07 15 26 38 42 43 63 69 73 74","Bourgogne-Franche-Comté":"21 25 39 58 70 71 89 90",
 "Bretagne":"22 29 35 56","Centre-Val de Loire":"18 28 36 37 41 45","Corse":"2A 2B",
 "Grand Est":"08 10 51 52 54 55 57 67 68 88","Hauts-de-France":"02 59 60 62 80","Île-de-France":"75 77 78 91 92 93 94 95",
 "Normandie":"14 27 50 61 76","Nouvelle-Aquitaine":"16 17 19 23 24 33 40 47 64 79 86 87",
 "Occitanie":"09 11 12 30 31 32 34 46 48 65 66 81 82","Pays de la Loire":"44 49 53 72 85",
 "Provence-Alpes-Côte d'Azur":"04 05 06 13 83 84","Outre-mer":"971 972 973 974 976 975 986 987 988"}.items():
    for d in deps.split(): REG[d]=reg
SUB = {"67":"Alsace","68":"Alsace","54":"Lorraine","55":"Lorraine","57":"Lorraine","88":"Lorraine"}

def st(v):
    v=v.strip()
    if not v or v.startswith("non"): return "no"
    if "à vérifier" in v or "non précisée" in v or "lien Geneanet" in v: return "warn"
    return "ok"
def per(v):
    m=re.search(r"\((.*?)\)", v); return m.group(1) if m else ""

out=[]
for r in load("departementales.csv"):
    fonds=[]
    for k,lab in [("etat_civil","État civil"),("tables_decennales","Tables décennales"),("recensements","Recensements"),
                  ("matricules","Registres matricules"),("cadastre","Cadastre"),("notariat","Notariat"),
                  ("successions","Successions"),("presse","Presse")]:
        v=r[k]; fonds.append([lab, per(v) if st(v)!="no" else "—", st(v)])
    url=re.match(r"(https?://\S+)", r["url"]);
    out.append({"cat":"departementale","num":r["numero"],"nom":r["nom"],"region":REG.get(r["numero"],""),
        "sub":SUB.get(r["numero"],""),"url":url.group(1) if url else "","site":re.sub(r"^https?://(www\.)?","",url.group(1)).rstrip("/") if url else "",
        "fonds":fonds,"autres":r["autres"],"verif":"à vérifier" in r["url"],"type":"Archives départementales"})

for r in load("nationales.csv"):
    out.append({"cat":"nationale","nom":r["nom"],"type":r["categorie"],"url":r["url"],"site":re.sub(r"^https?://(www\.)?","",r["url"]).rstrip("/"),
        "desc":r["contenu_genealogique"],"acces":r["acces"],"nominatif":r["recherche_nominative"],"verif":"à vérifier" in r["source"]})

for r in load("municipales.csv"):
    url=re.match(r"(https?://\S+)", r["url"])
    out.append({"cat":"municipale","nom":r["nom"],"type":r["type"],"num":r["departement"],"territoire":r["territoire"],
        "region":REG.get(r["departement"].split("/")[0],""),"url":url.group(1) if url else "",
        "site":re.sub(r"^https?://(www\.)?","",url.group(1)).rstrip("/") if url else "",
        "desc":r["fonds_en_ligne"],"note":r["note"],"verif":"à vérifier" in (r["url"]+r["source"]+r["note"])})

for r in load("associations.csv"):
    dep=r["departement"]; first=re.split(r"[/ ]",dep)[0]
    out.append({"cat":"association","nom":r["nom"],"type":"Association / cercle","num":dep if re.match(r"^[0-9AB/ +]+$",dep) else "","territoire":r["territoire"],
        "region":REG.get(first,""),"sub":SUB.get(first,""),"url":r["url"],"site":re.sub(r"^https?://(www\.)?","",r["url"]).rstrip("/"),
        "desc":r["contenu_en_ligne"],"acces":r["acces"],"nominatif":r["recherche_nominative"],"verif":"à vérifier" in (r["source"]+r["acces"]+r["contenu_en_ligne"])})

for r in load("privees.csv"):
    out.append({"cat":"privee","nom":r["nom"],"type":r["categorie"],"url":r["url"],"site":re.sub(r"^https?://(www\.)?","",r["url"]).rstrip("/"),
        "desc":r["contenu_genealogique"],"acces":r["acces"],"nominatif":r["recherche_nominative"],"verif":"à vérifier" in r["source"]})

for r in load("officiel.csv"):
    out.append({"cat":"officiel","nom":r["nom"],"type":r["categorie"],"num":r["code_postal"],"territoire":r["ville"],
        "region":REG.get(r["code_postal"],""),"sub":SUB.get(r["code_postal"],""),"url":r["url"],"site":re.sub(r"^https?://(www\.)?","",r["url"]).rstrip("/"),
        "desc":"Service recensé dans l'annuaire officiel des archives publiques (FranceArchives). Fonds en ligne non encore décrits : à compléter.",
        "note":"Fiche FranceArchives : "+r["lien_francearchives"],"verif":False})

open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data.js"),"w",encoding="utf-8").write("const DATA="+json.dumps(out,ensure_ascii=False)+";")
print(len(out), sum(1 for o in out if o["verif"]))
