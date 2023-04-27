from django.core.validators import RegexValidator
from django.conf import settings
from django.db import models
from users.models import User


class Repository(models.Model):
    class Visibility(models.IntegerChoices):
        PUBLIC = 0
        PRIVATE = 1

    name = models.CharField(
            max_length=128,
            null=False,
            validators=[RegexValidator(
                r'^[a-zA-Z0-9_\-]{6,}$',
                "Repository name must consist only of latin letters, numbers, underscores and dashes."
            )])

    owner = models.ForeignKey(User, null=False, on_delete=models.CASCADE)

    vilibility = models.IntegerField(choices=Visibility.choices, default=Visibility.PRIVATE)

    # TODO: override save() to commit repository to gitolite beforehand


    def get_absolute_url(self):
        return '/' + self.__str__()

    def get_remote_url(self):
        return 'git@' + settings.GITOLITE_HOST + ':' + self.__str__() + '.git'

    def __str__(self):
        return self.owner.username + '/' + self.name

class Collaborator(models.Model):
    class Permissions(models.TextChoices):
        NO_PERM = 0, '-'
        READ = 1, 'R'
        WRITE = 2, 'RW'
        READWRITEPLUS = 3, 'RW+'

    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    repo = models.ForeignKey(Repository, null=False, on_delete=models.CASCADE)
    perm = models.CharField(max_length=7,
                            choices=Permissions.choices,
                            default=Permissions.NO_PERM)

    # TODO: override save() to commit permissions to repository in gitolite beforehand


# TODO:
# * issues
# * pull requests
