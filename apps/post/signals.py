import uuid
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Follow, Notification


@receiver(post_save, sender=Follow)
def notify_on_follow(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            id=str(uuid.uuid4())[:25],
            sender=instance.follower,
            receiver=instance.following,
            notification_type=3,
            notification_text=f"{instance.follower.username} started following you.",
        )


@receiver(post_delete, sender=Follow)
def remove_follow_notification(sender, instance, **kwargs):
    Notification.objects.filter(
        sender=instance.follower,
        receiver=instance.following,
        notification_type=3,
    ).delete()
