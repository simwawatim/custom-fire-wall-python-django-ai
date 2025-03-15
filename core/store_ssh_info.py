import requests
from celery import shared_task
from core.models import SSHConnection

@shared_task
def fetch_ssh_sessions():
    try:
        response = requests.get("http://localhost:5000/api/ssh_sessions")
        response.raise_for_status()  
        ssh_sessions = response.json()

        for key, session in ssh_sessions.items():
            source, destination = key.split(' -> ')
            start_time = session.get("start_time", "Unknown")
            end_time = session.get("end_time", "Active") 
            """
            
            print(f"Source: {source}, Destination: {destination}")
            print(f"Start Time: {start_time}, End Time: {end_time}")
            print("-" * 50)

            """

            SSHConnection.objects.create(
                source=source,
                destination=destination,
                start_time=start_time,
                end_time=end_time
            )

    except requests.RequestException as e:
        print(f"Error fetching SSH sessions: {e}")
