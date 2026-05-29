from django.contrib import admin
from useraccount.models import User
# Register your models here.

@admin.register(User)

class usercre(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone_no', 'gender','profile_photo')
    ordering = ('-date_updated',)
