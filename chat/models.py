from django.db import models
from groups.models import Group
from django.conf import settings
from credentials.models import UserRole

class Message(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="messages")  
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="sender_of_message") 
    text = models.TextField()  
    created_at = models.DateTimeField(auto_now_add=True)  
    deleted_at = models.DateTimeField(null=True, blank=True)
    # later add 'name' of sender if required
