# Documentation

In order to easily document our code, we use Sphinx. The master branch documentation is
 automatically compiled and hosted on [Read The Docs](https://ade-scheduler.readthedocs.io/en/latest/).

## Building the docs

If you make any change in the documentation, then run these commands:

```bash
cd docs
sphinx-apidoc -o source/backend ../backend -f
sphinx-apidoc -o source/views ../views -f
make html
```
Then refer to your local documentation build located [here](/docs/build/html/index.html).

## Coding style

The coding style we follow is described in the [CONTRIBUTING GUIDE](CONTRIBUTING.md).

## Readings

More informations about how to use Sphinx can be found here:
- https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html
- https://thomas-cokelaer.info/tutorials/sphinx/docstring_python.html
- https://thomas-cokelaer.info/tutorials/sphinx/rest_syntax.html
