from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.post.models import Story


class Command(BaseCommand):

    help = "Deletes expired stories and their images."

    def handle(self, *args, **kwargs):

        now = timezone.now()
    
        stories = Story.objects.filter(expires_at__lte=now)

        count = stories.count()

        for story in stories:

            if story.image:
                story.image.delete(save=False)

            story.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"{count} expired stor{'y' if count == 1 else 'ies'} deleted successfully."
            )
        )