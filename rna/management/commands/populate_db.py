from django.core.management.base import BaseCommand
from rna.models import SystemRequirement
from datetime import datetime


class Command(BaseCommand):
    help = "Adds the blank field to the System Requirements table"

    def _create_blank_requirement(self):
        if SystemRequirement.objects.filter(code_name = 'Blank').exist() == False:
            print "Entering here"
            blank_req = SystemRequirement(code_name = 'Blank', content='', creation_date=datetime.now())
            blank_req.save()

    def handle(self, *args, **options):
        self._create_blank_requirement()