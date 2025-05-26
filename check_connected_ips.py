import psutil

for iface, snics in psutil.net_if_addrs().items():
    print(f"Interface: {iface}")
    for snic in snics:
        print(f"  Address: {snic.address}")
