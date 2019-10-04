# ADE-Scheduler : un outil horaire destiné aux étudiants

[ADE-Scheduler](https://ade-scheduler.info.ucl.ac.be/) est un outil créé par des étudiants et à destination des membres de l'UCLouvain, et plus particulièrement les étudiants de l'EPL.

## Initiateurs du projet :

- [Eertmans Jérome](https://www.linkedin.com/in/j%C3%A9rome-eertmans-130ab1130/)
- [Navarre Louis](https://www.linkedin.com/in/louis-navarre-36b78b143/)
- [Poncelet Gilles](https://www.linkedin.com/in/gilles-poncelet-020442195/)

Nous sommes trois étudiants de l'EPL et entrions tout juste en master 1 quand nous avons commencé ce projet.

## Raison d'existence

Face au service très peu intuitif qu'est le service d'horaire [ade](http://horaire.uclouvain.be/direct/) fourni par l'UCLouvain, nous avons décidé de créer cet outil afin de faciliter la création d'horaire via une interface plus esthitique, plus complète et offrant [un panel d'options assez large](##Fonctionnalités).

## Dates importantes

- **Début août 2019** : début du projet
- **Début septembre 2019** : obtiention d'un accès à l'api de ADE
- **Mi-septembre 2019** : mise en ligne du site au monde entier

## Comment cela fonctionne

### Back-end <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/1024px-Python-logo-notext.svg.png" alt="python" width="20" height="20"></img>

#### L'obtention des données

Grâce à notre accès à l'api de ADE, nos pouvons obtenir toutes les informations dans un format XML.
De ces données, nous intéressent :
- la liste de événements par cours (type d'événement, lieu, durée, date, professeur, ...)
- la liste des locaux de l'UCLouvain et, quand disponible, leur adresse postale

#### Le traitement des données

Les données sont essentiellement traitées avec du Python pure et des méthodes built-in. Néanmoins, le package [pandas](https://pandas.pydata.org/) est presque indispensable pour atteindre de bonnes performances et le package [ics](https://pypi.org/project/ics/) est fort utile quand à la conversion en format iCal.

Nous utilisons un serveur [redis](https://redis.io) afin de stocker toutes les sessions des utilisateurs mais aussi les résultats des requêtes afin de minimiser l'utilisation d'ADE.

#### Front-end <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/1024px-Python-logo-notext.svg.png" alt="python" width="20" height="20"></img> <img src="https://www.w3.org/html/logo/downloads/HTML5_Badge_512.png" alt="html" width="20" height="20"></img> <img src="https://i1.wp.com/www.thekitchencrew.com/wp-content/uploads/2016/03/js-logo.png?fit=500%2C500" alt="js" width="20" height="20"></img>

L'application web est entièrement gérée grâce au module [Flask](https://pypi.org/project/Flask/). Le côté esthétique est en grosse partie dû à l'usage de deux bibliothèques : [FullCalendar](https://fullcalendar.io) et [Bootstrap](https://getbootstrap.com/).

Le serveur et le nom de domaine nous ont été prêtés par le pôle INGI de l'EPL.

## Fonctionnalités

Ici, sont listées les différentes fonctionnalités qu'offre notre site web :
- visualisation du calendrier en temps réel
- ajout et suppression des cours via leur code cours
- sélection, par cours, des éléments à garder
  - ex. : pour le cours de Probabilité (LFSAB1105), on choisit de ne prendre que le TP n°3, le mercredi à 14h00
  - ex. : pour le cours de Logique (LINGI1101), on choisit de ne prendre en compte que les cours magistraux
- ajout de slots horaires pendant lesquels on souhaite être libre (avec divers niveaux de priorité)
- génération les "n" meilleurs horaires, minimisant les conflits horaires, et respectant au maximum les souhaits de l'utilisateur, selon une fonction de coûts à minimiser (par exemple : un conflit horaire génère un cout élevé)
- création un fichier .ics téléchargeable à partir du calendrier visionnié
- sauvegarde d'un calendrier (sauve les paramètres dans une base de donnée) et obtention d'un code pour récupérer à tout moment la dernière version du calendrier selon les dernières informations de ADE-UCLouvain
  - utilité : via une url, récupérer un calendrier (via son encodage) en format .ics -> ceci peut faire office de lien d'abonnement iCalendar
- site disponible en français et en anglais
- liste de tous les locaux de l'UCLouvain avec, si dispobible, leur adresse
- possibiblité de voir le planning horaire lié à un local

### Documentation

La documentation du site web est disponible sur [la page d'aide](https://ade-scheduler.info.ucl.ac.be/help) de ce dernier.

### Améliorations futures

Ici, sont listées, par ordre de priorité, les améliorations que nous jugeons intéressantes à ajouter dans un futur plus ou moins proche :
- créer une version mobile du site plus accessible
- implémenter une suite de tests à effectuer sur tout code pull-request
- finir videos de la section aide
- corriger texte (mise en page + orthographe) de l'aide

### Contribuer

Cette application étant open-source, vous êtes invités à contribuer à cette dernière de quelque manière !

Cette section est encore en cours de développement mais n'hésitez pas à nous contacter par [mail](adescheduler@gmail.com) ou sur ce repo !
