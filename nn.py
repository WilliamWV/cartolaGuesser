from __future__ import absolute_import, division, print_function, unicode_literals
import functools

import tensorflow as tf
import numpy as np

import argparse

parser = argparse.ArgumentParser(description='Receive dataset to train')
parser.add_argument('-d', '--dataset', required=True, type = str,
                   help='Dataset to train')
args = parser.parse_args()

def main():



if __name__ == '__main__':
    main()
