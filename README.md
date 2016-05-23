Tweet scraper using django to store tweets, twitter users, and locations.

##### General thoughts
This project is made up of two parts:

* A Django server
* A tweet scraper

The Django server is responsible for the database composed of:

* Tweets
* TwitterUsers
* Locations
* Images

The scraper is primarily responsible for watching the Twitter stream and tracking hashtags.
Each location is associated with a hashtag. When a new location is added to the database, the scraper will restart itself, adding the new hashtags to its list of tracked items.

##### Getting started
First of all, clone the repo:

    git clone git@github.com:jeremylow/cyberpunkd.collector.git

    tree
    .
    ├── cyberpunkd
    │   ├── bin
    │   │   └── start_server.sh
    │   ├── collector
    │   │   ├── admin.py
    │   │   ├── apps.py
    │   │   ├── env.py
    │   │   ├── __init__.py
    │   │   ├── migrations
    │   │   │   └── [...]
    │   │   ├── models.py
    │   │   ├── scraper.pid
    │   │   ├── scraper.py
    │   │   ├── signals.py
    │   │   ├── tests.py
    │   │   └── views.py
    │   ├── conf
    │   │   ├── cyberpunkd.nginx.conf
    │   │   └── cyberpunkd.supervisord.conf
    │   ├── cyberpunkd
    │   │   ├── __init__.py
    │   │   ├── settings.py
    │   │   ├── urls.py
    │   │   └── wsgi.py
    │   ├── db.sqlite3
    │   ├── docker.postgres.sh
    │   ├── manage.py
    │   └── media
    ├── LICENSE
    ├── README
    ├── requirements.txt
    ├── setup.cfg
    └── VERSION

Set up a python virtual environment using your tool of choice (I'm using [pyenv](https://github.com/yyuu/pyenv) and [pyenv-virtualenv](https://github.com/yyuu/pyenv-virtualenv)). Anyway, once you've got that squared away, install the dependencies:

    cd cyberpunkd.collector
    pip install -r requirements.txt

If you're just running this locally and don't want to deal with postgres:

    vim cyberpunkd/cyberpunkd/settings.py

& uncomment:

    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # }

& comment out:

    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'cyberpunkdDB',
        'USER': 'defaultuser',
        'PASSWORD': 'defaultuserpassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }

Once that's done, create a superuser with:

    python cyberpunkd/manage.py migrate
    python cyberpunkd/manage.py createsuperuser

Follow the prompts. Then run the server with:

    python cyberpunkd/manage.py runserver

Go to [127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) and login with the user that you just created.

Add a Location by clicking on "Location" under "Collector". Click "Add Location", fill out at least the `loc_name` & `hashtag` fields. Save it.

The scraper depends on you having credentials to access Twitter's API. Put those in a file called `cyberpunkd/collector/env.py`:

    CONSUMER_KEY = 'www'
    CONSUMER_SECRET = 'xxx'
    ACCESS_TOKEN= 'yyy'
    ACCESS_SECRET = 'zzz'
    SLACK_URL='http://example.com'

Leave the slack URL as is. It's just so I can see errors on my phone.

Open up a new terminal and start the scraper with:

    python cyberpunkd/collector/scraper.py

If all went well, you should see something like the following printed to the console:

    Started scraping, PID:  4811
    Watching hashtags: #artprize, #selfie

When a tweet is tagged with a Location's hashtag, it'll save the photo, the tweet, the twitter user, and attach those to a Location. The image is stored in `media/` if you want to check it out.
