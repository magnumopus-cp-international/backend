# Summery creator


## Basic Commands

### Runserver

    $ ./manage.py runserver_plus

### Type checks

Running type checks with mypy:

    $ mypy summery_creator

#### Running tests with pytest

    $ pytest

### Setting Up Your Users

-   To create a **superuser account**, use this command:

        $ python manage.py createsuperuser

### Celery

This app comes with Celery.

To run a celery worker:

``` bash
cd summery_creator
celery -A config.celery_app worker -l info
```

Please note: For Celery's import magic to work, it is important *where* the celery commands are run. If you are in the same folder with *manage.py*, you should be right.


made with [cookiecutter-django](https://github.com/Alexander-D-Karpov/cookiecutter-django)
