# Spécifications de l'application ADE-scheduler
Sur base des données fournies par l'api ade de l'UCLouvain, l'application obtient les données et les traite.

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
- avoir le site en : anglais / français
- participer au développement de l'application (pull request)

## Mises à jours à venir (par ordre de priorité)

Doit être fait
- (plus) facilement créer des FTS récurrents
- suite de tests à effectuer sur tout code pull-request
- finir videos de la section aide
- corriger texte (mise en page + orthographe) de l'aide
- créer une version mobile plus accessible

L'utilisateur pourra
- participer au développement de l'application (pull request) de manière sûre : suite de tests à effectuer sur tout code
- integrer un calendrier personnel externe (.ics / abonnement)
- se connecter avec son compte MyUCL afin que l'application obtienne la liste des cours auquel il est inscrit et la mette par défaut dans le calendrier [?]

## Langages utilisés

### `Python` pour
- communiquer avec ADE et récupérer les données
- effectuer tous les calculs sur les calendriers
- gestion de l'application avec Flask
- gestion d'une base de donnée SQLite afin de stocker 
  - les liens d'abonnements + les paramètres d'un utilisateur afin de pouvoir reconstituer son calendrier/sa session sur demande
- gestion d'un "cache" de mémoire Redis pour:
  - stocker les cours pendant 24h afin de limiter la quantité de requêtes ADE
  - les sessions des utilisateurs d'une actualisation à une autre

### `HTML` pour
- les pages webs

### `JavaScript` pour
- les pages webs
- affichage du calendrier avec FullCalendar (fullcalendar.io)
