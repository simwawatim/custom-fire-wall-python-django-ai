print('now ')
import logging
import time
import psutil
import pyshark
import threading
from datetime import datetime

class SSHMonitor:
    def __init__(self):
        self.interfaces = self.get_interfaces()
        self.captures = []  # Initially an empty list for captures

        # If no interfaces are found, set a default interface for testing
        if not self.interfaces:
            self.interfaces = ['lo']  # Use 'lo' (loopback) interface for testing

        # Set up logging
        logging.basicConfig(
            level=logging.DEBUG,  # Show all levels of logs (DEBUG and higher)
            format='%(asctime)s - %(levelname)s - %(message)s',  # Add timestamp to each log
            handlers=[
                logging.StreamHandler(),  # Output to the console
                logging.FileHandler("network_monitor.log")  # Output to file
            ]
        )

        # Create captures for each interface
        self.captures = [pyshark.LiveCapture(interface=iface, bpf_filter='tcp port 22') for iface in self.interfaces]
        self.running = True

    def log(self, message):
        """Log messages to both console and file."""
        logging.info(message)

    def get_interfaces(self):
        """Get all active network interfaces."""
        interfaces = psutil.net_if_addrs()
        active_interfaces = [iface for iface, addrs in interfaces.items() if addrs]
        if not active_interfaces:
            self.log("[!] No active interfaces detected.")
        else:
            self.log(f"[*] Active interfaces: {', '.join(active_interfaces)}")
        return active_interfaces

    def detect_ssh_handshake(self, packet):
        """Detect SSH handshakes and log connection start and end times."""
        try:
            if 'SSH' in packet:
                ip_src = packet.ip.src
                ip_dst = packet.ip.dst
                start_time = datetime.now()  # Capture connection start time
                self.log(f"[✓] SSH connection attempt from {ip_src} to {ip_dst} at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

                # Simulate the end time after some time (e.g., after 10 seconds)
                time.sleep(10)  # Placeholder for actual connection duration (this could be based on your own logic)
                
                end_time = datetime.now()  # Capture connection end time
                self.log(f"[✓] SSH connection ended from {ip_src} to {ip_dst} at {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            self.log(f"[!] Error in SSH handshake detection: {e}")

    def start_capture(self):
        """Start packet capture on all active interfaces."""
        self.log(f"[*] Starting packet capture on interfaces: {', '.join(self.interfaces)}")
        try:
            while self.running:
                for capture in self.captures:
                    try:
                        self.log(f"[*] Capturing packets on {capture.interface}...")
                        capture.sniff(timeout=10)  # Sniff packets for 10 seconds
                        self.log(f"[*] Finished capturing packets on {capture.interface}...")

                        for packet in capture:
                            self.detect_ssh_handshake(packet)

                    except Exception as e:
                        self.log(f"[!] Error capturing packets: {e}")
                time.sleep(1)  # Reduce CPU usage
        except KeyboardInterrupt:
            self.log("\n[!] KeyboardInterrupt detected. Cleaning up...")
        except Exception as e:
            self.log(f"[!] Unexpected error: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up any resources after capture ends."""
        self.log("[*] Cleaning up resources...")
        self.running = False
        for capture in self.captures:
            capture.close()

    def run(self):
        """Run the SSH monitoring."""
        self.log("[*] Starting SSH monitoring...")
        capture_thread = threading.Thread(target=self.start_capture)
        capture_thread.start()
        capture_thread.join()

if __name__ == "__main__":
    monitor = SSHMonitor()
    monitor.run()
