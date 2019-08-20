# Spécifications de l'application ADE-scheduler
Sur base des données fournies par le site ade-uclouvain, l'application obtient les données et les traite.

## Objectifs
L'utilisateur peut
- visualiser le calendrier en temps réel
- créer un fichier .ics téléchargeable à partir du calendrier visionnié
- ajouter et supprimer des cours via leur code cours
- sélectionner, par cours, les éléments que l'on veut garder
  - ex. : pour le cours de proba, on choisit de ne prendre que le TP n°3, le mercredi à 14h00
- générer les "n" meilleurs horaires, minimisant les conflits horaires
- rajouter des slots horaires pendant lesquels on veut être libre
- sauvegarder son calendrier (sauve les paramètres dans la base de donnée) et obtenir un code pour récuperer à tout moment la dernière version à jour du calendrier
  - utilité : via une url, récuperer un calendrier (via son code) en format .ics -> ceci peut faire office de lien d'abonnement iCalendar

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

### `html` pour
- les pages webs

### `javascript` pour
- les pages webs
- affichage du calendrier avec FullCalendar
