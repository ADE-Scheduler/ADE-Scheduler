
<p align="center">
  <img src="static/img/ade_scheduler_icon.png" width="200" height="200"> </img>
</p>

# ADE Scheduler: a scheduling tool made for humans

[ADE-Scheduler](https://ade-scheduler.info.ucl.ac.be/) is a web-application made by students which is destined to be used by UCLouvain members (students, academics,...).

### Project creators

- [Eertmans Jérome](https://www.linkedin.com/in/j%C3%A9rome-eertmans-130ab1130/)
- [Navarre Louis](https://www.linkedin.com/in/louis-navarre-36b78b143/)
- [Poncelet Gilles](https://www.linkedin.com/in/gilles-poncelet-020442195/)

We are three students from the Ecole Polytechnique de Louvain (EPL) and were starting our first master year at the start of the project.

### Why such a tool ?

The currently used scheduling tool used by the UCLouvain, [ADE](http://horaire.uclouvain.be/direct/), lacks an intuitive interface and general usability. Therefore, we decided to create ADE-Scheduler as a "wrapper" around this tool to make it more intuitive, nice and complete.

Before that, we were using the excellent [ADE2ICS](https://github.com/cdamman/UCL2ICS) made by Corentin Damman which allowed to create subscription links where one could select its events (TPs, CMs, etc). ADE-Scheduler is therefore an improvement of this tool.

### Key dates

- **August 2019** : start of the project
- **September 2019** : access to the API of ADE and release of the first version of the tool
- **Summer 2020**: complete overhaul of the tool to make it more attractive, intuitive and mobile-friendly.
- **September 2020**: release of the second version of the tool

### How does it work ?

#### Back-end <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/1024px-Python-logo-notext.svg.png" alt="python" width="20" height="20"></img>

##### Data source

Thanks to the access to the API of ADE, we obtain all the information in a `XML` format. Those are up-to-date with the infos you will find on the ADE website. We are mainly interested in two type of informations:
 - Event list sorted by course
 - Location of every UCLouvain classroom, auditorium, etc.

#### Data treatmeant

The backend of ADE-Scheduler is written in Python using the [Flask](https://flask.palletsprojects.com/en/1.1.x/) micro-framework. Other packages are also used to supply many useful functions to enhance the overall user experience.\
Among those, we use [pandas](https://pandas.pydata.org/) pandas to optimise the performances, [ics](https://pypi.org/project/ics/) to convert the schedules in the iCal format, [Flask-Security](https://pypi.org/project/Flask-Security-Too/) to handle user registrations and security aspects - and many more.

We also use a [Redis](https://redis.io) server to store user sessions and buffer data, as well as a [PostgreSQL](https://www.postgresql.org/) database to store user accounts and schedules.

### Front-end <img src="https://www.w3.org/html/logo/downloads/HTML5_Badge_512.png" alt="html" width="20" height="20"></img> <img src="https://i1.wp.com/www.thekitchencrew.com/wp-content/uploads/2016/03/js-logo.png?fit=500%2C500" alt="js" width="20" height="20"></img>

Client-side logic is handled using [Vue](https://vuejs.org/), a JavaScript reactive framework. Moreover, the events are displayed on a calendar generated with the help of the [FullCalendar](https://fullcalendar.io) package.

The UI is made mainly with the help of [Bootstrap](https://getbootstrap.com/), which handles all the CSS and makes the website enjoyable and mobile-friendly.


### Fonctionnalités

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

#### Comparaison with ADE
Dans un objectif de palier aux problèmes rencontrés sur ADE, voici les solutions que nous avons mises en place :

| Problème sur ADE                             | Notre solution                                      |
|----------------------------------------------|-----------------------------------------------------|
| Connexion avec mot de passe                  | Pas de mot de passe requis                          |
| Session d'une durée très courte              | Pas de déconnexion de session en cours              |
| Aucune sauvegarde de la session              | Votre session est sauvergardée sur notre serveur    |
| Pas de lien d'abonnement                     | Possibilité de lien d'abonnement                    |
| Pas de compte personnel                      | Création d'un compte personnel                      |
| \                                            | Possibilité de mettre à jour son abonnement         |
| Sélection de plusieurs cours difficile       | Sélection de plusieurs cours très aisée             |
| Encodage des TP / CM peu lisible             | Décodage des TP / CM                                |
| Sélection d'un TP parmi plusieurs impossible | Sélections des TP / CM au choix                     |
| Pas de couleur                               | Une couleur par code                                |
| Pas d'adresse des locaux                     | Adresse du local quand disponible                   |
| Peu de description de l'événement            | Description max. de l'événement (prof., cours, ...) |

### Documentation

The website's documentation is available on the [help page](https://ade-scheduler.info.ucl.ac.be/help).

### Future improvements

Here are listed a series of issues we would like to implement in the future:
 - Implement a complete testing suite to enable easy and robust CI
 - Complete the help section with more videos, tips, etc.

We are open to any suggestions !

## Contributing

This application being open source, everyone is more than welcome to contribute in any way !
To see more details about our contributing guidelines, please refer to [contributing](/CONTRIBUTING.md).

Any suggestion, idea or bugs are much appreciated, and you can contact us at all times either by [mail](mailto:adescheduler@gmail.com) or directly on this repository.
