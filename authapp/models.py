from pathlib import Path
from time import time

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.mail import send_mail
from django.db import models
from django.utils.translation import gettext_lazy


def users_avatars_path(instance, filename):
    # file will be uploaded to
    # MEDIA_ROOT / user_<username> / avatars / <filename>
    num = int(time() * 1000)
    suff = Path(filename).suffix
    return f'user_{instance.username}/avatars/pic_{num}{suff}'


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username_validator = ASCIIUsernameValidator()

    username = models.CharField(gettext_lazy('username'), max_length=150, unique=True,
                                help_text=_(
                                    "Required. 150 characters or fewer. ASCII letters and digits only."
                                ),
                                validators=[username_validator],
                                error_messages={"unique": gettext_lazy('A user with that username already exists')})
    first_name = models.CharField(gettext_lazy('first name'), max_length=150, blank=True)
    last_name = models.CharField(gettext_lazy('last name'), max_length=150, blank=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    avatar = models.ImageField(upload_to=users_avatars_path, blank=True, null=True)
    email = models.EmailField(gettext_lazy('email address'), unique=True, max_length=256, error_messages={
        "unique": gettext_lazy('A user with that email already exists')
    })
    is_staff = models.BooleanField(gettext_lazy('staff status'), default=False,
                                   help_text=gettext_lazy('Designates whether the user can log into this admin site'))
    is_active = models.BooleanField(gettext_lazy('staff status'), default=True,
                                    help_text=gettext_lazy('Designates whether this user should be treated as active.'
                                                           'Unselect this instead of deleting accounts'))
    date_joined = models.DateTimeField(gettext_lazy('date joined'), auto_now_add=True)
    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = gettext_lazy('user')
        verbose_name_plural = gettext_lazy('users')

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)
