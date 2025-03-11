from django.urls import path
from .views import (
    home,
    traffic,
    ssh_connection,
)

app_name = "core"
urlpatterns = [
    path('', home, name='home'),

    path('traffic/', traffic, name='traffic'),
    path('ssh-connection/', ssh_connection, name='ssh_connection')
]
