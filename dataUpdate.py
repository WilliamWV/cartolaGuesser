import cartolafc
import os

api = cartolafc.Api()
mercado = api.mercado()
current_round = mercado.rodada_atual
current_year = mercado.fechamento.year

# A dictionary with previous round scouts for all players
# a player scout is a dictionary associating all non-zero features with its value

previous_scout = {}
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


def read_previous_scout():
    previous_round = current_round - 1
    if (str(previous_round) + '.txt') in os.listdir('scouts/' + str(current_year)):
        file = open('scouts/' + str(current_year) + str(previous_round) + '.txt', 'r')
        _ = file.readline()
        for line in file.readlines():
            items = line.split(',')
            player_id = int(items[0])
            previous_scout[player_id] = {}
            for i in range(len(scout_items)):
                previous_scout[player_id][scout_items[i]] = items[i+1]


def get_round_diff(player, new_scout):
    pass


def update_data(player):
    scouts = player.scout
    get_round_diff(player.id, scouts)


if __name__ == '__main__':
    read_previous_scout()
    atletas = api.mercado_atletas()
    mount_current_scout(atletas)

