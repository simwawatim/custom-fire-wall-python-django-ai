#!/usr/bin/env python3

import os
import subprocess
import socket
import netifaces
from datetime import datetime

LOG_FILE = "/var/log/facebook_dns_block.log"
DNSMASQ_CONF = "/etc/dnsmasq.d/facebook_block.conf"

PRIVATE_IP_RANGES = [
    ("10.0.0.0", "10.255.255.255"),
    ("172.16.0.0", "172.31.255.255"),
    ("192.168.0.0", "192.168.255.255"),
]

def is_private_ip(ip):
    ip_parts = list(map(int, ip.split(".")))
    for start, end in PRIVATE_IP_RANGES:
        s = list(map(int, start.split(".")))
        e = list(map(int, end.split(".")))
        if s <= ip_parts <= e:
            return True
    return False

def detect_interfaces():
    lan_iface, wan_iface = None, None
    for iface in netifaces.interfaces():
        ifaddresses = netifaces.ifaddresses(iface)
        if netifaces.AF_INET in ifaddresses:
            ip = ifaddresses[netifaces.AF_INET][0]['addr']
            if is_private_ip(ip):
                lan_iface = iface
            else:
                wan_iface = iface
    if not lan_iface or not wan_iface:
        raise RuntimeError("Could not auto-detect LAN and WAN interfaces.")
    print(f"✅ Detected LAN: {lan_iface}, WAN: {wan_iface}")
    return lan_iface, wan_iface

def enable_nat(lan_iface, wan_iface):
    print("⚙️ Enabling NAT and IP forwarding...")
    os.system("echo 1 > /proc/sys/net/ipv4/ip_forward")
    os.system("iptables -t nat -F")
    os.system("iptables -F")
    os.system(f"iptables -t nat -A POSTROUTING -o {wan_iface} -j MASQUERADE")
    os.system(f"iptables -A FORWARD -i {lan_iface} -o {wan_iface} -j ACCEPT")
    os.system(f"iptables -A FORWARD -i {wan_iface} -o {lan_iface} -m state --state ESTABLISHED,RELATED -j ACCEPT")


def configure_dnsmasq():
    print("🛡️ Configuring dnsmasq to block Facebook...")
    config = (
        "address=/facebook.com/127.0.0.1\n"
        "address=/www.facebook.com/127.0.0.1\n"
        f"log-queries\nlog-facility={LOG_FILE}\n"
    )
    with open(DNSMASQ_CONF, "w") as f:
        f.write(config)
    os.system("systemctl restart dnsmasq")

def redirect_dns(lan_iface):
    print("🔁 Redirecting LAN DNS requests to local dnsmasq...")
    os.system(f"iptables -t nat -A PREROUTING -i {lan_iface} -p udp --dport 53 -j REDIRECT --to-ports 53")
    os.system(f"iptables -t nat -A PREROUTING -i {lan_iface} -p tcp --dport 53 -j REDIRECT --to-ports 53")

def tail_log():
    print("👁️ Monitoring blocked Facebook DNS requests (Ctrl+C to stop)...")
    try:
        subprocess.run(["tail", "-f", LOG_FILE])
    except KeyboardInterrupt:
        print("\n🛑 Stopped.")

def cleanup():
    print("🧹 Cleaning up...")
    os.system("iptables -F")
    os.system("iptables -t nat -F")
    os.system("echo 0 > /proc/sys/net/ipv4/ip_forward")
    if os.path.exists(DNSMASQ_CONF):
        os.remove(DNSMASQ_CONF)
        os.system("systemctl restart dnsmasq")
    print("✅ Restored system to normal.")

if __name__ == "__main__":
    if os.geteuid() != 0:
        exit("❌ Please run as root: sudo python3 gateway_block_facebook.py")

    try:
        lan_iface, wan_iface = detect_interfaces()
        enable_nat(lan_iface, wan_iface)
   
        configure_dnsmasq()
        redirect_dns(lan_iface)
        tail_log()
    except KeyboardInterrupt:
        cleanup()
    except Exception as e:
        print(f"❌ Error: {e}")
