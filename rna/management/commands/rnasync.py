from optparse import make_option

from django.core.mail import mail_admins
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

from requests.exceptions import RequestException

from ... import clients


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--force',
            action='store_true',
            dest='force',
            default=False,
            help='Force complete sync, ignoring modified timestamps'),
        )

    def model_params(self, models, force=False):
        if force:
            return {}
        params = dict((m, {}) for m in models)
        for m in models:
            try:
                latest = m.objects.latest('modified')
            except ObjectDoesNotExist:
                pass
            else:
                params[m]['modified_after'] = latest.modified.isoformat()
        return params

    def handle(self, *args, **options):
        rc = clients.RNAModelClient()
        model_params = self.model_params(rc.model_map.values(),
                                         force=options['force'])
        try:
            for url_name, model_class in rc.model_map.items():
                params = model_params.get(model_class)
                rc.model_client(url_name).model(save=True, params=params)
        except RequestException as e:
            subject = 'Problem connecting to Nucleus'
            mail_admins(subject, str(e))
            raise CommandError('%s: %s' % (subject, e))
