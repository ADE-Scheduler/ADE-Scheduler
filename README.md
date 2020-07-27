
<p align="center">
  <img src="https://github.com/SnaKyEyeS/ADE-Scheduler/blob/AS-2.0/static/img/ade_scheduler_icon.png" width="200" height="200"> </img>
</p>

# ADE-Scheduler : un outil horaire destiné aux étudiants

[ADE-Scheduler](https://ade-scheduler.info.ucl.ac.be/) est un outil créé par des étudiants et à destination des membres de l'UCLouvain, et plus particulièrement les étudiants de l'EPL.

## Initiateurs du projet :

- [Eertmans Jérome](https://www.linkedin.com/in/j%C3%A9rome-eertmans-130ab1130/)
- [Navarre Louis](https://www.linkedin.com/in/louis-navarre-36b78b143/)
- [Poncelet Gilles](https://www.linkedin.com/in/gilles-poncelet-020442195/)

Nous sommes trois étudiants de l'EPL et entrions tout juste en master 1 quand nous avons commencé ce projet.

## Raison d'existence

Face au service très peu intuitif qu'est le service d'horaire [ade](http://horaire.uclouvain.be/direct/) fourni par l'UCLouvain, nous avons décidé de créer cet outil afin de faciliter la création d'horaire via une interface plus esthitique, plus complète et offrant un panel d'options assez large.

Avant cela, nous utilisions le très bon outil [ADE2ICS](https://github.com/cdamman/UCL2ICS), réalisé par Corentin Damman, qui nous permettait de créer des liens d'abonnements dans lequel on pouvait choisir nos TPs / CMs. ADE-Scheduler est donc une amélioration de cet outil.

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

### Front-end <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/1024px-Python-logo-notext.svg.png" alt="python" width="20" height="20"></img> <img src="https://www.w3.org/html/logo/downloads/HTML5_Badge_512.png" alt="html" width="20" height="20"></img> <img src="https://i1.wp.com/www.thekitchencrew.com/wp-content/uploads/2016/03/js-logo.png?fit=500%2C500" alt="js" width="20" height="20"></img>

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

### Tableau comparatif avec ADE
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

## Documentation

La documentation du site web est disponible sur [la page d'aide](https://ade-scheduler.info.ucl.ac.be/help) de ce dernier.

## Améliorations futures

Ici, sont listées, par ordre de priorité, les améliorations que nous jugeons intéressantes à ajouter dans un futur plus ou moins proche :
- créer une version mobile du site plus accessible
- implémenter une suite de tests à effectuer sur tout code pull-request
- finir videos de la section aide
- corriger texte (mise en page + orthographe) de l'aide

## Installation

### 1. Installez Redis
Pour installer un serveur Redis, référez-vous au site https://redis.io/topics/quickstart.

### 2. Clonez ce repo

`git clone https://github.com/SnaKyEyeS/ADE-Scheduler`

### 3. Installez les packages Python requis

(Optionnel) Créez un environnement virtuel:
```
cd <repo>
pip3 install venv
source venv/bin/activate
```

L'installation des packages se fait via la commande suivante:
```
pip3 install -r requirements.txt
```

### 4. Installez les packages Node requis
Installez d'abord Node.js si ce n'est pas déjà fait: https://nodejs.org/en/download/  
Ensuite, installez les modules NodeJS:
```
cd <repo>
npm install
```

Pour assembler tous les assets .js et .css, il suffit d'exécter la commande `npx webpack`.  
Pour éviter de devoir exécuter cette commande à chaque changement dans le code, il est
possible de dire à Webpack d'automatiquement s'exécuter à chaque changement avec
la commande `npx webpack --mode development --watch`.

Il est possible qu'une erreur apparaisse concernant le nombre maximum de 'watchers' autorisé. Une solution sur Linux est d'exécuter: `echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf && sudo sysctl -p`. (https://stackoverflow.com/questions/53930305/nodemon-error-system-limit-for-number-of-file-watchers-reached)

### 5. Initialisez la base de données

Spécifiez une variable d'environnement `ADE_DB_PATH` contenant l'URI vers une base de données SQL.
Par exemple, vous pouvez simplement spécifier `ADE_DB_PATH = "sqlite:///path_to_db"` ce qui conduira à la création d'une base de données SQLite au path spécifié. Ensuite, exécutez ces commandes pour l'initialiser et créer les tables proprement:
```
cd <repo>
flask shell
db.create_all()
```

### 6. Accès à l'API de ADE (optionnel)

#### 6.1 Accéder grâce à des identifiants

Si vous possédez des identifiants d'accès à l'API de ADE, enregistrez les quelque part sur votre ordinateur dans un fichier JSON. Le contenu attendu est spéficié dans la classe **Credential** dans /backend/credentials.py.

Pour lier vos identifiants au projet :

```
python3
from backend.credentials import Credentials; Credentials.set_credentials("identifiants.json")
```

Un message vous attirera l'attention sur le fait que ce lien est ephémère : il faudra refaire cette commande pour chaque processus Python. Des solutions permanentes sont proposées par ce message.

#### 6.2 Accéder sans identifiants

Il n'est pas possible d'accéder à l'API sans identifiants valides et nous ne vous en fournirons pas. Cependant, une réplique de l'API peut être interfacée via la classe **DummyClient** dans /backend/ade_api.py.

#### 6.3 Documentation

Afin de faciliter la documentation de nos fonctions, nous utilisons Sphinx. La page contenant la documentation est /docs/build/html/index.html. Pour mettre à jour :
```
cd docs
sphinx-apidoc -o source/backend ../backend
make html
```

Pour savoir comment documenter votre code de la même manière que nous :
- https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html
- https://thomas-cokelaer.info/tutorials/sphinx/docstring_python.html

## Contribuer

Cette application étant open-source, vous êtes invités à contribuer à cette dernière de quelque manière !

Cette section est encore en cours de développement mais n'hésitez pas à nous contacter par [mail](mailto:adescheduler@gmail.com) ou sur ce repo !
