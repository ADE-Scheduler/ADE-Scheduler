# Migrate the database

Base on the Flask Mega-Tutorial:
https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database.

## Generate the migration script

Multiple versions of the database are stored in the folder.
When a change occurs on any of the database models (see `backend/models.py`), you
must execute this command in order to create the migration script:

```
flask db migrate -m "version description"
```

## Upgrade/Downgrade workflow

Next, to apply changes, execute this command:

```
flask db upgrade
```

There also exists the `flask db downgrade` to revert last migration if needed.

> **NOTE:** the `FLASK_APP` environment variable must be defined in order for it to work.
