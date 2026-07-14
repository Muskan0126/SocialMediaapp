from django.contrib import admin
from apps.post.models import Post, Likes,Comment,Notification,Follow, Stream
# Register your models here.

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Likes)
admin.site.register(Notification)
admin.site.register(Follow)
admin.site.register(Stream)

