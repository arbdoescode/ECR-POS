import asyncio
import socket
import struct
import platform
import psutil
from ipaddress import IPv4Address


def build_universal_ecr_message(msg_types, fields, direction='ECR', variant='01', version='01'):
    body = ''.join(f"{t}{f}" for t, f in zip(msg_types, fields))
    body_bytes = body.encode('ascii')
    header = direction.encode('ascii') + variant.encode('ascii') + version.encode('ascii')
    total_length = len(header) + len(body_bytes)
    length_prefix = struct.pack('>H', total_length)
    return length_prefix + header + body_bytes


async def test_conn_ecr_message(ip, port, msg_bytes):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(ip, port), timeout=3)
        writer.write(msg_bytes)
        await writer.drain()
        
        response = await asyncio.wait_for(reader.read(1024), timeout=2)
        if len(response) < 2:
            return None

        msg_len = struct.unpack('>H', response[:2])[0]
        message = response[2:2+msg_len]

        direction = message[0:3].decode('ascii')
        variant = message[3:5].decode('ascii')
        version = message[5:7].decode('ascii')
        body = message[7:].decode('ascii')

        print(f"✅ Got response from {ip}: {body}")
        writer.close()
        await writer.wait_closed()
        return {'direction': direction, 'variant': variant, 'version': version, 'body': body}
    except Exception as e:
        return None


async def send_and_listen_to_pos(ip, port, msg_bytes):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(ip, port), timeout=60)
        print(f"✅ Connected to {ip}:{port}")
        writer.write(msg_bytes)
        await writer.drain()
        print("📤 Message sent to POS")

        response_buffer = b''

        while True:
            data = await reader.read(1024)
            if not data:
                break

            response_buffer += data
            while len(response_buffer) >= 2:
                msg_len = struct.unpack('>H', response_buffer[:2])[0]
                if len(response_buffer) >= 2 + msg_len:
                    message = response_buffer[2:2+msg_len]
                    response_buffer = response_buffer[2+msg_len:]

                    direction = message[0:3].decode('ascii')
                    variant = message[3:5].decode('ascii')
                    version = message[5:7].decode('ascii')
                    body = message[7:].decode('ascii')

                    print('\n📩 Response from POS:')
                    print(f'  Direction: {direction}')
                    print(f'  Variant:   {variant}')
                    print(f'  Version:   {version}')
                    print(f'  Body:      {body}')

                    if any(x in body for x in ['/Z', '/Y', '/N']):
                        print('🟢 Final transaction message received')
                        writer.close()
                        await writer.wait_closed()
                        return {'direction': direction, 'variant': variant, 'version': version, 'body': body}

                    if 'E/' in body:
                        error_map = {
                            '001': "Not supported protocol",
                            '002': "Same session number as previous",
                            '003': "Syntax error in message",
                            '004': "Currency code mismatch",
                            '100': "Internal POS error",
                            '999': "POS is busy",
                        }
                        error_type = next((desc for code, desc in error_map.items() if code in body), "Timeout")
                        print(f'🔴 Error occurred: {error_type}')
                else:
                    break
    except asyncio.TimeoutError:
        print("❌ Timeout connecting to POS")
    except Exception as e:
        print(f"❗ Error communicating with POS: {e}")


async def scan_ip_range(base_ip):
    print("🔍 Scanning for POS device")
    port = 4000
    msg = build_universal_ecr_message(["X//"], ["Hello from ECR"])

    tasks = []
    found = None
    print(base_ip)
    async def try_ip(ip):
        nonlocal found
        if found:
            return
        result = await test_conn_ecr_message(ip, port, msg)
        if result and result.get('body'):
            print(f"✅ POS found at {ip}")
            found = ip

    for i in range(1, 255):
        ip = f"{base_ip}{i}"
        tasks.append(try_ip(ip))

    await asyncio.gather(*tasks)
    return found


async def send_pos_request(ip):
    port = 4000
    msg = build_universal_ecr_message(
        ["A//S", "//F", "//D", "//R", "//H", "//T", "//G", "//M"],
        ["000100", "5000:008:2", "20211122123652", "200111", "PUPO9999", "000032", ":0:0:0:0", "123456789123456789"]
    )
    await send_and_listen_to_pos(ip, port, msg)


def get_wifi_ipv4_prefix():
   
    for iface, snics in psutil.net_if_addrs().items():
        
        if "Wi-Fi" in iface or "wlan" in iface:
            for snic in snics:
                if snic.family == socket.AF_INET:
                    ip_parts = snic.address.split('.')
                    return '.'.join(ip_parts[:3]) + '.'
        if "Ethernet" in iface or "wlan" in iface:
            for snic in snics:
                if snic.family == socket.AF_INET:
                    ip_parts = snic.address.split('.')
                    return '.'.join(ip_parts[:3]) + '.'
    return None

def is_local_lan(ip):
    return (
        #bypass VPN ip and disabled ips (start with 169.254.) to find your device
        ip.startswith("your VPN Ip") or ip.startswith("169.254.")
    )

def get_wifi_ipv4_prefix_new():
    for iface, snics in psutil.net_if_addrs().items():
        if "Wi-Fi" in iface or "wlan" in iface or "Ethernet" in iface:
            for snic in snics:
                if snic.family == socket.AF_INET:
                    ip = snic.address
                    if is_local_lan(ip): 
                        continue
                    ip_parts = ip.split('.')
                    return '.'.join(ip_parts[:3]) + '.'
    return None

async def main():

    base_ip = get_wifi_ipv4_prefix_new()

    if not base_ip:
        print("❌ Device has no connection to Wi-Fi")
        return

    found_ip = await scan_ip_range(base_ip)
    if found_ip:
        await send_pos_request(found_ip)
    else:
        print("❌ POS not found")

if __name__ == "__main__":
    asyncio.run(main())