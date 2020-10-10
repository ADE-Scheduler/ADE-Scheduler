# SETUP - Everything you need to run this project

## Storage

##### Redis
Redis is used as a cache memory and acts as a buffer between the ADE API and ADE-Scheduler, to enhance the performance and try to reduce lag.  \
To install a Redis server, please refer to [the official website](https://redis.io/topics/quickstart).

Various utilities about Redis are integrated in the Flask CLI. To know more, type `flask redis --help`.

##### SQL Database
ADE Scheduler uses a SQL database to store any relevant data and uses SQLAlchemy as an ORM, so you can basically plug in any SQL database you may want.  \
However, every SQL database has its own specific functionalities, so minor modifications may be required to accommodate another type. Up until now, any of those three databases has been tested and should therefore work: SQLite (recommended for development), MySQL and PostgreSQL (recommended for production).

Various utilities about database migrations & data transfers can be found in the Flask CLI. To know more about it, type: `flask db --help` or `flask sql --help`.

## Python
We recommend to use a virtual environment to manage the various required python packages:
```
cd <repo>
sudo apt install python3-virtualenv
virtualenv env_name
source env_name/bin/activate
pip3 install -r requirements.txt
```
and you are all set !

## NodeJS
First, make sure you have installed node.js and npm. If that's not the case, please refer to the [official website](https://nodejs.org/en/).  \
Then, install the required packages by running:
```
cd <repo>
npm install
```
Any javascript or HTML asset needs to be bundled by webpack before being used. To do so, run the `npx webpack` command.  \
Moreover, you can activate the file watcher for hot-reloading and map source files for easy debugging by running the complete `npx webpack --watch --devtool inline-source-map`.

If an error appears about the maximum amount of allowed watchers, you can fix this by running `echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf && sudo sysctl -p`, as  described [here](https://stackoverflow.com/questions/53930305/nodemon-error-system-limit-for-number-of-file-watchers-reached).

## Configuration

In order to be able to run the website, you first need to specify several configuration variables. Create a `<repo>/.flaskenv` file and specify the following environment variables:

##### For development:
```
FLASK_APP = path/to/<repo>/app.py
FLASK_ENV = development
FLASK_RUN_HOST = localhost
FLASK_RUN_PORT = 5000
TEMPLATES_AUTO_RELOAD = True

ADE_DB_PATH = <database URI>
FLASK_SECRET_KEY = super_secret_key
FLASK_SALT = super_complex_salt

MAIL_USERNAME = an-email@address
MAIL_PASSWORD = password
```

##### For production:
```
FLASK_APP = path/to/<repo>/app.py
FLASK_ENV = production

ADE_DB_PATH = <database URI>
FLASK_SECRET_KEY = super_secret_key
FLASK_SALT = super_complex_salt

MAIL_USERNAME = an-email@address
MAIL_PASSWORD = password
```

##### Access to the ADE API (optional)
--TODO: explain the procedure to follow to have access to the Dummy Client !


## Flask CLI
The website can be started simply by running `flask run`. Moreover, there are various useful commands such as `flask shell`. To discover them all, type `flask --help`.

## Production

-- TODO: document production deployment procedure here

## Documentation

To know how to document your code, follow the instructions [here](/docs/README.md)
