

import argparse
import socket
import struct


def connect_to_server(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host, port))
        print("Connected to server!")

        # Create and send the packet
        packet = create_packet(args.version, args.header_length, args.service_type, payload)
        client_socket.sendall(packet)  # Send the entire packet (header + payload)


        header_format = "BBBH"  # Ensure this matches the server
        packet_size = struct.calcsize(header_format)
        response = client_socket.recv(packet_size)  # Receive the header size response
        unpacked_header = struct.unpack(header_format, response)
        print("Received header:", unpacked_header)  

        
        payload_length = unpacked_header[3]  # Extract the payload length from the header
        payload_data = client_socket.recv(payload_length)  # Receive the payload
        print("Received payload:", payload_data.decode()) 

    # print exceptions based on errors
    except ConnectionResetError:
        print("Connection Reset Error")
    except ConnectionAbortedError:
        print("Connection Aborted")
    except ConnectionRefusedError:
        print("Connection refused")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        client_socket.close()


def create_packet(version, header_length, service_type, payload):
    # Compute payload length based on service type
    if service_type == 1:  # Integer payload
        payload_encoded = struct.pack('i', payload)
    elif service_type == 2:  # Float payload
        payload_encoded = struct.pack('f', payload)
    elif service_type == 3:  # String payload
        payload_encoded = payload.encode('utf-8')
    else:
        raise ValueError("Invalid service_type")

    payload_length = len(payload_encoded)

    # Create the fixed-length header
    header = struct.pack('BBBH', version, header_length, service_type, payload_length)

    # Return header + payload
    packet_created = header + payload_encoded
    return packet_created


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Client for packet creation and sending.")
    parser.add_argument('--version', type=int, required=True, help='Packet version')
    parser.add_argument('--header_length', type=int, required=True, help='Length of the packet header')
    parser.add_argument('--service_type', type=int, required=True,
                        help='Service type of the payload (1 for int, 2 for float, 3 for string)')
    parser.add_argument('--payload', type=str, required=True, help='Payload to be packed into the packet')
    parser.add_argument('--host', type=str, default='localhost', help='Server host')
    parser.add_argument('--port', type=int, default=12345, help='Server port')
    args = parser.parse_args()

    if args.service_type == 1:
        payload = int(args.payload)  # Service type 1 = Integer payload
    elif args.service_type == 2:
        payload = float(args.payload)  # Service type 2 = Float payload
    elif args.service_type == 3:
        payload = str(args.payload)  # Service type 3 = String payload
    else:
        raise ValueError("Invalid service type")

    # Connect to the server and perform operations
    connect_to_server("localhost", 12345)
