# Tender test task

## Prerequisites

### Installing

Follow next steps:

```shell
git clone https://github.com/DmytroBondariev/tender_django.git
```
```shell
cd tender_django
```
```shell
python3 -m venv venv
```
```shell
source venv/bin/activate
```
```shell
pip install -r requirements.txt
```
```shell
manage.py makemigrations
```
```shell
manage.py migrate
```

Login credentials(available after migration):
```
username: demo
password: demo
```

## Environment Variables

The project uses environment variables for configuration. Create a `.env` file in the project directory and define the following variables:

You can use the `.env.sample` file provided as a template:

1. Rename the `.env.sample` file to `.env`.
2. Fill `DJANGO_SECRET_KEY` with your actual Django secret key (https://djecrety.ir/)

```shell
python manage.py runserver
```

## Running the tests
```Shell
python manage.py test
```
