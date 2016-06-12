from django.apps import apps

from contextlib import contextmanager


def session():
    return apps.get_app_config('basex').basex


@contextmanager
def recipe_db():
    s = session()
    s.execute('open recipe')
    yield s
    s.close()
