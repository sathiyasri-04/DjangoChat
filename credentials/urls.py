from rest_framework.urls import path
from .views import *

urlpatterns = [
    path('register/', register_view),
    path('register/page/', register_page),
    path('login/', login_view),
    path('login/page/', login_page),
    path('group-directions/page/', group_directions_page),
    path('current/', get_current_user),
    path('logout/', LogoutView.as_view()),
]