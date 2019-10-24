
import argparse
import os
import tensorflow as tf
import cartolafc

model_names = {}


def read_model(model_path):
    return tf.keras.models.load_model(model_path)


def parse_models():
    parser = argparse.ArgumentParser(description='Receive models to use on prediction')
    parser.add_argument('-m', '--model', required=False, help='Path to saved model, if nothing is passed will train '
                                                              'with all models from \'/models\'')

    args = parser.parse_args()
    pred_models = []
    if args.model is None:
        for item in os.listdir('models'):
            pred_models.append('models/' + item)
    else:
        pred_models = [args.model]

    return [read_model(path) for path in pred_models]


def get_players():
    provavel_status = 7
    atletas = cartolafc.Api().mercado_atletas()
    return [atleta.id for atleta in atletas if atleta.status.id == provavel_status]


def build_player_line(player):
    pass

def predict_player_score(player, model):
    pass


def choose_coach(model):
    pass

def mount_team(model):
    pass


if __name__ == '__main__':
    models = parse_models()
    players = get_players()
    player_lines = [build_player_line(player) for player in players]
    teams = [mount_team(model) for model in models]