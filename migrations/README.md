# Migration de base de données
Basé sur le Flask Mega-Tutorial: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database

## Générer le script de migration

Les différentes versions de la base de données sont stockées dans ce dossier.
Quand un changement est effectué sur les modèles de la base de données (tels qu'ils sont définis dans le fichier backend/models.py),
il faut exécter cette commande pour créer un script de migration:
```
cd <repo>
flask db migrate -m "version description"
```

## Upgrade/Downgrade workflow

Ensuite, pour appliquer les changements, exécuter la commande suivante:
```
cd <repo>
flask db upgrade
```

Il existe aussi la commande `flask db downgrade` pour défaire la dernière migration si nécessaire.
