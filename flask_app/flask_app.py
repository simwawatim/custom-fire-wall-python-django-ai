import redis
import psutil
import time
from datetime import datetime
import json
from flask import Flask, jsonify
from flask_cors import CORS
import logging
from threading import Thread

def create_flask_app():
    app = Flask(__name__)
    CORS(app)  
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Redis connection
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    try:
        r.ping()
        logging.info("Connected to Redis")
    except redis.ConnectionError:
        logging.error("Could not connect to Redis")

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

                        # If the session is new, add it to the dictionary
                        if conn_key not in ssh_sessions:
                            ssh_sessions[conn_key] = {
                                "start_time": str(datetime.now()),
                                "end_time": None,
                                "status": "Active"
                            }

            # Mark inactive sessions as closed
            for conn_key in list(ssh_sessions.keys()):
                if conn_key not in active_keys and ssh_sessions[conn_key]["status"] == "Active":
                    ssh_sessions[conn_key]["end_time"] = str(datetime.now())
                    ssh_sessions[conn_key]["status"] = "Closed"

            try:
                # Update Redis with the latest session data
                r.set('ssh_sessions', json.dumps(ssh_sessions))
                logging.info("Updated SSH session data in Redis")
            except redis.RedisError as e:
                logging.error(f"Failed to update Redis: {e}")

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

    # Start the SSH monitoring thread
    thread = Thread(target=detect_ssh_connections, daemon=True)
    thread.start()

    return app

if __name__ == "__main__":
    app = create_flask_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
