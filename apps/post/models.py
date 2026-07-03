from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.

User = get_user_model()
def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)


class Post(models.Model):
    picture = models.ImageField(upload_to=user_directory_path)
    caption = models.CharField(max_length=10000)
    posted = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-posted']

    def __str__(self):
        return f"{self.user.username} - {self.id}"

class Likes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_likes")

    def user_liked_post(sender, instance, *args, **kwargs):
        like = instance
        post = like.post
        sender = like.user
        

    def user_unliked_post(sender, instance, *args, **kwargs):
        like = instance
        post = like.post
        sender = like.user
        
class Comment(models.Model):
    id = models.CharField(max_length=25, primary_key=True, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    comment = models.TextField(blank=False)
    total_likes = models.ManyToManyField(User, related_name='total_likes', blank=True)
    liked_by_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='liked_comment')
    is_liked = models.BooleanField(default=False)
    date_commented = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.item}"


class Notification(models.Model):
    NOTIFICATION_TYPE = (
        (1, 'Like'),
        (2, 'Comment'),
        (3, 'Follow'),
    )

    id = models.CharField(max_length=25, primary_key=True, unique=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    notification_type = models.IntegerField(choices=NOTIFICATION_TYPE)
    notification_text = models.CharField(max_length=50)     
    is_read = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)
    

    class Meta:
        ordering = ['-date_created']


    def __str__(self):
        return f'{self.notification_type}'


    

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')

    def user_follow(sender, instance, *args, **kwargs):
        follow = instance
        sender = follow.follower
        following = follow.following
        notify = Notification(sender=sender, user=following, notification_types=3)
        notify.save()

    def user_unfollow(sender, instance, *args, **kwargs):
        follow = instance
        sender = follow.follower
        following = follow.following
        notify = Notification.objects.filter(sender=sender, user=following, notification_types=3)
        notify.delete()

    unique_together = (
        "follower",
        "following"
    )
class Stream(models.Model):
    following = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='stream_following')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    date = models.DateTimeField()

    def add_post(sender, instance, *args, **kwargs):
        post = instance
        user = post.user
        followers = Follow.objects.all().filter(following=user)

        for follower in followers:
            stream = Stream(post=post, user=follower.follower, date=post.posted, following=user)
            stream.save()


class Story(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="stories"
    )

    image = models.ImageField(
        upload_to="stories/"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    expires_at = models.DateTimeField()

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):

        if not self.expires_at:

            self.expires_at = (
                timezone.now()
                + timedelta(hours=24)
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} Story"