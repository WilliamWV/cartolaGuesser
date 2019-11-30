import cartolafc
import os

api = cartolafc.Api()
mercado = api.mercado()
current_round = mercado.rodada_atual
current_year = mercado.fechamento.year

# A dictionary with previous round scouts for all players
# a player scout is a dictionary associating all non-zero features with its value

scout_items = ['A', 'CA', 'CV', 'DD', 'DP', 'FC', 'FD', 'FF', 'FS', 'FT', 'G', 'GC', 'GS', 'I', 'PE', 'PP', 'RB', 'SG']


def mount_current_scout(atletas):
    dirs = 'scouts/' + str(current_year)
    file_name = dirs + '/' + str(current_round) + '.txt'
    if not os.path.exists(dirs):
        os.makedirs(dirs)
    file = open(file_name, 'w')
    file.write('ID,A,CA,CV,DD,DP,FC,FD,FF,FS,FT,G,GC,GS,I,PE,PP,RB,SG\n')
    for atleta in atletas:
        file.write(str(atleta.id))
        for item in ['A', 'CA', 'CV', 'DD', 'DP', 'FC', 'FD', 'FF', 'FS', 'FT', 'G', 'GC',' GS', 'I', 'PE', 'PP', 'RB', 'SG']:
            try:
                value = atleta.scout[item]
                file.write(',{:.1f}'.format(value))
            except KeyError:
                file.write(',0.0')
        file.write('\n')


def fill_gaps(player):
    round_scout = {}
    new_scout = player.scout
    for item in scout_items:
        if new_scout.get(item) is not None:
            round_scout[item] = new_scout[item]
        else:
            round_scout[item] = 0.0
    return player.id, round_scout


def update_match_file():
    matches = api.partidas(current_round - 1)
    file = open('matches.csv', 'a')
    for match in matches:
        home_team = match.clube_casa.nome
        away_team = match.clube_visitante.nome
        if home_team == 'Athlético-PR':
            home_team = 'Atlético-PR'
        if away_team == 'Athlético-PR':
            away_team = 'Atlético-PR'

        home_goals = float(match.placar_casa)
        away_goals = float(match.placar_visitante)
        file.write(str(current_year) + ',' + str(current_round-1) + ',' + home_team + ',' + away_team +
                   ',' + str(home_goals) + ',' + str(away_goals) + '\n')


def update_history_files(round_scouts, players):
    file_name = 'data/' + str(current_year) + '/rodada-' + str(current_round-1) + '.csv'
    file = open(file_name, 'w', encoding='utf-8')

    file.write('atletas.atleta_id,atletas.clube.id.full.name,atletas.pontos_num,atletas.preco_num,atletas.posicao_id')
    for item in scout_items:
        file.write(','+item)
    file.write('\n')

    for player in players:
        player_id = player.id
        team = player.clube.nome
        if team == 'Athlético-PR':
            team = 'Atlético-PR'
        pos = player.posicao.abreviacao
        preco = 0.0
        points = player.pontos
        line = [player_id, team, points, preco, pos]
        for item in scout_items:
            line.append(round_scouts[player_id][item])
        file.write(str(line[0]))
        for item in line[1:]:
            file.write(','+str(item))
        file.write('\n')


if __name__ == '__main__':
    print("Reading available players")
    players = api.mercado_atletas()
    print("Mounting players scout")
    mount_current_scout(players)
    print("Mounting round scouts")
    round_scouts = dict([fill_gaps(player) for player in players])
    print("Updating history file")
    update_history_files(round_scouts, players)
    print("Updating match file")
    update_match_file()

