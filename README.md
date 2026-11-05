# Archivéo

**Annuaire des archives en ligne utiles à la généalogie en France** — et un outil qui dit, pour un nom, une période et un lieu, *quelles* archives peuvent répondre.

816 services recensés : archives départementales (101), nationales / militaires / guerres (52), municipales et régionales (114), associations et cercles généalogiques (190), entreprises, cultes, hôpitaux, écoles (71), et 288 autres services issus de l'annuaire officiel des archives publiques (municipales, régionales, hospitalières, universitaires, privées) dont les fonds en ligne restent à décrire.

> Prototype. Les données ont été collectées le 4 novembre 2026 à partir de sources de synthèse (data.gouv.fr, Geneanet, FranceArchives, annuaires spécialisés, sites des services). Une partie des lignes porte la mention **« à vérifier »** : URL non confirmée ou contenu non vérifié. Les contributions sont bienvenues.

## Contenu du dépôt

```
index.html   Le site (statique, aucun serveur nécessaire) — data.js contient les données
data/        Les données sources (5 fichiers CSV, séparateur « ; ») + le tableur Excel consolidé
scripts/     build_data.py (CSV → data.js), build_xlsx.py (CSV → tableur), archiveo_compte.py (comptage en ligne de commande)
extension/   Extension Chrome/Edge qui compte les résultats dans votre navigateur
```

## Le site

En ligne : **https://danmonceau.fr/Archiveo/**. En local : ouvrez `index.html` dans un navigateur, ou servez le dossier (`python -m http.server 8000`).

Deux modes :

- **Annuaire** — recherche plein texte (département, ville, région, organisme, type de fonds), onglets par famille, filtres par fonds (état civil, matricules, cadastre…), favoris. Les fiches d'archives départementales montrent, fonds par fonds, ce qui est en ligne et pour quelle période.
- **Qui peut me répondre ?** — nom, prénom, année de naissance approximative, lieu. Le site renvoie :
  1. les bases qui **répondent directement à un nom** (Geneanet, FamilySearch, Filae, Grand Mémorial, Mémoire des Hommes, Léonore, FranceArchives, Arolsen, fichier des décès INSEE, Gallica, RetroNews…), filtrées par période de vie, avec lien pré-rempli quand le site le permet ;
  2. les **registres à feuilleter** aux archives départementales du lieu, limités aux fonds qui couvrent la période (un homme né en 1885 : état civil, recensements 1886-1936, matricule classe 1905… mais pas le cadastre napoléonien) ;
  3. les **archives municipales** et **relevés d'associations** du département.

## L'extension (comptage des résultats)

Les bases d'archives ne sont pas interrogeables depuis une page web (pas d'API, protections anti-robot). L'extension contourne ça proprement : elle ouvre chaque source **dans votre navigateur, avec vos sessions** (Geneanet, Filae…), lit le nombre de résultats affiché, le renvoie au site et ferme l'onglet.

Installation (Chrome, Edge, Brave) :

1. `chrome://extensions` ou `edge://extensions` → activer le **Mode développeur**.
2. **Charger l'extension non empaquetée** → choisir le dossier `extension/`.
3. Si le site est ouvert en `file://`, activer « Autoriser l'accès aux URL de fichier » dans les détails de l'extension.
4. Recharger le site : le bandeau « Extension détectée » apparaît dans le mode « Qui peut me répondre ? », avec le bouton **Compter les résultats**.

Fonctionnement : `bridge.js` fait le pont page ↔ extension (`window.postMessage`), `background.js` ouvre les sources 3 par 3 en arrière-plan, `counter.js` est injecté dans chaque onglet pour lire le compteur. L'extraction est générique (« N résultats », « N … trouvés », « 1-20 sur N ») avec des règles par site quand il le faut — aujourd'hui **Léonore** (pas d'URL de recherche : l'extension saisit le nom et valide). Les sites qui demandent une connexion ou une vérification anti-robot sont signalés comme tels.

Pour ajouter une règle de site : dans `counter.js`, section « Règles propres à certains sites », tester `location.hostname` et renvoyer `{ count, status, snippet }`.

## Contribuer

Depuis le site : lien **« Corriger »** sur chaque fiche, bouton **« Proposer un ajout »** en tête de page. Les deux ouvrent un formulaire Google pré-rempli (aucun compte nécessaire) ; les réponses arrivent dans une feuille de calcul. Les développeurs peuvent aussi ouvrir une issue ou une pull request ici. Les corrections acceptées sont reportées dans les CSV de `data/`, puis `data.js` est régénéré.

## Mettre à jour les données

1. Modifier les CSV dans `data/` (séparateur `;` — ne pas utiliser `;` à l'intérieur d'un champ).
2. `python3 scripts/build_data.py` → régénère `data.js`.
3. `python3 scripts/build_xlsx.py` → régénère le tableur (nécessite `openpyxl`).

Colonnes du tableur / des CSV : voir l'onglet **Synthèse** du fichier Excel (légende).

## Le script de comptage (sans extension)

```
python3 scripts/archiveo_compte.py Monceau --annee 1885 --lieu Moselle
```

Interroge les bases à API ouverte (fichier des décès INSEE via matchID, Gallica SRU, Open Archives) et ouvre les autres dans des onglets pré-remplis. Python 3 seul, rien à installer. Ajouter `--no-open` pour n'afficher que les liens.

## Limites connues

- Les **tables décennales** ne sont pas distinguées de l'état civil par les sources de synthèse : colonne à remplir site par site.
- Beaucoup de sites associatifs bloquent les robots : les lignes de l'onglet *Associations* sont les moins vérifiées.
- Hors périmètre pour l'instant : pays frontaliers (Belgique, Allemagne, Suisse, Luxembourg, Italie, Espagne), archives des petites communes.
- L'extension fonctionne sur ordinateur uniquement ; un site qui change de mise en page peut casser son compteur.

## Sources principales

- [data.gouv.fr — Principaux corpus d'archives numérisés et mis en ligne par les archives départementales](https://www.data.gouv.fr/datasets/68ef546997d5b57ab7ab93f4)
- [Geneanet — Archives départementales en ligne](https://www.geneanet.org/explore/beginners/post/archives-departementales-ligne/)
- [FranceArchives](https://francearchives.gouv.fr/) et l'[Annuaire des services d'archives publiques en France](https://data.culturecommunication.gouv.fr/explore/dataset/annuaire-des-services-darchives-publiques-en-france/) (ministère de la Culture) — copie dans `data/annuaire_services_archives_officiel.csv`
- [Geneabank — associations participantes](https://www.geneabank.org/gensocs/indexfr.html)
- [La Revue française de Généalogie — annuaire](https://www.rfgenealogie.com/annuaire/associations)
- Annuaires aupresdenosracines.com, archiveenligne.fr, genealogiepratique.fr

## Licence

Code : MIT. Données : agrégées depuis des sources publiques, à réutiliser en citant les sources ci-dessus.
