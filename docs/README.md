# Documentation

Afin de faciliter la documentation de nos fonctions, nous utilisons Sphinx. La page contenant la documentation est /docs/build/html/index.html. Pour mettre à jour :
```
cd docs
sphinx-apidoc -o source/backend ../backend -f
sphinx-apidoc -o source/views ../views -f
make html
```
Nous utilisons également le package built-in `typing` qui permet de définir le type des objets. Ceci n'a aucun impact sur le code car cela est juste une indication mais certains IDE comme PyCharm utilisent ces informations pour aider au débuggage.

Pour savoir comment documenter votre code de la même manière que nous :
- https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html
- https://thomas-cokelaer.info/tutorials/sphinx/docstring_python.html
