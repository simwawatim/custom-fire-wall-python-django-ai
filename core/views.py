from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from core.models import SSHConnection
from django.http import JsonResponse
from django.contrib import messages
import subprocess
import signal
import os


flask_process = None

@login_required(login_url='/login/')
def home(request):
    """Render the home page."""

    return render(request, 'core/home.html')


def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)  
        if user is not None:
            auth_login(request, user)
            return redirect('core:home')
        else:
            messages.warning(request, 'Invalid email or password credentials')
            return redirect('core:login_user')

    return render(request, 'core/login.html')


def logout_user(request):
    """Handle user logout (to be implemented)."""
    pass

def traffic(request):
    """Render the traffic monitoring page."""
    return render(request, 'core/traffic.html')

def ssh_connection(request):
    """Render the SSH connections page."""
    return render(request, 'core/ssh_connections.html')

def start_flask_app(request):
    """Starts the Flask application as a subprocess."""
    global flask_process

    if flask_process and flask_process.poll() is None:
        return JsonResponse({"message": "Flask app is already running.", "is_running": True}, status=400)

    try:
        flask_process = subprocess.Popen(
            ["python", "flask_app/flask_app.py"],
            stdout=subprocess.DEVNULL,  # Suppress output
            stderr=subprocess.DEVNULL
        )
        return JsonResponse({"message": "Flask app started successfully.", "is_running": True})

    except Exception as e:
        return JsonResponse({"message": f"Failed to start Flask app: {e}", "is_running": False}, status=500)

def stop_flask_app(request):
    """Stops the Flask application."""
    global flask_process

    if flask_process and flask_process.poll() is None:
        try:
            flask_process.terminate()  # Gracefully stop the process
            flask_process.wait()  # Ensure the process fully exits
            flask_process = None
            return JsonResponse({"message": "Flask app stopped successfully.", "is_running": False})
        except Exception as e:
            return JsonResponse({"message": f"Failed to stop Flask app: {e}", "is_running": True}, status=500)
    else:
        return JsonResponse({"message": "Flask app is not running.", "is_running": False}, status=400)

def check_flask_app_status(request):
    """Checks if the Flask app is running."""
    global flask_process

    if flask_process and flask_process.poll() is None:
        return JsonResponse({"message": "Flask app is running.", "is_running": True})
    else:
        return JsonResponse({"message": "Flask app is not running.", "is_running": False})
    

def recent_connections(request):
    connections = SSHConnection.objects.all()
    context = {
        'connections':connections
    }
    return render(request, 'core/recent_connection.html', context)
    



