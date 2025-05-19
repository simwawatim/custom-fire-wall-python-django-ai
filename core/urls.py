from django.urls import path
from .views import home, login_user, logout_user, traffic, ssh_connection, start_flask_app, stop_flask_app, check_flask_app_status, recent_connections
from core import views

app_name = "core"
urlpatterns = [
    path('', home, name='home'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('traffic/', traffic, name='traffic'),
    path('authenticant-user/', views.login_user, name='login_user'),
    path('ssh-connection/', ssh_connection, name='ssh_connection'),
    path('start-flask-app/', start_flask_app, name='start_flask_app'),
    path('stop-flask-app/', stop_flask_app, name='stop_flask_app'),
    path('check-flask-app-status/', check_flask_app_status, name='check_flask_app_status'),
    path('recent-connections/', recent_connections, name='recent_connections')
]
