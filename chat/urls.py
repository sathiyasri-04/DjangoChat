from django.urls import path
from .views import *

urlpatterns = [
    path('group/<int:group_id>/', chatGroup, name='chat-group'),
    path('send/', sendMessage, name='send-message'),
    path('group/<int:group_id>/user/<int:user_id>/', getMessagesUserGroup, name='get-messages-user-group'),
    path('group/messages/<int:group_id>/', getMessagesOfGroup, name='get-messages-of-group'),
    path('message/<int:message_id>/', getAMessage, name='get-a-message'),
]