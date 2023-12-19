import nmap3
import ipaddress
import json


def scanning(ip_addr):
    try:
        ipaddress.ip_address(ip_addr)
        nmap = nmap3.Nmap()
        result = nmap.nmap_version_detection(
            ip_addr, args="--script vulners --script-args mincvss+5.0")
        data = json.dumps(result[ip_addr]["ports"], indent=2)
        print(data)
        with open("output.json", "w") as out_file:
            json.dump(data, out_file)
    except Exception:
        print("Enter a Valid Ip Address!")


if __name__ == '__main__':
    ip_addr = input("Enter the IP Address: ")
    scanning(ip_addr)
