from django.apps import AppConfig

from django.conf import settings

from basex_session import Session

class BasexConfig(AppConfig):
    name = 'basex'
    verbose_name = 'Basex'

    def __init__(self, *args, **kwargs):
        super(BasexConfig, self).__init__(*args, **kwargs)

        self._basex = None

    def ready(self):
        bxconfig = settings.BASEX_CONFIG

        bxhost = bxconfig['HOST']
        bxport = bxconfig['PORT']
        bxuser = bxconfig['USER']
        bxpw = bxconfig['PASSWORD']

        self._basex = lambda: Session(bxhost, bxport, bxuser, bxpw)

    @property
    def basex(self):
        return self._basex()
