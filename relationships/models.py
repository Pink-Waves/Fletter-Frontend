from django.db import models
from accounts.models import ExtendedUser

class Relationship(models.Model):
    requester = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE, related_name='requester')
    addressee = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE, related_name='addressee')
    created_time = models.DateTimeField()
    status = models.CharField(max_length=50)
