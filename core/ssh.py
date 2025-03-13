import psutil
import time
import subprocess

MAX_CONNECTIONS = 128  # Limit the output to 128 connections

def detect_ssh_connections():
    ssh_connections = []
    
    for conn in psutil.net_connections(kind="inet"):
        if conn.laddr and conn.raddr:
            if conn.laddr.port == 22 or conn.raddr.port == 22:  # SSH port
                ssh_connections.append(conn)

    return ssh_connections

def trigger_action():
    print("[ALERT] High SSH connection detected! Taking action...")
    # Example: Logging or executing a shell command
    subprocess.run(["logger", "High SSH activity detected"])  # Logs to system log
    # Example: Trigger an LED if running on a Raspberry Pi
    # subprocess.run(["echo", "1", ">", "/sys/class/leds/led0/brightness"])

def main():
    while True:
        ssh_connections = detect_ssh_connections()
        
        if ssh_connections:
            print(f"\nActive SSH Connections ({min(len(ssh_connections), MAX_CONNECTIONS)} shown):")
            for conn in ssh_connections[:MAX_CONNECTIONS]:  # Print only up to 128 connections
                print(f"Local: {conn.laddr.ip}:{conn.laddr.port} <--> Remote: {conn.raddr.ip}:{conn.raddr.port}")

        if len(ssh_connections) >= 128:
            trigger_action()  # Trigger action if SSH connections reach the limit

        time.sleep(5)  # Adjust the polling interval

if __name__ == "__main__":
    main()
