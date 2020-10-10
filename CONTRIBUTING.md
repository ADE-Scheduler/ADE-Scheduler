# Contributing

Any contributions are welcome. If you would like to fix a bug or add a feature, you can do it ! However, it is important to follow a set of rules so that everything can go smoothly.

If you have an idea or a bug, please report it first in the [Issues](https://github.com/SnaKyEyeS/ADE-Scheduler/issues) tab of the repository so we can discuss it and decide of the best strategy to bring your idea to life. Directly issuing a pull request is generally a bad idea: you might end up coding something that has already been done or is being done.

## Reading the documentation

An updated version of the documentation is hosted
[here](https://ade-scheduler.readthedocs.io/en/latest/). This contains
 details about of each function should work and how to use them properly.

## Running ADE Scheduler on your computer

### Getting the code

First, you need to fork the repository. Then, we recommend you to follow the [setup](/SETUP.md) guide so that you can properly install all the dependencies and required tools to run your own development environment.

Once that's done, we invite you to create a local branch on which you will write your code:
```bash
git branch -b your-branch-name
```
When your code is written, tested and formatted, you can submit a pull request through the GitHub website !

### Testing

Before issuing a pull request, it is imperative that you run the tests. If your code does not passes the test, it will not be integrated ! Moreover, you need to write tests for any new features you might have added to ensure a smooth continuous integration. To run the test, you just need to run the `pytest` command in the main folder.

### Code format

To maintain a minimal standard, we decided to adopt the [black code formatter](https://github.com/psf/black) accross all python files.\
To make sure your code complies with our standards, you need to run the following:
```bash
pre-commit install
pre-commit run --all-files
```
Note that this will setup a hook which will automatically run a formatter before your commits.
