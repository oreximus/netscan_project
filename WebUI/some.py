import nmap3
import json
import ipaddress


def scan(ip_addr):
    ipaddress.ip_address(ip_addr)
    nmap = nmap3.Nmap()
    result = nmap.nmap_version_detection(
        ip_addr, args="--script vulners --script-args mincvss+5.0")
    data = json.dumps(result[ip_addr]["ports"], indent=2)
    print(data)


ip_addr = input("Enter the IP: ")

scan(ip_addr)
