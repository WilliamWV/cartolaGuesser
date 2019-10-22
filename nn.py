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


def get_values_from_dataframe(dataframe):
    values = dataframe.values
    if len(values.shape) == 2:
        return values.reshape((values.shape[0], values.shape[1], 1))
    else:
        return values


def main():
    train = pd.read_csv(args.dataset, delimiter=',', header=0)
    test = pd.read_csv(args.test, delimiter=',', header=0)

    print("Read csv data")

    test_target = test.pop('realScore')
    test_dataset = tf.data.Dataset.from_tensor_slices((test.values, test_target.values))

    print("Created test datasets")

    train_target = train.pop('realScore')
    # train_dataset = tf.data.Dataset.from_tensor_slices((train.values, train_target.values))

    print("Created train datasets")

    model = tf.keras.models.Sequential([
        tf.keras.layers.Flatten(input_shape=(22, 1)),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(1, activation='softmax')
    ])

    model.compile(optimizer='adam', loss='mean_absolute_error', metrics=['accuracy'])
    model.fit(get_values_from_dataframe(train), get_values_from_dataframe(train_target), epochs=200)
    model.evaluate(get_values_from_dataframe(test), get_values_from_dataframe(test_target))


if __name__ == '__main__':
    main()
