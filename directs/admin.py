from django.contrib import admin
from directs.models import Message
# Register your models here.

@admin.register(Message)

class mess(admin.ModelAdmin):
    readonly_fields = ( 'receiver_id', 'sender_id')
    list_display = ('text', 'receiver_id','sender_id','is_read')