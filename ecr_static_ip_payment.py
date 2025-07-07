import socket
import struct
import os
from dotenv import load_dotenv

load_dotenv()


def build_echoo_ecr_message(msg_type: str, fields: list, direction='ECR', variant='01', version='01') -> bytes:
    body = f"{msg_type}/" + "/".join(fields)
    body_bytes = body.encode('ascii')

    direction_bytes = direction.encode('ascii')        
    variant_bytes = variant.encode('ascii')           
    version_bytes = version.encode('ascii')            

    header = direction_bytes + variant_bytes + version_bytes 
    total_length = len(header) + len(body_bytes)              

    length_prefix = struct.pack('>H', total_length)           

    return length_prefix + header + body_bytes

def build_universal_ecr_message(msg_types: list, fields: list, direction='ECR', variant='01', version='01') -> bytes:
    body = ""
    i = 0

    for type in msg_types:
        body += f"{type}" + fields[i]
        i+=1

    
    body_bytes = body.encode('ascii')

    direction_bytes = direction.encode('ascii')        
    variant_bytes = variant.encode('ascii')           
    version_bytes = version.encode('ascii')            

    header = direction_bytes + variant_bytes + version_bytes 
    total_length = len(header) + len(body_bytes)              

    length_prefix = struct.pack('>H', total_length)           

    return length_prefix + header + body_bytes

def send_and_listen_to_pos(ip, port, msg_bytes):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(200) 
            s.connect((ip, port))
            print(f"✅ Connected to {ip}:{port}")

            s.sendall(msg_bytes)
            print("📤 Message sent to POS.")

            while True:
                header = s.recv(2)
                if not header:
                    print("🔌 Connection closed by POS.")
                    break

                msg_len = struct.unpack('>H', header)[0]

                data = b''
                while len(data) < msg_len:
                    chunk = s.recv(msg_len - len(data))
                    if not chunk:
                        print("❌ Disconnected mid-message.")
                        return
                    data += chunk

                try:
                    direction = data[0:3].decode('ascii')
                    variant = data[3:5].decode('ascii')
                    version = data[5:7].decode('ascii')
                    body = data[7:].decode('ascii')
                except Exception as parse_err:
                    print(f"⚠️ Parsing error: {parse_err}")
                    continue

                print("\n📩 Response from POS:")
                print(f"  Direction: {direction}")
                print(f"  Variant:   {variant}")
                print(f"  Version:   {version}")
                print(f"  Body:      {body}")

                if "/Z" in body or "/Y" in body or "/N" in body:
                    print("🟢 Final transaction message received.")
                    break

    except Exception as e:
        print("❗ Error communicating with POS:", e)

if __name__ == "__main__":
    posIp = os.getenv("POS_IP")
    ip = posIp
    port = 4000

    # msg = build_echoo_ecr_message("X", ["Hello from ECR"])
    # msg = build_universal_ecr_message(["X//"], ["Hello from ECR"]) 

    msg = build_universal_ecr_message(["A//S","//F","//D","//R","//H","//T","//G","//M"], ["000001","2500:008:2","20211122123652","200111","PUPO0001","000003",":0:0:0:0","123456789123456789"])

    send_and_listen_to_pos(ip, port, msg)