# SETUP - Tout ce qu'il faut savoir afin de contribuer à ce projet

## Installation

### 1. Installez Redis
Pour installer un serveur Redis, référez-vous au site https://redis.io/topics/quickstart.

### 2. Clonez ce repo

`git clone https://github.com/SnaKyEyeS/ADE-Scheduler`

### 3. Créez un environnement virtuel Python (optionnel)

Placez-vous dans le dossier du projet
```
cd <repo>
pip3 install venv
source venv/bin/activate
```


### 4. Installez packages nécessaires

`pip3 install -r requirements.txt`

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

Pour savoir comment documenter votre code, suivez nos indications [ici](/docs/README.md)
