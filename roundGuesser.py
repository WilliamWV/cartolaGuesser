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


def get_player(player_id):
    player = [player for player in cartolafc.Api().mercado_atletas() if player.id == player_id]
    if len(player) != 1:
        print('ERROR: could not find player ' + str(player_id))
    else:
        return player[0]


def read_model(model_path):
    return tf.keras.models.load_model(model_path)


def parse_models():
    global email, password
    parser = argparse.ArgumentParser(description='Receive models to use on prediction')
    parser.add_argument('-a', '--ata_model', required=False)
    parser.add_argument('-m', '--mei_model', required=False)
    parser.add_argument('-z', '--zag_model', required=False)
    parser.add_argument('-l', '--lat_model', required=False)
    parser.add_argument('-g', '--gol_model', required=False)

    parser.add_argument('-d', '--model_dir', required=False, help='Path to models directory')

    parser.add_argument('-e', '--email', required=True,
                        help='Registered email on cartola, used to get price of the players')
    parser.add_argument('-p', '--password', required=True,
                        help='Registered password on cartola, used to get price of the players')

    args = parser.parse_args()
    email = args.email
    password = args.password
    mod = []

    if args.ata_model is not None or args.mei_model is not None or args.zag_model is not None or \
            args.lat_model is not None or args.gol_model is not None:
        if args.ata_model is None or args.mei_model is None or args.zag_model is None or \
                args.lat_model is None or args.gol_model is None:
            print("You may either enter path to all models (-a, -m, -z, -l and -g) or to the model directory (-d)")
            exit()
        else:
            ata_model = read_model(args.ata_model)
            mei_model = read_model(args.mei_model)
            zag_model = read_model(args.zag_model)
            lat_model = read_model(args.lat_model)
            gol_model = read_model(args.gol_model)

            model_names[ata_model] = 'ata'
            model_names[mei_model] = 'mei'
            model_names[zag_model] = 'zag'
            model_names[lat_model] = 'lat'
            model_names[gol_model] = 'gol'

            mod = [ata_model, mei_model, zag_model, lat_model, gol_model]

    elif args.model_dir is not None:
        for item in os.listdir(args.model_dir):
            print('Reading ' + str(item))
            inp_model = read_model(args.model_dir + '/' + item)
            model_names[inp_model] = item.replace('.h5', '')
            mod.append(inp_model)

    else:
        print("You may either enter path to all models (-a, -m, -z, -l and -g) or to the model directory (-d)")
        exit()

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


def build_player_line(player_id, round_num, api):
    global history

    player_row = history.loc[history['PlayerID'] == player_id]
    if len(player_row) > 1:
        print("ERROR: Multiple lines of the same player")
        return None
    elif len(player_row) == 0:
        return None
    else:
        player_team = player_row.values[0][3]
        player_vals = player_row.values[0][4:-1]
        player_line = np.concatenate([player_vals[:-6], player_vals[-5:]])
        price = [
            round_score.preco
            for round_score in api.pontuacao_atleta(player_id)
            if round_score.rodada_id == round_num - 1
        ]
        if len(price) != 1:
            print("ERROR: could not get the price of player " + str(player_id))
            return None
        else:
            player_line[-6] = price[0]
            return player_line, player_id, player_team


def predict_players_score(player_lines, trained_model):
    players_scores = {}
    for player_line in player_lines:
        line = player_line[0]
        player_id = player_line[1]
        player_team = player_line[2]
        tensor = tf.convert_to_tensor(line.reshape((1, 24)), np.float32)
        score = trained_model.predict(tensor).tolist()[0][0]
        players_scores[player_id] = score
        if teams_score.get(player_team) is None:
            teams_score[player_team] = 0.0

        teams_score[player_team] += score
    return players_scores


def suggest_coach():
    suggested_teams = [c for c in teams_score if teams_score[c] == max(teams_score.values())]
    score = teams_score[suggested_teams[0]] / (11.0 * (len(model_names) / 5))
    all_players = cartolafc.Api().mercado_atletas()
    coachs = [c for c in all_players if c.posicao[2] == 'tec']
    return [c.id for c in coachs if c.clube.nome in suggested_teams][0], score


def get_highest_scores(players_scores, num_players):
    items = list(players_scores.items())
    score_vals = list(players_scores.values())
    arr = np.array(score_vals)
    highest_indexes = arr.argsort()[-num_players:][::-1]
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


def build_team(models_suggestions, formation, ata_model, mei_model, zag_model, lat_model, gol_model):
    team = {
        'gol': models_suggestions[gol_model],
        'lat': models_suggestions[lat_model][:formation[0]],
        'zag': models_suggestions[zag_model][:formation[1]],
        'mei': models_suggestions[mei_model][:formation[2]],
        'ata': models_suggestions[ata_model][:formation[3]]
    }
    team_score = sum([sum([score[1] for score in pos_players]) for pos_players in team.values()])

    return team, team_score, formation


def get_most_voteds(vote_list, num_classified):
    vote_log = {}
    for item in vote_list:
        if vote_log.get(item) is None:
            vote_log[item] = 1
        else:
            vote_log[item] += 1

    votes_vals = list(vote_log.values())
    arr = np.array(votes_vals)
    highest_indexes = arr.argsort()[-num_classified:][::-1]
    voted_items = list(vote_log.keys())
    return [voted_items[ind] for ind in highest_indexes]


def vote_team(models_suggestions, formation, ata_models, mei_models, zag_models, lat_models, gol_models):
    voted_suggestions = {
        'gol': [],
        'lat': [],
        'zag': [],
        'mei': [],
        'ata': []
    }
    for g_model in gol_models:
        voted_suggestions['gol'].extend(models_suggestions[g_model])
    for l_model in lat_models:
        voted_suggestions['lat'].extend(models_suggestions[l_model])
    for z_model in zag_models:
        voted_suggestions['zag'].extend(models_suggestions[z_model])
    for m_model in mei_models:
        voted_suggestions['mei'].extend(models_suggestions[m_model])
    for a_model in ata_models:
        voted_suggestions['ata'].extend(models_suggestions[a_model])

    gol_suggestions = get_most_voteds(voted_suggestions['gol'], max_players_same_pos['gol'])
    lat_suggestions = get_most_voteds(voted_suggestions['lat'], max_players_same_pos['lat'])
    zag_suggestions = get_most_voteds(voted_suggestions['zag'], max_players_same_pos['zag'])
    mei_suggestions = get_most_voteds(voted_suggestions['mei'], max_players_same_pos['mei'])
    ata_suggestions = get_most_voteds(voted_suggestions['ata'], max_players_same_pos['ata'])

    team = {
        'gol': gol_suggestions,
        'lat': lat_suggestions[:formation[0]],
        'zag': zag_suggestions[:formation[1]],
        'mei': mei_suggestions[:formation[2]],
        'ata': ata_suggestions[:formation[3]]
    }
    team_score = sum([sum([score[1] for score in pos_players]) for pos_players in team.values()])

    return team, team_score, formation


def suggest_team(models_suggestions):
    team_formations = [
        (0, 3, 4, 3),  # 3-4-3
        (0, 3, 5, 2),  # 3-5-2
        (2, 2, 3, 3),  # 4-3-3
        (2, 2, 4, 2),  # 4-4-2
        (2, 2, 5, 1),  # 4-5-1
        (2, 3, 3, 2),  # 5-3-2
        (2, 3, 4, 1)  # 5-4-1
    ]

    ata_models = [sug_model for sug_model in models_suggestions.keys() if model_names[sug_model].find('ata') >= 0]
    mei_models = [sug_model for sug_model in models_suggestions.keys() if model_names[sug_model].find('mei') >= 0]
    zag_models = [sug_model for sug_model in models_suggestions.keys() if model_names[sug_model].find('zag') >= 0]
    lat_models = [sug_model for sug_model in models_suggestions.keys() if model_names[sug_model].find('lat') >= 0]
    gol_models = [sug_model for sug_model in models_suggestions.keys() if model_names[sug_model].find('gol') >= 0]

    if len(ata_models) == 1 and len(mei_models) == 1 and len(zag_models) == 1 and len(lat_models) == 1 and len(
            gol_models) == 1:
        ata_model = ata_models[0]
        mei_model = mei_models[0]
        zag_model = zag_models[0]
        lat_model = lat_models[0]
        gol_model = gol_models[0]
        possible_teams = [
            build_team(models_suggestions, formation, ata_model, mei_model, zag_model, lat_model, gol_model) for
            formation in team_formations]
        max_score = max([team[1] for team in possible_teams])
        optimal_team = [team for team in possible_teams if team[1] == max_score][0]
        return optimal_team
    else:
        possible_teams = [
            vote_team(models_suggestions, formation, ata_models, mei_models, zag_models, lat_models, gol_models) for
            formation in team_formations]
        max_score = max([team[1] for team in possible_teams])

        optimal_team = [team for team in possible_teams if team[1] == max_score][0]
        return optimal_team


def print_formation(formation):
    print("\nEsquema tatico:")
    print(str(formation[0] + formation[1]) + '-' + str(formation[2]) + '-' + str(formation[3]))


def choose_cap(team):
    team_players = []
    team_players.extend(team['gol'])
    team_players.extend(team['lat'])
    team_players.extend(team['zag'])
    team_players.extend(team['mei'])
    team_players.extend(team['ata'])

    cap = team['gol'][0]
    for player in team_players:
        if player[1] > cap[1]:
            cap = player

    return cap


def print_team(team_to_print):

    print("\nGol: ")
    for suggested_player in team_to_print['gol']:
        player = get_player(suggested_player[0])
        print(player.apelido + ': {:.2f}'.format(suggested_player[1]))

    print("\nLat: ")
    for suggested_player in team_to_print['lat']:
        player = get_player(suggested_player[0])
        print(player.apelido + ': {:.2f}'.format(suggested_player[1]))

    print("\nZag: ")
    for suggested_player in team_to_print['zag']:
        player = get_player(suggested_player[0])
        print(player.apelido + ': {:.2f}'.format(suggested_player[1]))

    print("\nMei: ")
    for suggested_player in team_to_print['mei']:
        player = get_player(suggested_player[0])
        print(player.apelido + ': {:.2f}'.format(suggested_player[1]))

    print("\nAta: ")
    for suggested_player in team_to_print['ata']:
        player = get_player(suggested_player[0])
        print(player.apelido + ': {:.2f}'.format(suggested_player[1]))


def save_suggestion(team, year, roundNum):
    file_name = 'suggestion/' + str(year) + '/' + str(roundNum) + '.txt'
    file = open(file_name, 'w')
    gols = [get_player(player[0]) for player in team[0]['gol']]
    lats = [get_player(player[0]) for player in team[0]['lat']]
    zags = [get_player(player[0]) for player in team[0]['zag']]
    meis = [get_player(player[0]) for player in team[0]['mei']]
    atas = [get_player(player[0]) for player in team[0]['ata']]
    file.write('Suggestion to round ' + str(roundNum) + ' of ' + str(year) + '\n\n')
    file.write('Foramation: ' + str(team[2][0] + team[2][1]) + '-' + str(team[2][2]) + '-' + str(team[2][3]) + '\n')

    file.write('\nGol: \n')
    for player in gols:
        file.write(
            "\tId = " + str(player.id) + "\tNickname = " + str(player.apelido) + "\tTeam = " + str(player.clube.nome) + '\n')

    file.write('\nLat: \n')
    for player in lats:
        file.write(
            "\tId = " + str(player.id) + "\tNickname = " + str(player.apelido) + "\tTeam = " + str(player.clube.nome) + '\n')

    file.write('\nZag: \n')
    for player in zags:
        file.write(
            "\tId = " + str(player.id) + "\tNickname = " + str(player.apelido) + "\tTeam = " + str(player.clube.nome) + '\n')

    file.write('\nMei: \n')
    for player in meis:
        file.write(
            "\tId = " + str(player.id) + "\tNickname = " + str(player.apelido) + "\tTeam = " + str(player.clube.nome) + '\n')

    file.write('\nAta: \n')
    for player in atas:
        file.write(
            "\tId = " + str(player.id) + "\tNickname = " + str(player.apelido) + "\tTeam = " + str(player.clube.nome) + '\n')


if __name__ == '__main__':
    api = cartolafc.Api()
    mercado = api.mercado()
    current_round = mercado.rodada_atual
    current_year = mercado.fechamento.year

    print("Parsing models")
    models = parse_models()
    print("Setting credentials")
    api.set_credentials(email, password)

    print("Running suggestions for year " + str(current_year) + " and round " + str(current_round))
    print("Getting players of the round")
    players = get_players()
    print("Found " + str(len(players)) + " possible players")
    print("Calculating history of this round's players")
    history = read_history(current_year, current_round)

    lines = {}
    print("Building player information for this round")
    lines['ata'] = [line for line in [build_player_line(player[0], current_round, api) for player in players if player[1] == 'ata'] if line is not None]
    lines['mei'] = [line for line in [build_player_line(player[0], current_round, api) for player in players if player[1] == 'mei'] if line is not None]
    lines['zag'] = [line for line in [build_player_line(player[0], current_round, api) for player in players if player[1] == 'zag'] if line is not None]
    lines['lat'] = [line for line in [build_player_line(player[0], current_round, api) for player in players if player[1] == 'lat'] if line is not None]
    lines['gol'] = [line for line in [build_player_line(player[0], current_round, api) for player in players if player[1] == 'gol'] if line is not None]


    print("Predicting players score")
    suggestions = {}
    for model in models:
        print("Predicting for model " + str(model_names[model]))
        position = get_model_position(model)
        scores = predict_players_score(lines[position], model)
        suggestions[model] = get_suggestions(scores, position)

    print("Calculating suggested team")
    team = suggest_team(suggestions)
    coach_suggestion = suggest_coach()

    print("Team suggestion: ")
    print_formation(team[2])
    print_team(team[0])
    cap = choose_cap(team[0])
    print('Cap: ' + [player.apelido for player in api.mercado_atletas() if player.id == cap[0]][0])
    print('Coach suggestion: ', end='')
    print([player.apelido for player in api.mercado_atletas() if player.id == coach_suggestion[0]][0] + ':{:.2f}'.format(coach_suggestion[1]))
    print("Expected score: {:.2f}".format(team[1] + cap[1] + coach_suggestion[1]))
    print("Saving suggestion to file")
    save_suggestion(team, current_year, current_round)
