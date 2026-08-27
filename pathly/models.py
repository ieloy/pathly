from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
  pass

class Groupsaves(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  groups = models.JSONField()
  places = models.JSONField(default=dict)
  created_at = models.DateTimeField(auto_now_add=True)