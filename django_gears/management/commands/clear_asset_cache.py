from django.core.management.base import NoArgsCommand
from django_gears.settings import environment


class Command(NoArgsCommand):

    help = 'Clears assets cache.'

    def handle_noargs(self, **options):
        environment.cache.clear()
