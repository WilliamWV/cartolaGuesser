from __future__ import absolute_import, division, print_function, unicode_literals
import functools

import tensorflow as tf
import numpy as np
import pandas as pd

import argparse

parser = argparse.ArgumentParser(description='Receive dataset to train')
parser.add_argument('-d', '--dataset', required=True, type=str,
                   help='Train dataset')
parser.add_argument('-t', '--test', required=True, type=str,
                   help='Test dataset')

args = parser.parse_args()


def main():
    train = pd.read_csv(args.dataset, delimiter=',', header=0)
    test = pd.read_csv(args.test, delimiter=',', header=0)

    train_target = train.pop('realScore')
    train_dataset = tf.data.Dataset.from_tensor_slices((train.values, train_target.values))


if __name__ == '__main__':
    main()
