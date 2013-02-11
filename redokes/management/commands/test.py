from django.core.management.base import BaseCommand


class Command(BaseCommand):
    args = ''
    help = 'Testing'

    def handle(self, *args, **options):
        print 'just testing'
