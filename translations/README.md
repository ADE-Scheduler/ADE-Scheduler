# Babel

## Flask-Megatutorial about babel:
https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xiii-i18n-and-l10n

## En résumé
Mettre tous les string dans les `.html` à traduire entre moustaches comme suit:  `{{ _('string_to_translate') }}`

Ensuite, il faut dire à Babel d'aller chercher tous ces strings à traduire en exécutant la commande suivante dans le dossier `<repo>` (en ayant installé au préalable la commande pybabel `sudo apt-get install python-babel`):
```
pybabel extract -F translations/babel.cfg -k _l -o translations/messages.pot .
pybabel update -i translations/messages.pot -d translations
```

Ensuite, on entre manuellement les traductions dans les fichiers `messages.po`. Une fois que c'est fait, compiler:
```
pybabel compile -d translations
```

## Ajouter une nouvelle langue:
Il est possible d'ajouter une nouvelle langue à l'aide de la commande suivante:
```
pybabel init -i translations/messages.pot -d translations -l fr
```
