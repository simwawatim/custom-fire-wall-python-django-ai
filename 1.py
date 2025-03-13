import psutil
import time
import subprocess
import curses
from datetime import datetime

MAX_CONNECTIONS = 128
ssh_sessions = {}  

def detect_ssh_connections():
    """Detects active SSH connections and updates session details."""
    ssh_connections = []

    for conn in psutil.net_connections(kind="inet"):
        if conn.laddr and conn.raddr:
            if conn.laddr.port == 22 or conn.raddr.port == 22:  
                ssh_connections.append(conn)

                conn_key = (conn.laddr.ip, conn.raddr.ip)
                if conn_key not in ssh_sessions:
                    ssh_sessions[conn_key] = {
                        "start_time": datetime.now(),
                        "end_time": None,
                        "status": "Active"
                    }
    
    active_keys = [(c.laddr.ip, c.raddr.ip) for c in ssh_connections]
    for conn_key in list(ssh_sessions.keys()):
        if conn_key not in active_keys and ssh_sessions[conn_key]["status"] == "Active":
            ssh_sessions[conn_key]["end_time"] = datetime.now()
            ssh_sessions[conn_key]["status"] = "Closed"

    return ssh_connections

def trigger_action():
    """Triggers an alert if SSH connections exceed MAX_CONNECTIONS."""
    print("[ALERT] High SSH connection detected! Taking action...")
    subprocess.run(["logger", "High SSH activity detected"])
def display_table(stdscr):
    """Displays the SSH connection summary dynamically in the terminal."""
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(1000) 

    while True:
        stdscr.clear() 
        stdscr.addstr(0, 0, "SSH Connection Summary:", curses.A_BOLD)
        stdscr.addstr(1, 0, "-" * 80)

        header = f"{'Source IP':<22} {'Destination IP':<22} {'Start Time':<20} {'End Time':<20} {'Status':<8}"
        stdscr.addstr(2, 0, header, curses.A_UNDERLINE)

        ssh_connections = detect_ssh_connections()

        row = 3
        for (src, dst), data in ssh_sessions.items():
            start_time = data["start_time"].strftime("%Y-%m-%d %H:%M:%S")
            end_time = data["end_time"].strftime("%Y-%m-%d %H:%M:%S") if data["end_time"] else "N/A"
            status = data["status"]
            line = f"{src:<22} {dst:<22} {start_time:<20} {end_time:<20} {status:<8}"
            stdscr.addstr(row, 0, line)
            row += 1

        if len(ssh_connections) >= MAX_CONNECTIONS:
            trigger_action()

        stdscr.refresh()

        # Exit on 'q' press
        key = stdscr.getch()
        if key == ord('q'):
            break

def main():
    curses.wrapper(display_table) 

if __name__ == "__main__":
    main()
