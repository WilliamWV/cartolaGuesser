import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(description='Server of suggestions, receives port to listen TCP connections')
    parser.add_argument('-p', '--port', help='Port to listen', required = True, type = int)
    args = parser.parse_args()
    return args.port


def listen():
    pass


def process():
    pass


def response():
    pass


if __name__ == '__main__':
    parse_arguments()
    listen()