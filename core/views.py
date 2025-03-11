from django.shortcuts import render

"""
Get the home page, this is the entry page of the web app

if the user has no active session the will be redirected 

to login/
"""
def home(request):
    return render(request, 'core/home.html')


def login_user(request):
    return render(request, 'core/login.html')


def logout_user(request):
    pass

def traffic(request):
    return render(request, 'core/traffic.html')

def ssh_connection(request):
    return render(request, 'core/ssh_connections.html')