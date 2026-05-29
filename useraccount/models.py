from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
# user model to keep user information
class User(AbstractUser):
    def user_directory_path(instance, filename):
        return 'userprofile_{0}/{1}'.format(instance.id, filename)
    
    bio = models.TextField()
    
    gender = models.CharField(max_length=7, blank=True, null=True)
    country = models.CharField(max_length=30, blank=True, null = True)
    phone_no = models.CharField(blank=True,null = True)
    date_updated = models.DateTimeField(auto_now=True)
    profile_photo = models.ImageField(upload_to=user_directory_path, null=True,blank=True, default = 'null')

    class Meta:
        ordering = ['username']

    def __str__(self):
        return f'{self.username}'