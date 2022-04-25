from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class Presence(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # èoê»éûä‘
    presence_time = models.DateTimeField(default=datetime.now)
    
    leave_time = models.DateTimeField(null=True)
