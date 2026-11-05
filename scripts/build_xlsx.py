import re, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

import os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data") + os.sep
def load(f):
    lines = [l for l in open(D+f, encoding="utf-8").read().splitlines() if l.strip()]
    rows = [re.split(r";(?! )", l) for l in lines]
    return rows[0], rows[1:]

SHEETS = [
 ("Départementales", "departementales.csv",
  {"numero":"N°","nom":"Département","url":"Site des archives","etat_civil":"État civil","tables_decennales":"Tables décennales",
   "recensements":"Recensements","matricules":"Registres matricules","cadastre":"Cadastre","notariat":"Notariat",
   "successions":"Successions","presse":"Presse","autres":"Autres fonds","source":"Source"}),
 ("Nationales & guerres", "nationales.csv",
  {"nom":"Service / base","categorie":"Catégorie","url":"URL","contenu_genealogique":"Contenu utile en généalogie",
   "acces":"Accès","recherche_nominative":"Recherche par nom","source":"Source / vérification"}),
 ("Municipales & régionales", "municipales.csv",
  {"nom":"Service","type":"Type","territoire":"Territoire","departement":"Dép.","url":"URL",
   "fonds_en_ligne":"Fonds en ligne","note":"Note (état civil hors AD, etc.)","source":"Source / vérification"}),
 ("Associations généalogiques", "associations.csv",
  {"nom":"Association","departement":"Dép.","territoire":"Territoire","url":"URL","contenu_en_ligne":"Ce qui est en ligne",
   "acces":"Accès","recherche_nominative":"Recherche par nom","source":"Source / vérification"}),
 ("Autres (annuaire officiel)", "officiel.csv",
  {"nom":"Service","categorie":"Catégorie officielle","code_postal":"Dép.","ville":"Ville","url":"URL","lien_francearchives":"Fiche FranceArchives","source":"Source"}),
 ("Collections indexées", "collections.csv",
  {"source":"Site","collection":"Collection","type":"Type","departement":"Dép.","periode":"Période","nb_documents":"Documents","url":"URL","acces":"Accès","source_releve":"Source"}),
 ("Entreprises & privées", "privees.csv",
  {"nom":"Organisme","categorie":"Catégorie","url":"URL","contenu_genealogique":"Contenu utile en généalogie",
   "acces":"Accès","recherche_nominative":"Recherche par nom","source":"Source / vérification"}),
]

FONT = "Arial"
hdr_fill = PatternFill("solid", fgColor="2B241C")
hdr_font = Font(name=FONT, bold=True, color="FFFFFF", size=10)
body = Font(name=FONT, size=10)
link = Font(name=FONT, size=10, color="8B3A2F", underline="single")
warn_fill = PatternFill("solid", fgColor="F7EAD0")
thin = Side(style="thin", color="E4DCCD")
border = Border(bottom=thin)

wb = Workbook()
syn = wb.active; syn.title = "Synthèse"

counts = []
for title, f, cols in SHEETS:
    hdr, rows = load(f)
    ws = wb.create_sheet(title)
    names = [cols.get(h, h) for h in hdr]
    names.append("Vérifié le")
    ws.append(names)
    for c in range(1, len(names)+1):
        cell = ws.cell(1, c); cell.fill = hdr_fill; cell.font = hdr_font
        cell.alignment = Alignment(vertical="center", wrap_text=True)
    url_idx = hdr.index("url")
    for r in rows:
        r = r + [""]*(len(hdr)-len(r))
        ws.append(r + [""])
        i = ws.max_row
        for c in range(1, len(names)+1):
            cell = ws.cell(i, c); cell.font = body; cell.border = border
            cell.alignment = Alignment(vertical="top", wrap_text=True)
        u = ws.cell(i, url_idx+1)
        m = re.match(r"(https?://\S+)", u.value or "")
        if m:
            u.hyperlink = m.group(1); u.font = link
        if any("à vérifier" in x for x in r):
            ws.cell(i, 1).fill = warn_fill
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    widths = {"N°":6,"Dép.":9,"Département":20,"Site des archives":34,"URL":40,"Service / base":38,"Organisme":38,"Service":40,
              "Catégorie":16,"Type":16,"Territoire":26,"Accès":22,"Recherche par nom":14,"Source":28,"Source / vérification":30,
              "Vérifié le":12,"Note (état civil hors AD, etc.)":40}
    for c, n in enumerate(names, 1):
        ws.column_dimensions[get_column_letter(c)].width = widths.get(n, 30)
    counts.append((title, len(rows)))

# Synthèse
syn["A1"] = "Archivéo — annuaire des archives en ligne (France)"; syn["A1"].font = Font(name=FONT, bold=True, size=14)
syn["A2"] = "Jeu de données de départ pour l'annuaire. Collecté le 4 novembre 2026. Les lignes surlignées en jaune contiennent une mention « à vérifier »."
syn["A2"].font = body
syn["A4"] = "Onglet"; syn["B4"] = "Nombre d'entrées"
for c in ("A4","B4"):
    syn[c].fill = hdr_fill; syn[c].font = hdr_font
for i, (t, n) in enumerate(counts, 5):
    syn.cell(i, 1, t).font = body
    syn.cell(i, 2, f"=COUNTA('{t}'!A:A)-1").font = body
syn.cell(5+len(counts), 1, "Total").font = Font(name=FONT, bold=True, size=10)
syn.cell(5+len(counts), 2, f"=SUM(B5:B{4+len(counts)})").font = Font(name=FONT, bold=True, size=10)

r = 7 + len(counts)
syn.cell(r, 1, "Légende").font = Font(name=FONT, bold=True, size=11)
legend = [
 ("Colonnes de fonds (onglet Départementales)", "« oui (…) » = fonds numérisé en ligne, avec période quand la source la donne ; vide = non signalé en ligne."),
 ("Tables décennales", "Aucune source de synthèse ne les distingue de l'état civil : à compléter site par site."),
 ("Jaune", "Au moins une mention « à vérifier » : URL non joignable depuis l'outil de collecte ou contenu non confirmé."),
 ("Vérifié le", "Colonne à remplir à la main lors de la vérification manuelle de chaque ligne."),
 ("Sources principales", "data.gouv.fr « Principaux corpus d'archives numérisés… par les AD » (oct. 2025) ; Geneanet « AD en ligne » (2026) ; annuaires aupresdenosracines.com, archiveenligne.fr, genealogiepratique.fr ; rfgenealogie.com ; sites des services (test HTTP)."),
 ("Associations", "Cercles généalogiques et bases de relevés (Geneabank, etc.) : l'accès est le plus souvent réservé aux adhérents. Bigenet est fermé depuis 2019."),
 ("Hors périmètre pour l'instant", "Pays frontaliers (Belgique, Allemagne, Suisse, Luxembourg, Italie, Espagne) et archives des petites communes."),
]
for k, v in legend:
    r += 1
    syn.cell(r, 1, k).font = Font(name=FONT, bold=True, size=10)
    syn.cell(r, 2, v).font = body
    syn.cell(r, 2).alignment = Alignment(wrap_text=True, vertical="top")
syn.column_dimensions["A"].width = 42; syn.column_dimensions["B"].width = 100

wb.save(os.path.join(D, "Annuaire_archives_France.xlsx"))
print(counts)
