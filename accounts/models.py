from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from simple_email_confirmation.models import SimpleEmailConfirmationUserMixin

class ExtendedUser(SimpleEmailConfirmationUserMixin, AbstractUser):
    nickname = models.CharField(max_length=30)
    number = models.CharField(max_length=4)
    address = models.TextField()
    state = models.CharField(max_length=30)
    bird_color = models.CharField(max_length=30)
