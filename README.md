# Getting started

## Install dependencies
Open up your command terminal and run the following to set up

```bash
pip install -r requirements.txt
```

## Set up Flask
Please change the app config file path to fit wherever you've downloaded the repo to
```bash
export FLASK_APP=postmates
export FLASK_ENV=development
export APP_CONFIG_FILE=<Change this to your path please>/postmates/config/development.py
```

Create instance directory to store secret values. 
In the your file you should store your API keys, customer_id and secret key as:
```
postmates_api_key=<enter your api key here>
customer_id=<enter your customer id here>
SECRET_KEY=<enter your secret key, can be a random string>
```

``` bash
mkdir instance
touch config.py
```

## Set up DB
Make sure Postgres is running. [Postgres.app](https://postgresapp.com) is simple one for Mac.

App uses Flask Migrate to manage DB migrations.
Edit [dev configuration](./config/development.py) so that the DB configuration is for your local Postgres.

```bash
dropdb postmates
createdb postmates
flask db init
flask db migrate
flask db upgrade
```

## Run app
```bash
python run.py
```

## Open webpage
Go to your browser of choice and key in `127.0.0.1:5000`
This will open up the web-app.

Have fun and happy deliveries!