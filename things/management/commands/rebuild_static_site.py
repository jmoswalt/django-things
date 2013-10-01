from django.core.management.base import BaseCommand
from django.core.management import call_command

from things.models import StaticBuild

class Command(BaseCommand):
    """
    Runs the staticsitegen command and the collectstatic command.
    """

    def handle(self, **options):
        call_command('collectstatic', interactive=False)
        call_command('staticsitegen')
        mark_staticbuild = StaticBuild()
        mark_staticbuild.save()
        print "DONE !!!"
