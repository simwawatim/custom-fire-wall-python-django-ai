import redis
import psutil
import time
from datetime import datetime
import json
from flask import Flask, jsonify

app = Flask(__name__)

# Redis connection
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
try:
    r.ping()
    print("Connected to Redis")
except redis.ConnectionError:
    print("Could not connect to Redis")

ssh_sessions = {}

def detect_ssh_connections():
    """Continuously monitors SSH connections and updates session details in Redis."""
    while True:
        ssh_connections = []
        active_keys = set()

        for conn in psutil.net_connections(kind="inet"):
            if conn.laddr and conn.raddr:
                if conn.laddr.port == 22 or conn.raddr.port == 22:
                    conn_key = f"{conn.laddr.ip}:{conn.laddr.port} -> {conn.raddr.ip}:{conn.raddr.port}"
                    ssh_connections.append(conn)
                    active_keys.add(conn_key) 

                    if conn_key not in ssh_sessions:
                        ssh_sessions[conn_key] = {
                            "start_time": str(datetime.now()),
                            "end_time": None,
                            "status": "Active"
                        }

        for conn_key in list(ssh_sessions.keys()):
            if conn_key not in active_keys and ssh_sessions[conn_key]["status"] == "Active":
                ssh_sessions[conn_key]["end_time"] = str(datetime.now())
                ssh_sessions[conn_key]["status"] = "Closed"

        r.set('ssh_sessions', json.dumps(ssh_sessions))
        print("Updated SSH session data in Redis")

        time.sleep(5)

@app.route('/api/ssh_sessions', methods=['GET'])
def get_ssh_sessions():
    """Expose SSH session data via API."""
    try:
        data = r.get('ssh_sessions')
        if data:
            return jsonify(json.loads(data))
        return jsonify({"message": "No SSH sessions found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    from threading import Thread


    thread = Thread(target=detect_ssh_connections, daemon=True)
    thread.start()

    # Start Flask API
    app.run(host="0.0.0.0", port=5000, debug=True)
