import pyshark
import subprocess
import signal
import sys
import time
from collections import defaultdict

class NetworkCompromiseAssessment:
    def __init__(self, interfaces, blocked_ips=None, allowed_ips=None, log_file="network_monitor.log"):
        self.interfaces = interfaces
        self.ssh_counter = defaultdict(int)
        self.captures = []
        self.connections = set()
        self.logged_in_users = self.get_logged_in_users()
        self.blocked_ips = blocked_ips if blocked_ips else set()
        self.allowed_ips = allowed_ips if allowed_ips else set()
        self.running = True  # Control flag for stopping execution
        self.log_file = log_file
        
        self.init_captures()
        self.block_all_ssh_traffic()

        signal.signal(signal.SIGINT, self.cleanup)  # Handle Ctrl+C
        signal.signal(signal.SIGTERM, self.cleanup)  # Handle system termination

    def log(self, message):
        """Log messages to both console and file."""
        print(message)
        with open(self.log_file, "a") as f:
            f.write(message + "\n")

    def init_captures(self):
        """Initialize packet capture on valid network interfaces."""
        for iface in self.interfaces:
            try:
                capture = pyshark.LiveCapture(interface=iface, display_filter="tcp")
                self.captures.append(capture)
                self.log(f"[*] Monitoring network on {iface}")
            except Exception as e:
                self.log(f"[!] Failed to initialize capture on {iface}: {e}")

    def cleanup(self, signum=None, frame=None):
        """Cleanup firewall rules and exit."""
        self.log("\n[!] Cleaning up firewall rules before exiting...")
        try:
            for ip in self.blocked_ips:
                subprocess.run(["sudo", "iptables", "-D", "INPUT", "-s", ip, "-j", "DROP"], check=True)
                self.log(f"[+] Unblocked {ip}")
            
            subprocess.run(["sudo", "iptables", "-D", "INPUT", "-p", "tcp", "--dport", "22", "-j", "DROP"], check=True)
            self.log("[+] Restored normal SSH traffic.")

            for ip in self.allowed_ips:
                subprocess.run(["sudo", "iptables", "-D", "INPUT", "-s", ip, "-p", "tcp", "--dport", "22", "-j", "ACCEPT"], check=True)

        except Exception as e:
            self.log(f"[!] Error during cleanup: {e}")

        self.running = False
        self.log("[*] Exiting gracefully...")
        sys.exit(0)

    def get_logged_in_users(self):
        """Retrieve a list of currently logged-in users."""
        try:
            output = subprocess.check_output(["who"], universal_newlines=True)
            return [line.split()[0] for line in output.splitlines()]
        except Exception as e:
            self.log(f"[!] Error retrieving logged-in users: {e}")
            return []

    def block_all_ssh_traffic(self):
        """Block all SSH traffic except for allowed IPs."""
        self.log("[*] Blocking all SSH traffic except allowed IPs...")
        subprocess.run(["sudo", "iptables", "-A", "INPUT", "-p", "tcp", "--dport", "22", "-j", "DROP"], check=True)
        for ip in self.allowed_ips:
            subprocess.run(["sudo", "iptables", "-I", "INPUT", "-s", ip, "-p", "tcp", "--dport", "22", "-j", "ACCEPT"], check=True)
            self.log(f"[+] Allowed SSH access from {ip}")

    def detect_ssh_handshake(self, packet):
        """Detect SSH handshake attempts and block brute-force attacks."""
        try:
            if "IP" in packet and "TCP" in packet:
                src_ip = packet.ip.src
                port = packet.tcp.dstport

                if int(port) == 22:
                    if src_ip in self.allowed_ips:
                        self.log(f"[✓] Allowed SSH attempt from {src_ip}, ignoring...")
                        return

                    self.ssh_counter[src_ip] += 1
                    self.log(f"[*] SSH attempt from {src_ip} ({self.ssh_counter[src_ip]} times)")

                    if self.ssh_counter[src_ip] >= 3 and src_ip not in self.blocked_ips:
                        self.log(f"[!] Blocking SSH attempts from {src_ip}")
                        subprocess.run(["sudo", "iptables", "-A", "INPUT", "-s", src_ip, "-j", "DROP"], check=True)
                        self.blocked_ips.add(src_ip)
        except Exception as e:
            self.log(f"[!] Error processing packet: {e}")

    def start_capture(self):
        """Continuously monitor network traffic until manually stopped."""
        self.log(f"[*] Starting packet capture on interfaces: {', '.join(self.interfaces)}")
        try:
            while self.running:
                for capture in self.captures:
                    try:
                        capture.apply_on_packets(self.detect_ssh_handshake, timeout=10)
                    except Exception as e:
                        self.log(f"[!] Error capturing packets: {e}")
                time.sleep(1)  # Reduce CPU usage
        except KeyboardInterrupt:
            self.log("\n[!] KeyboardInterrupt detected. Cleaning up...")
        except Exception as e:
            self.log(f"[!] Unexpected error: {e}")
        finally:
            self.cleanup()

if __name__ == "__main__":
    interfaces = ["eth0", "wlan0"]  
    allowed_ips = {"172.17.160.1", "192.168.1.101"}
    monitor = NetworkCompromiseAssessment(interfaces, allowed_ips=allowed_ips)
    monitor.start_capture()
