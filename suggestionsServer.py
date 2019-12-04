import argparse
import socket
import cartolafc
import time
import os

IP = '127.0.0.1'
BUFFER_SIZE = 16
BACKLOG = 5

HELP_MESSAGE = " \
    \nOPERATIONS: \
        \n\t- 'S',  # Get suggestions to this round \
        \n\t- 'H',  # Help, should return all operations available and a small description \
        \n\t- 'P',  # Get suggestions to previous round -> needs an additional integer to indicate the round ex: P34 \
        \n\t- Any other input should receive an error message and the help response \
    \nRESPONSES: \
        \n\tFormed as: \
        \n\t- s,r: where s is the status and r the response message \
        \n\tStatus are: \
            \n\t\t0: OK \
            \n\t\t1: Failed to read data \
            \n\t\t2: Failed to obtain round number \
            \n\t\t3: Unknown operation \
            \n\t\t4: Suggestions not found \
"

OK = 0
FAILED_TO_READ_DATA = 1
FAILED_TO_OBTAIN_ROUND = 2
UNKNOWN_OP = 3
SUGGESTION_NOT_FOUND = 4

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
    process(conn)


def suggestion(conn, round_num):
    current_year = time.localtime().tm_year
    suggestion_dir = 'suggestion/' + str(current_year) + '/'
    if round_num in [int(file.replace('.txt', '')) for file in os.listdir(suggestion_dir)]:
        file = open(suggestion_dir + str(round_num) + '.txt')
        message = file.read()
        conn.send(str(OK) + ',' + str(message))
    else:
        error(conn, SUGGESTION_NOT_FOUND, "Could not find suggestions to round " + str(round_num))


def help(conn):
    conn.send(str(OK) + "," + HELP_MESSAGE)


def error(conn, code, message):
    conn.send(str(code) + "," + message)


def process(conn):
    data = conn.recv(BUFFER_SIZE)
    if not data:
        error(conn, FAILED_TO_READ_DATA, "Failed to read request message")
    else:
        if data[0] == SUGGESTION_OP:
            current_round = cartolafc.Api().mercado().rodada_atual
            suggestion(conn, current_round)
        elif data[0] == PREVIOUS_SUGG_OP:
            try:
                round_num = int(data[1:])
                suggestion(conn, round_num)
            except ValueError:
                error(conn, FAILED_TO_OBTAIN_ROUND, "Failed to obtain a number to identify the previous round "
                                                    "from: " + str(data))
        elif data[0] == HELP_OP:
            help(conn)
        else:
            error(conn, UNKNOWN_OP, "Unknown operation: " + str(data))
    conn.close()


if __name__ == '__main__':
    port = parse_arguments()
    listen(port)
