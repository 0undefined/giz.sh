from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from users.models import Invitation

User = get_user_model()

class Command(BaseCommand):
    help = "Create user invites and prints to stdout"

    def add_arguments(self, parser):
        parser.add_argument("-n", "--num", type=int)

    def handle(self, *args, **options):
        try:
            superuser = User.objects.filter(is_superuser=True).first()
        except:
            raise CommandError("You need to create a superuser first!")

        num = 1
        if options['num']:
            num = options['num']

        if num < 1:
            raise CommandError("You need give a positive integer!")

        self.stdout.write("Creating %d keys" % (num))

        for _ in range(num):
            i = Invitation(referer=superuser)
            i.save()

            self.stdout.write(str(i.key))
