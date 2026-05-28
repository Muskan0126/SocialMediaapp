from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.

User = get_user_model()

class Message(models.Model):
    id = models.CharField(max_length=25, primary_key=True, unique=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='from_user')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='to_user')
    text = models.TextField(null=True, blank=False)
    is_read = models.BooleanField(default=False)
    date_sent = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

    
    class Meta:
        ordering = ['date_sent']
    

    def send_message(from_user, to_user, msg):
        # sender's message
        sender_message = Message.objects.create(
            sender=from_user,
            receiver=to_user,
            text=msg,
            is_read=True,
        )
        sender_message.save()

        return sender_message
    

    def get_inbox_messages(user):
        # logged in user inbox
        users_lists = []
        msgs = Message.objects.filter(models.Q(sender=user) | models.Q(receiver=user)).values('receiver').annotate(last_msg=models.Max('date_sent')).order_by('-last_msg')

        for message in msgs:
            users_lists.append({
                'user': User.objects.get(pk=message["receiver"]),
                'last': message["last_msg"],
                "unread": Message.objects.filter(sender=user, receiver__pk=message["receiver"], is_read=False).count(),
                'last_message': [last_text.text for last_text in Message.objects.filter(receiver__pk=message["receiver"]).order_by('-date_sent')][0]  
            })
        
        return users_lists