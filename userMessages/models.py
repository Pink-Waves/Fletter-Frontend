from django.db import models
from accounts.models import ExtendedUser

class Message(models.Model):
    sender = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE, related_name='sender')
    recipient = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE, related_name='recipient')
    time = models.DateTimeField()
    subject = models.CharField(max_length=35)
    body = models.TextField()
    favorite = models.BooleanField(default=False)
    status = models.CharField(max_length=50)
