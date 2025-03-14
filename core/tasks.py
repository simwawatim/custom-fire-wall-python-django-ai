from celery import shared_task
import redis
import json

@shared_task
def fetch_ssh_sessions():
    """Fetches the latest SSH sessions from Redis."""
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    ssh_sessions_json = r.get('ssh_sessions')
    
    if ssh_sessions_json:
        ssh_sessions = json.loads(ssh_sessions_json)

        return ssh_sessions
    return None
