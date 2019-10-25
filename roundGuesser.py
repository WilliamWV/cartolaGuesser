
import argparse
import os
import tensorflow as tf
import cartolafc
import pandas as pd

model_names = {}
history = None


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

    mod = []
    for path in pred_models:
        model = read_model(path)
        model_names[model] = path.replace('.h5', '')
        mod.append(model)

    return mod


def get_players():
    provavel_status = 7
    atletas = cartolafc.Api().mercado_atletas()
    return [(atleta.id, atleta.posicao.abreviacao) for atleta in atletas if atleta.status.id == provavel_status]


def read_history(year, round_num):
    history_file = 'scoresExtractedData.csv'
    data = pd.read_csv(history_file, header=0, delimiter=',')
    year_data = data[data["Year"] == year]
    round_data = year_data[year_data["Round"] == round_num - 1]
    return round_data


def build_player_line(player):
    global history
    player_id = player[0]
    player_pos = player[1]
    player_row = history.loc[history['PlayerID'] == 85930]
    if len(player_row > 1):
        print("ERROR: Multiple lines of the same player")
        exit()
    elif len(player_row) == 0:
        pass
    else:
        player_vals = player_row.values[0][3:-1]


def predict_player_score(player, model):
    pass


def choose_coach(model):
    pass

def mount_team(model):
    pass


if __name__ == '__main__':
    current_round = cartolafc.Api().mercado().rodada_atual
    current_year = cartolafc.Api().mercado().fechamento.year
    models = parse_models()
    players = get_players()
    history = read_history(current_year, current_round)
    player_lines = [build_player_line(player) for player in players]
    teams = [mount_team(model) for model in models]