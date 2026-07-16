from django.contrib import admin

from apps.useraccount.models import Subscription, User

# Register your models here.
admin.site.register(Subscription)


@admin.register(User)
class usercre(admin.ModelAdmin):
    list_display = ("username", "email", "phone_no", "gender", "profile_photo")
    ordering = ("-date_updated",)
