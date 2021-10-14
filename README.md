# OpenChat Server

**API server for OpenChat with Django.**

# Installation

```bash
git clone https://github.com/nohackjustnoobb/OpenChat-Server.git
```

```bash
cd OpenChat-Server && pip3 install -r requirements.txt
```

```bash
python3 manage.py makemigrations
```

```bash
python3 manage.py migrate
```

# Set Up Settings

Go to settings in '/openchat/settings'.

Replace this with your informations.

```bash
# database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': {Database Name},
        'USER': {Username},
        'PASSWORD': {Password},
        'HOST': {Database IP},
        'PORT': {Database Port},
    }
}

# email
EMAIL_HOST = {SMTP Server}
EMAIL_PORT = {Server Port}
EMAIL_USE_TLS = True
EMAIL_HOST_USER = {Email}
EMAIL_HOST_PASSWORD =  {Password}
```

You can use another DBMS.

You can find more infomations in Django website.

Link: https://docs.djangoproject.com/en/3.2/ref/databases/

# Start Server

```bash
python3 manage.py runserver
```
