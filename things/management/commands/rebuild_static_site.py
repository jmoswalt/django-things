import os

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings

from things.models import StaticBuild

class Command(BaseCommand):
    """
    Runs the staticsitegen command and the collectstatic command.
    """

    def handle(self, **options):
        call_command('collectstatic', interactive=False)
        call_command('staticsitegen')
        if settings.MEDUSA_DEPLOY_DIR:
            os.system("sed -i 's|http://testserver|%s|g' %s" % (settings.SERVER_NAME, os.path.join(settings.MEDUSA_DEPLOY_DIR, 'feed', 'index.rss')))
        mark_staticbuild = StaticBuild()
        mark_staticbuild.save()
        print "DONE !!!"
