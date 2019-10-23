from __future__ import absolute_import, division, print_function, unicode_literals
import functools
import tensorflow as tf
from tensorflow import keras
import numpy as np
import pandas as pd
import datetime
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

    test_target = test.pop('realScore')
    train_target = train.pop('realScore')

    model = tf.keras.models.Sequential([
        tf.keras.layers.Dense(22, activation='relu', input_shape=[22]),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(1)
    ])

    log_dir = "logs\\fit\\" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)

    model.compile(optimizer='adam', loss='mse', metrics=['mse', 'mae'])
    model.fit(
        train, train_target,
        epochs=200, callbacks=[tensorboard_callback],
        validation_data=(test, test_target)
    )
    model.evaluate(test, test_target, callbacks=[tensorboard_callback])


if __name__ == '__main__':
    main()
