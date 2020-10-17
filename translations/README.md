# Babel

## Flask-Megatutorial about babel

<https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xiii-i18n-and-l10n>

## In short

In the `.html` files, write all the strings to be translated in this format: `{{ _
('string_to_translate') }}`.

In the `.py` files, you should import `gettext` function
```python
from flask_babel import gettext
```
and all the strings to be translated should be called by this function.
```python
x = gettext("string_to_translate")
```

Next, you need to ask Babel to get all these strings by executing these commands in
 the `<repo>` folder:
```bash
pybabel extract -F translations/babel.cfg -k _l -o translations/messages.pot .
pybabel update -i translations/messages.pot -d translations
```

Finally, you manually enter the translations in the `messages.po` files and, then
, you compile:
```bash
pybabel compile -d translations
```

## Adding a new language

You can add a new language (here `fr`) by executing this command:
```bash
pybabel init -i translations/messages.pot -d translations -l fr
```
