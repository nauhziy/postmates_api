# Getting started

## Install dependencies
Open up your command terminal and run the following to set up

```bash
pip install -r requirements.txt
```

## Set up Flask
Create instance directory to store secret values. 
In the your file you should store your API keys, customer_id and secret key as:
``` bash
mkdir instance
touch config.py
```

Save within config.py
```
postmates_api_key=<enter your api key here>
customer_id=<enter your customer id here>
SECRET_KEY=<enter your secret key, can be a random string>
```

Please change the app config file path to fit wherever you've downloaded the repo to
```bash
export FLASK_APP=postmates
export FLASK_ENV=development
export APP_CONFIG_FILE=<Add local path here>/postmates_api/config/development.py
```

## Set up DB
Set up postgres and run it. [Postgres.app](https://postgresapp.com)
Edit /config/development.py to match your local configuration.

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

# Credits to @far33d and @jennyslu for much of the framework inspiration