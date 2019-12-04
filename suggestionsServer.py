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
RESPONSES:
    Formed as:
    - s,r: where s is the status and r the response
    Status are:
        0: OK
        1: Failed to read data
        2: Failed to obtain round number
        3: Unknown operation
    
'''

OK = 0
FAILED_TO_READ_DATA = 1
FAILED_TO_OBTAIN_ROUND = 2
UNKNOWN_OP = 3

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


def error(conn, addr, code, message):
    conn.send(str(code) + ": " + message)


def process(conn, addr):
    data = conn.recv(BUFFER_SIZE)
    if not data:
        error(conn, addr, FAILED_TO_READ_DATA, "Failed to read request message")
    else:
        if data[0] == SUGGESTION_OP:
            current_round = cartolafc.Api().mercado().rodada_atual
            suggestion(conn, addr, current_round)
        elif data[0] == PREVIOUS_SUGG_OP:
            try:
                round_num = int(data[1:])
                suggestion(conn, addr, round_num)
            except ValueError:
                error(conn, addr, FAILED_TO_OBTAIN_ROUND, "Failed to obtain a number to identify the previous round "
                                                          "from: " + str(data))
        elif data[0] == HELP_OP:
            help(conn, addr)
        else:
            error(conn, addr, UNKNOWN_OP, "Unknown operation: " + str(data))
    conn.close()


if __name__ == '__main__':
    port = parse_arguments()
    listen(port)