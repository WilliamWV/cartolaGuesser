
import argparse
import os
import tensorflow as tf
import cartolafc
import pandas as pd
import numpy as np

model_names = {}
email = None
password = None
history = None


def read_model(model_path):
    return tf.keras.models.load_model(model_path)


def parse_models():
    global email, password
    parser = argparse.ArgumentParser(description='Receive models to use on prediction')
    parser.add_argument('-m', '--model', required=False, help='Path to saved model, if nothing is passed will train '
                                                              'with all models from \'/models\'')

    parser.add_argument('-e' '--email', required=True,
                        help='Registered email on cartola, used to get price of the players')
    parser.add_argument('-p' '--password', required=True,
                        help='Registered password on cartola, used to get price of the players')

    args = parser.parse_args()
    email = args.email
    password = args.password
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


def build_player_line(player_id, round_num):
    global history, email, password
    player_row = history.loc[history['PlayerID'] == player_id]
    if len(player_row > 1):
        print("ERROR: Multiple lines of the same player")
        return None
    elif len(player_row) == 0:
        return None
    else:
        player_vals = player_row.values[0][3:-1]
        player_line = np.concatenate([player_vals[:-4], player_vals[-3:]])
        api = cartolafc.Api()
        api.set_credentials(email, password)
        price = [round_score.preco for round_score in api.pontuacao_atleta(player_id) if round_score.rodada_id == round_num]
        if len(price) != 1:
            print("ERROR: could not get the price of player " + str(player_id))
            return None
        else:
            player_line[-3] = price[0]
            return player_line




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

    ata_lines = []
    mei_lines = []
    zag_lines = []
    lat_lines = []
    gol_lines = []

    for player in players:
        ata_lines = [build_player_line(player[0], current_round) for player in players if player[1] == 'ata']
        mei_lines = [build_player_line(player[0], current_round) for player in players if player[1] == 'mei']
        zag_lines = [build_player_line(player[0], current_round) for player in players if player[1] == 'zag']
        lat_lines = [build_player_line(player[0], current_round) for player in players if player[1] == 'lat']
        gol_lines = [build_player_line(player[0], current_round) for player in players if player[1] == 'gol']

    for player_set in [ata_lines, mei_lines, zag_lines, lat_lines, gol_lines]:
        player_set = [line for line in player_set if line is not None]

    valid_players = [line for line in player_lines if line is not None]
    teams = [mount_team(model) for model in models]