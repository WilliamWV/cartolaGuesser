import socket
import argparse

IP = '127.0.0.1'
BUFFER_SIZE = 1024


def parse_arguments():
    global IP
    parser = argparse.ArgumentParser(description='Server of suggestions, receives port to listen TCP connections')
    parser.add_argument('-p', '--port', help='Port to listen', required=True, type=int)
    parser.add_argument('-i', '--ip', help='IP to bind, if none is passed uses 127.0.0.1')
    args = parser.parse_args()
    if args.ip is not None:
        IP = args.ip
    return args.port


def requests(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP, port))

    print("Requesting help message")
    s.send('H'.encode('ascii'))
    data = s.recv(BUFFER_SIZE)
    print(data)


if __name__ == '__main__':
    port = parse_arguments()
    requests(port)