import socket
import struct


def recv_all(conn, size):
    # Receive the specified number of bytes from the socket so if matches with the client

    data = b''  # Initialize an empty bytes object to hold the received data
    while len(data) < size:  # Loop until we have received the requested number of bytes
        packet = conn.recv(size - len(data))  # Receive the remaining bytes
        if not packet:  # handle connection closed error
            raise ConnectionError("Connection closed")
        data += packet  # Append received packet to data
    return data  # Return the complete data received


def unpack_packet(conn, header_format):
    # Unpack a packet from the connection based on the required format.

    header_size = struct.calcsize(header_format)  # Calculate the size of the header based on the format
    received_packet = recv_all(conn, header_size)  # Receive the complete header
    unpacked_packet = struct.unpack(header_format, received_packet)  # Unpack the received packet
    return unpacked_packet


def create_response_payload(unpacked_packet, payload):
    # Create a new payload based on the unpacked header and the original payload.

    version, header_length, service_type, payload_length = unpacked_packet
    new_payload = f"Received version: {version}, Header Length: {header_length}, Service Type: {service_type}, Original Payload: {payload.decode()}"
    return new_payload.encode('utf-8')  # Encode the new payload as bytes


def create_and_send_packet(conn, header_format, version, header_length, service_type, payload):
    # Create a packet and send it through the connection.

    header = struct.pack(header_format, version, header_length, service_type, len(payload))  # Pack header
    packet = header + payload  # Combine header and payload
    conn.sendall(packet)  # Send the complete packet to the client


if __name__ == '__main__':
    host = 'localhost'
    port = 12345
    header_format = 'BBBH'  # Define the header format: 2 bytes for version and header length, 2 bytes for service type and payload length

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:  # Create a TCP socket
        s.bind((host, port))
        s.listen()
        print("Server is listening...")  # Print server status

        conn, addr = s.accept()
        with conn:
            print(f"Connected by: {addr}")  # Print client address
            while True:
                try:
                    unpacked_packet = unpack_packet(conn, header_format)  # Unpack the incoming packet
                    print(f"Received packet: {unpacked_packet}")  # Print received packet

                    # Read the payload based on the length specified in the header
                    payload_length = unpacked_packet[3]  # Extract the payload length from the unpacked header
                    payload = recv_all(conn, payload_length)  # Receive the payload data
                    print(f"Received payload: {payload.decode()}")  # Print the received payload

                    # Create a new payload based on the header and received payload
                    response_payload = create_response_payload(unpacked_packet, payload)

                    # Construct and send the response packet back to the client
                    create_and_send_packet(conn, header_format, unpacked_packet[0], unpacked_packet[1],
                                           unpacked_packet[2], response_payload)

                except Exception as e:
                    print(f"Connection closed or an error occurred: {e}")  # Print any exceptions
                    break  # Exit the loop on error
