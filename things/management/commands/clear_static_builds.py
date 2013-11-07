import os
import shutil

from django.core.management.base import BaseCommand
from django.conf import settings

from things.models import StaticBuild


class Command(BaseCommand):
    """
    Clears the static build objects from the DB.
    """

    def handle(self, **options):
        sbs = StaticBuild.objects.all()
        sbs.delete()
        static_dir = settings.MEDUSA_DEPLOY_DIR
        if static_dir:
            shutil.rmtree(static_dir)
            if not os.path.exists(static_dir):
                os.makedirs(static_dir)

        print "Static builds cleared"
