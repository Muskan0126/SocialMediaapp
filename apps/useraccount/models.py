from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import timedelta
from django.utils import timezone
import os
import uuid
# Create your models here.

class User(AbstractUser):
    def profile_upload_path(instance, filename):
        ext = os.path.splitext(filename)[1]
        return f"https://instagram-clone-muskan.s3.ap-southeast-2.amazonaws.com/profile/{instance.id}/{uuid.uuid4()}{ext}"
    
    bio = models.TextField()
    email = models.EmailField( blank=False, null=False, unique=True)
    gender = models.CharField(max_length=7, blank=True, null=True)
    country = models.CharField(max_length=30, blank=True, null = True)
    phone_no = models.CharField(blank=True,null = True)
    date_updated = models.DateTimeField(auto_now=True)
    profile_photo = models.ImageField(upload_to=profile_upload_path, null=True,blank=True, default = 'null')

    class Meta:
        ordering = ['username']

    def __str__(self):
        return f'{self.username}'
    
class otp(models.Model):
    email = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        lifespan = timedelta(minutes=5)
        return timezone.now() > (self.created_at + lifespan)

    def __str__(self):
        return f"OTP for {self.email}"
