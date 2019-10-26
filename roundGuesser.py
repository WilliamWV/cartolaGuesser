
import argparse
import os
import tensorflow as tf
import cartolafc
import pandas as pd
import numpy as np

model_names = {}
teams_score = {}
max_players_same_pos = {
    'gol': 1,
    'lat': 2,
    'zag': 3,
    'mei': 5,
    'ata': 3
}
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
        inp_model = read_model(path)
        model_names[inp_model] = path.replace('.h5', '')
        mod.append(inp_model)

    return mod


def get_players():
    provavel_status = 7
    atletas = cartolafc.Api().mercado_atletas()
    return [(atleta.id, atleta.posicao.abreviacao) for atleta in atletas if atleta.status.id == provavel_status]


def read_history(year, round_num):
    history_file = 'scoresExtractedData.csv'
    data = pd.read_csv(history_file, header=0, delimiter=',', encoding='ISO-8859-1')
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
        player_team = player_row.values[3]
        player_vals = player_row.values[0][4:-1]
        player_line = np.concatenate([player_vals[:-4], player_vals[-3:]])
        api = cartolafc.Api()
        api.set_credentials(email, password)
        price = [
            round_score.preco
            for round_score in api.pontuacao_atleta(player_id)
            if round_score.rodada_id == round_num
        ]
        if len(price) != 1:
            print("ERROR: could not get the price of player " + str(player_id))
            return None
        else:
            player_line[-3] = price[0]
            return player_line, player_id, player_team


def predict_players_score(player_lines, trained_model):
    players_scores = {}
    for player_line in player_lines:
        line = player_line[0]
        player_id = player_line[1]
        player_team = player_line[2]
        tensor = tf.convert_to_tensor(line.reshape((1, 22)), np.float32)
        score = trained_model.predict(tensor).tolist()[0][0]
        players_scores[player_id] = score
        if teams_score.get(player_team) is None:
            teams_score[player_team] = 0.0

        teams_score[player_team] += score
    return players_scores


def suggest_coach():
    suggested_teams = [c for c in teams_score if teams_score[c] == max(teams_score.values())]
    players = cartolafc.Api().mercado_atletas()
    coachs = [c for c in players if c.posicao[2] == 'tec']
    return [c.id for c in coachs if c.clube.nome in suggested_teams]

def get_highest_scores(players_scores, num_players):
    items = players_scores.items
    score_vals = [item[1] for item in items]
    arr = np.array(score_vals)
    highest_indexes = arr.argsort[-num_players:][::-1]
    return [items[ind] for ind in highest_indexes]


def get_suggestions(players_scores, pos):

    # Each model generates a list with the highest predicted score
    # this list will contains the maximum possible number of player from the same position
    # playing together, that is:
    # gol  ->  1
    # lat  ->  2
    # zag  ->  3
    # mei  ->  5
    # ata  ->  3

    max_players = max_players_same_pos[pos]
    return get_highest_scores(players_scores, max_players)


def get_model_position(model_structure):
    if model_names[model_structure].find('ata') >= 0:
        return 'ata'
    if model_names[model_structure].find('mei') >= 0:
        return 'mei'
    if model_names[model_structure].find('zag') >= 0:
        return 'zag'
    if model_names[model_structure].find('lat') >= 0:
        return 'lat'
    if model_names[model_structure].find('gol') >= 0:
        return 'gol'


if __name__ == '__main__':
    current_round = cartolafc.Api().mercado().rodada_atual
    current_year = cartolafc.Api().mercado().fechamento.year
    models = parse_models()
    players = get_players()
    history = read_history(current_year, current_round)

    lines = {}

    for player in players:
        lines['ata'] = [build_player_line(player[0], current_round) for player in players if player[1] == 'ata']
        lines['mei'] = [build_player_line(player[0], current_round) for player in players if player[1] == 'mei']
        lines['zag'] = [build_player_line(player[0], current_round) for player in players if player[1] == 'zag']
        lines['lat'] = [build_player_line(player[0], current_round) for player in players if player[1] == 'lat']
        lines['gol'] = [build_player_line(player[0], current_round) for player in players if player[1] == 'gol']

    lines['ata'] = [line for line in lines['ata'] if line is not None]
    lines['mei'] = [line for line in lines['mei'] if line is not None]
    lines['zag'] = [line for line in lines['zag'] if line is not None]
    lines['lat'] = [line for line in lines['lat'] if line is not None]
    lines['gol'] = [line for line in lines['gol'] if line is not None]

    suggestions = {}

    for model in models:
        position = get_model_position(model)
        scores = predict_players_score(lines[position], model)
        suggestions[model] = get_suggestions(scores, position)

    coach_suggestions = suggest_coach()
