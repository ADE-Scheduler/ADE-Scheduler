# SETUP - Tout ce qu'il faut savoir afin de contribuer à ce projet

## Installation

### 1. Installez Redis
Pour installer un serveur Redis, référez-vous au site https://redis.io/topics/quickstart.

### 2. Clonez ce repo

`git clone https://github.com/SnaKyEyeS/ADE-Scheduler`

### 3. Créez un environnement virtuel Python (optionnel)

Placez-vous dans le dossier du projet et installer virtualenv (la procédure peut varier en fonction de votre OS)
```
cd <repo>
sudo apt install python3-virtualenv
virtualenv venv
source venv/bin/activate
```

### 4. Installez les packages Python requis

`pip3 install -r requirements.txt`

### 5. Installez les packages NodeJS requis
Installez d'abord Node.js et npm si ce n'est pas déjà fait : https://nodejs.org/en/
Ensuite, installez les modules:
```
cd <repo>
npm install
```  
Pour assembler tous les assets .js et .css, il suffit d'exécter la commande `npx webpack`  
Pour éviter de devoir exécuter cette commande à chaque changement dans le code, il existe la commande `npx webpack --watch .` qui dit à webpack d'automatiquement s'exécuter à chaque changement dans le code.

Il est possible qu'une erreur apparaisse concernant le nombre maximum de 'watchers' autorisé. Une solution sur Linux est d'exécuter: `echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf && sudo sysctl -p`. (https://stackoverflow.com/questions/53930305/nodemon-error-system-limit-for-number-of-file-watchers-reached)

## Configuration

### 1. Initialisez la base de données

Spécifiez une variable d'environnement `ADE_DB_PATH` contenant l'URI vers une base de données SQL.
Par exemple, vous pouvez simplement spécifier `ADE_DB_PATH = "sqlite:///path_to_db"` ce qui conduira à la création d'une base de données SQLite au path spécifié. Ensuite, exécutez ces commandes pour l'initialiser et créer les tables proprement:
```
cd <repo>
flask shell
db.create_all()
```

Note: si la DB utilisée est une DB MySQL, exécuter la soltuion au lien suivant pour éviter tout souci: https://stackoverflow.com/questions/18897420/data-too-long-for-column-why

### 2. Accès à l'API de ADE (optionnel)

#### 2.1 Accéder grâce à des identifiants

Si vous possédez des identifiants d'accès à l'API de ADE, enregistrez les quelque part sur votre ordinateur dans un fichier JSON. Le contenu attendu est spéficié dans la classe **Credential** dans /backend/credentials.py.

Pour lier vos identifiants au projet :

```
python3
from backend.credentials import Credentials; Credentials.set_credentials("identifiants.json")
```

Un message vous attirera l'attention sur le fait que ce lien est ephémère : il faudra refaire cette commande pour chaque processus Python. Des solutions permanentes sont proposées par ce message.

#### 2.2 Accéder sans identifiants

Il n'est pas possible d'accéder à l'API sans identifiants valides et nous ne vous en fournirons pas. Cependant, une réplique de l'API peut être interfacée via la classe **DummyClient** dans /backend/ade_api.py.

## Contribution au code et débuggage

### 1. Initialisation du serveur

Pour initialiser le server, utilisez la commande `redis-server` dans un terminal.
Si besoin, vous pouvez accéder à un client dans un autre terminal en entrant `redis-cli`. Référez-vous à la documentation de Redis à ce sujet.

Le client peut également être utilisé directement dans le terminal. Exemple : afin de supprimer toutes les clés contenant le mot "project" (sensible à la casse), entrez-ci `redis-cli keys "*project*" | xargs -I{lin} echo \"{lin}\" | xargs redis-cli unlink`.

Pour appliquer une expiration aléatoire, par exemple en 200 et 400 secondes, entrez `redis-cli keys *session* | xargs -n 1 -I{} python3 -c "import os;import random;os.system('redis-cli expire \"{}\" ' + str(random.randint(200, 400)))"`.

Pour vérifier que cela a bien fonctionné :
`redis-cli keys *project* | xargs -n 1 -I{} redis-cli ttl {}`

### 2. Démarrez le site-web

Entrez dans un terminal `python3 app.py`. Une url devrait vous indiquer où le site est accessible.

### 3. Documentation

Pour savoir comment documenter votre code, suivez nos indications [ici](/docs/README.md)
