import argparse
import pyshark
from collections import defaultdict
from colorama import init

init(autoreset=True)  # Automatically reset color after each print statement

class NetworkCompromiseAssessment:
    def __init__(self, interfaces):
        self.interfaces = interfaces
        self.ssh_counter = defaultdict(int)
        self.captures = [pyshark.LiveCapture(interface=iface) for iface in self.interfaces]

    def detect_ssh_tunneling(self, packet):
        try:
            if hasattr(packet, 'ssh') and hasattr(packet, 'tcp'):
                sport = int(packet.tcp.srcport)
                dport = int(packet.tcp.dstport)

                if sport > 1024 or dport > 1024:  # Non-standard SSH port usage
                    print(f"[+] Suspicious SSH tunneling detected on port {sport} -> {dport}")
                    print(packet)
        except AttributeError:
            pass  # Ignore packets that do not have the required fields

    def start_capture(self):
        print(f"[*] Monitoring network on interfaces: {', '.join(self.interfaces)}")
        
        for capture in self.captures:
            capture.apply_on_packets(self.detect_ssh_tunneling, timeout=60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Live Network SSH Traffic Monitor")
    parser.add_argument(
        "-i", "--interfaces", 
        type=str, 
        nargs="*",  # Accept multiple interfaces or none (detect automatically)
        help="Network interfaces to capture traffic from (e.g., eth0, wlan0, Wi-Fi, Ethernet)"
    )
    args = parser.parse_args()

    # Auto-detect active interfaces if none are provided
    if not args.interfaces:
        import psutil  # Requires `pip install psutil`
        active_interfaces = [iface for iface in psutil.net_if_addrs().keys()]
        args.interfaces = active_interfaces

    assessment = NetworkCompromiseAssessment(args.interfaces)
    assessment.start_capture()
