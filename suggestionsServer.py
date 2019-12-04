import argparse
import socket
import cartolafc

IP = '127.0.0.1'
BUFFER_SIZE = 16
BACKLOG = 5

'''
OPERATIONS:
    - 'S',  # Get suggestions to this round
    - 'H',  # Help, should return all operations available and a small description
    - 'P',  # Get suggestions to previous round -> needs an additional integer to indicate the round ex: P34
    - Any other input should receive an error message and the help response
'''

SUGGESTION_OP = 'S'
PREVIOUS_SUGG_OP = 'P'
HELP_OP = 'H'


def parse_arguments():
    global IP
    parser = argparse.ArgumentParser(description='Server of suggestions, receives port to listen TCP connections')
    parser.add_argument('-p', '--port', help='Port to listen', required=True, type=int)
    parser.add_argument('-i', '--ip', help='IP to bind, if none is passed uses 127.0.0.1')
    args = parser.parse_args()
    if args.ip is not None:
        IP = args.ip
    return args.port


def listen(port):
    s_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_listener.bind((IP, port))
    s_listener.listen(BACKLOG)

    conn, addr = s_listener.accept()
    print("Connected with " + str(addr))
    process(conn, addr)


def suggestion(conn, addr, round_num):
    pass


def help(conn, addr):
    pass


def error(conn, addr):
    pass


def process(conn, addr):
    data = conn.recv(BUFFER_SIZE)
    if not data:
        error(conn, addr)
    else:
        if data[0] == SUGGESTION_OP:
            current_round = cartolafc.Api().mercado().rodada_atual
            suggestion(conn, addr, current_round)
        elif data[0] == PREVIOUS_SUGG_OP:
            try:
                round_num = int(data[1:])
                suggestion(conn, addr, round_num)
            except ValueError:
                error(conn, addr)
        elif data[0] == HELP_OP:
            help(conn, addr)
        else:
            error(conn, addr)


if __name__ == '__main__':
    port = parse_arguments()
    listen(port)