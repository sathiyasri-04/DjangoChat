from django.urls import re_path
from .consumers import *

websocket_urlpatterns = [
    re_path(r'ws/chat/group/(?P<group_name>\w+)/$', ChatGroupConsumer.as_asgi()),   
]