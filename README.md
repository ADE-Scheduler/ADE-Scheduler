# Spécifications de l'application ADE-scheduler
Sur base des données fournies par le site ADE-UCLouvain, l'application obtient les données et les traite.

## Objectifs
L'utilisateur peut
- visualiser le calendrier en temps réel
- ajouter et supprimer des cours via leur code cours
- sélectionner, par cours, les éléments qu'il souhaite garder
  - ex. : pour le cours de Probabilité (LFSAB1105), il choisit de ne prendre que le TP n°3, le mercredi à 14h00
  - ex. : pour le cours de Logique (LINGI1101), il choisit de ne prendre en compte que les cours magistraux
- rajouter des slots horaires pendant lesquels il souhaite être libre (avec divers niveaux de priorité)
- générer les "n" meilleurs horaires, minimisant les conflits horaires, et respectant au maximum les souhaits de l'utilisateur, selon une fonction de coûts à minimiser (par exemple: un conflit horaire génère un cout élevé)
- créer un fichier .ics téléchargeable à partir du calendrier visionnié
- sauvegarder son calendrier (sauve les paramètres dans une base de donnée) et obtenir un code pour récupérer à tout moment la dernière version du calendrier selon les dernières informations de ADE-UCLouvain
  - utilité : via une url, récupérer un calendrier (via son code) en format .ics -> ceci peut faire office de lien d'abonnement iCalendar

## Objectifs bonus
L'utilisateur peut
- se connecter avec son compte MyUCL afin que l'application obtienne la liste des cours auquel il est inscrit et la mette par défaut dans le calendrier

## Langages utilisés

### `Python` pour
- communiquer avec ADE et récupérer les données
- effectuer tous les calculs sur les calendriers
- gestion de l'application avec Flask
- gestion d'une base de donnée SQLite afin de stocker 
  - les cours pour 24H et limiter la quantité de requêtes ADE en allant d'abord rechercher ce qu'il existe dans la base
  - les paramètres afin de reconstruire un calendrier à chaque requête de l'abonnement icalendar

### `HTML` pour
- les pages webs

### `JavaScript` pour
- les pages webs
- affichage du calendrier avec FullCalendar
