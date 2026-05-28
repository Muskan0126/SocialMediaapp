from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
# user model to keep user information
class User(AbstractUser):
    
    bio = models.TextField()
    gender = models.CharField(max_length=7, blank=False)
    country = models.CharField(max_length=30, blank=False)
    phone_no = models.IntegerField(blank=False)
    date_updated = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['username']

    def __str__(self):
        return f'{self.username}'