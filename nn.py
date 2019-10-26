from __future__ import absolute_import, division, print_function, unicode_literals

import os

import pandas as pd
import tensorflow as tf

datasets = [
    ('train/scoresAta_train.csv', 'test/scoresAta_test.csv'),
    ('train/scoresMei_train.csv', 'test/scoresMei_test.csv'),
    ('train/scoresZag_train.csv', 'test/scoresZag_test.csv'),
    ('train/scoresLat_train.csv', 'test/scoresLat_test.csv'),
    ('train/scoresGol_train.csv', 'test/scoresGol_test.csv'),
]

dataset_abbr = {
    'train/scoresAta_train.csv': 'ata',
    'train/scoresMei_train.csv': 'mei',
    'train/scoresZag_train.csv': 'zag',
    'train/scoresLat_train.csv': 'lat',
    'train/scoresGol_train.csv': 'gol',
}

EPOCHS = 50
LOG_DIR = "logs\\fit_saved_08\\"
MODELS_DIR = 'models_08\\'


class Model:

    def __init__(self, model, name, train_tuple, test_tuple):
        self.model = model
        self.name = name
        self.train_dataset = train_tuple[0]
        self.train_target = train_tuple[1]
        self.test_dataset = test_tuple[0]
        self.test_target = test_tuple[1]
        similar_items = 0
        for item in os.listdir(LOG_DIR):
            if item.find(self.name) >= 0:
                similar_items += 1
        log_dir = LOG_DIR + self.name
        if similar_items > 0:
            log_dir += '_' + str(similar_items)

        self.tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)

    def train(self):
        self.model.compile(optimizer='adam', loss='mse', metrics=['mse', 'mae'])
        self.model.fit(
            self.train_dataset, self.train_target,
            epochs=EPOCHS, callbacks=[self.tensorboard_callback],
            validation_data=(self.test_dataset, self.test_target)
        )

    def evaluate(self):
        self.model.evaluate(self.test_dataset, self.test_target, callbacks=[self.tensorboard_callback])

    def save(self, abbr):
        similar_items = 0
        for item in os.listdir(MODELS_DIR):
            if item.find(self.name) >= 0:
                similar_items += 1

        if similar_items > 0:
            file_name = self.name + '_' + abbr + '_' + str(similar_items) + '.h5'
        else:
            file_name = self.name + '_' + abbr + '.h5'

        self.model.save(MODELS_DIR + file_name)


def read_data(train_dataset, test_dataset):
    train = pd.read_csv(train_dataset, delimiter=',', header=0)
    test = pd.read_csv(test_dataset, delimiter=',', header=0)
    test_target = test.pop('realScore')
    train_target = train.pop('realScore')

    return (train, train_target), (test, test_target)


def build_models(train_tuple, test_tuple, abbr):
    models = []
    # 64x64 Dropout = 0.5
    temp_model = tf.keras.models.Sequential([
        tf.keras.layers.Dense(22, activation='relu', input_shape=[22]),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(1)
    ])
    models.append(Model(temp_model, "64x64_dropout_05_" + abbr, train_tuple, test_tuple))

    # 64x64 No regularization
    temp_model = tf.keras.models.Sequential([
        tf.keras.layers.Dense(22, activation='relu', input_shape=[22]),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(1)
    ])
    models.append(Model(temp_model, "64x64_noreg_" + abbr, train_tuple, test_tuple))

    # 64x64 Dropout = 0.2
    temp_model = tf.keras.models.Sequential([
        tf.keras.layers.Dense(22, activation='relu', input_shape=[22]),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(1)
    ])
    models.append(Model(temp_model, "64x64_dropout_02_" + abbr, train_tuple, test_tuple))

    # 512 Dropout = 0.5
    temp_model = tf.keras.models.Sequential([
        tf.keras.layers.Dense(22, activation='relu', input_shape=[22]),
        tf.keras.layers.Dense(512, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(1)
    ])
    models.append(Model(temp_model, "512_dropout_05_" + abbr, train_tuple, test_tuple))

    # 512 Dropout = 0.2
    temp_model = tf.keras.models.Sequential([
        tf.keras.layers.Dense(22, activation='relu', input_shape=[22]),
        tf.keras.layers.Dense(512, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(1)
    ])
    models.append(Model(temp_model, "512_dropout_02_" + abbr, train_tuple, test_tuple))

    temp_model = tf.keras.models.Sequential([
        tf.keras.layers.Dense(22, activation='relu', input_shape=[22]),
        tf.keras.layers.Dense(256, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(1)
    ])
    models.append(Model(temp_model, "256x128_dropout_02_" + abbr, train_tuple, test_tuple))

    temp_model = tf.keras.models.Sequential([
        tf.keras.layers.Dense(22, activation='relu', input_shape=[22]),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(1)
    ])
    models.append(Model(temp_model, "128x64x32_dropout_02_" + abbr, train_tuple, test_tuple))

    temp_model = tf.keras.models.Sequential([
        tf.keras.layers.Dense(22, activation='relu', input_shape=[22]),
        tf.keras.layers.Dense(256, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(1)
    ])
    models.append(Model(temp_model, "256x128_dropout_05_" + abbr, train_tuple, test_tuple))

    temp_model = tf.keras.models.Sequential([
        tf.keras.layers.Dense(22, activation='relu', input_shape=[22]),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(1)
    ])
    models.append(Model(temp_model, "128x64x32_dropout_05_" + abbr, train_tuple, test_tuple))

    return models


def main():
    for dataset in datasets:
        train_tuple, test_tuple = read_data(dataset[0], dataset[1])
        models = build_models(train_tuple, test_tuple, dataset_abbr[dataset[0]])
        for model in models:
            model.train()
            model.evaluate()
            model.save(dataset_abbr[dataset[0]])


if __name__ == '__main__':
    main()
