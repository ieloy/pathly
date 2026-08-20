from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
  pass

#class GroupSaves(models.Model):
 # user = models.ForeignKey(User, on_delete=models.CASCADE)
  #name = models.CharField(max_length=32)