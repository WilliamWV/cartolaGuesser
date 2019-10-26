import argparse
import random
import os

log = {}
scores = {}
results = {}
teams = {}

ROUNDS = 38
ATTRIBUTES = 18
DECAY = 0.8


class FileReader:
    A = 0
    CA = 3
    CV = 4
    DD = 6
    DP = 7
    FC = 8
    FD = 9
    FF = 10
    FS = 11
    FT = 12
    G = 13
    GC = 14
    GS = 15
    IMP = 16
    PE = 18
    PP = 19
    RB = 26
    SG = 28

    PLAYER_ID = 2
    YEAR = 30
    ROUND = 27
    PLAYED_THIS_ROUND = 20
    TEAM = 5
    HOME_SCORE = 71
    AWAY_SCORE = 67

    PONTOS = 21
    PRECO = 24
    POS = 23

    def __init__(self, file_name):
        print("Reading file: " + file_name)
        self.file = open(file_name, 'r', encoding='utf-8')
        self.file.readline()  # read headers

    def build_log(self):
        global log, teams
        lines = [line.split(',') for line in self.file.readlines()]
        for line in lines:

            player_id = line[self.PLAYER_ID]
            year = line[self.YEAR]
            round_num = int(line[self.ROUND])
            played_this_round = line[self.PLAYED_THIS_ROUND].find('True') == 0
            team = line[self.TEAM]
            player_team = line[-1]
            home_score = float(line[self.HOME_SCORE])
            away_score = float(line[self.AWAY_SCORE])

            if player_team.find('home') >= 0:
                team_score = home_score
                adv_score = away_score
            else:
                team_score = away_score
                adv_score = home_score

            if teams.get(team) is None:
                teams[team] = {}
            if teams[team].get(year) is None:
                teams[team][year] = {}
            if teams[team][year].get(round_num) is None:
                teams[team][year][round_num] = {'goals_scored': team_score, 'goals_taken': adv_score}

            if log.get(player_id) is None:
                log[player_id] = {}
            if log[player_id].get(year) is None:
                log[player_id][year] = {}
            if log[player_id][year].get(round_num) is None:
                log[player_id][year][round_num] = []

            if played_this_round and len(log[player_id][year][round_num]) == 0:
                for feature in [self.A, self.CA, self.CV, self.DD, self.DP, self.FC, self.FD, self.FF, self.FS,
                                self.FT, self.G, self.GC, self.GS, self.IMP, self.PE, self.PP, self.RB, self.SG]:
                    log[player_id][year][round_num].append(float(line[feature]))

                log[player_id][year][round_num].append(team)
                log[player_id][year][round_num].append(float(line[self.PONTOS]))
                log[player_id][year][round_num].append(line[self.POS])
                log[player_id][year][round_num].append(float(line[self.PRECO]))
        self.file.close()


# noinspection PyAttributeOutsideInit
class DirReader:

    def __init__(self, dir_name):
        temp_files = os.listdir(dir_name)
        self.year = dir_name[5:9]
        self.files = [dir_name + '/' + tf for tf in temp_files]

    def discover_headers(self, file):
        headers = file.readline().replace("\"", '').replace('\n', '').split(',')
        self.A = headers.index('A')
        self.CA = headers.index('CA')
        self.CV = headers.index('CV')
        self.DD = headers.index('DD')
        if 'DP' in headers:
            self.DP = headers.index('DP')
        else:
            self.DP = -1
        self.FC = headers.index('FC')
        self.FD = headers.index('FD')
        self.FF = headers.index('FF')
        self.FS = headers.index('FS')
        self.FT = headers.index('FT')
        self.G = headers.index('G')
        if 'GC' in headers:
            self.GC = headers.index('GC')
        else:
            self.GC = -1
        self.GS = headers.index('GS')
        self.IMP = headers.index('I')
        self.PE = headers.index('PE')
        if 'PP' in headers:
            self.PP = headers.index('PP')
        else:
            self.PP = -1
        self.RB = headers.index('RB')
        self.SG = headers.index('SG')

        self.PLAYER_ID = headers.index('atletas.atleta_id')
        self.TEAM = headers.index('atletas.clube.id.full.name')
        self.PONTOS = headers.index('atletas.pontos_num')
        self.PRECO = headers.index('atletas.preco_num')
        self.POS = headers.index('atletas.posicao_id')

    def build_log(self):
        global log, teams
        year_log = {}
        team_log = {}
        for file in self.files:
            file_handler = open(file, 'r', encoding='utf-8')
            print('Reading file: ' + file)
            self.discover_headers(file_handler)
            lines = [line.replace("\"", '').replace('\n', '').split(',') for line in file_handler.readlines()]
            round_num = int(file[file.rfind('-') + 1:file.rfind('.')])
            playing_teams = []
            team_goals = {}

            for line in lines:

                player_id = line[self.PLAYER_ID]
                played_this_round = line.count(',NA') < 18
                team = line[self.TEAM]

                if team not in playing_teams:
                    playing_teams.append(team)
                    team_goals[team] = [0.0, 0.0]

                if year_log.get(player_id) is None:
                    year_log[player_id] = {}
                if year_log[player_id].get(self.year) is None:
                    year_log[player_id][self.year] = {}
                if year_log[player_id][self.year].get(round_num) is None:
                    year_log[player_id][self.year][round_num] = []

                if played_this_round and len(year_log[player_id][self.year][round_num]) == 0:
                    for feature in [self.A, self.CA, self.CV, self.DD, self.DP, self.FC, self.FD, self.FF, self.FS,
                                    self.FT, self.G, self.GC, self.GS, self.IMP, self.PE, self.PP, self.RB, self.SG]:
                        if feature == -1 or line[feature] == 'NA':
                            feature_val = 0.0
                        else:
                            feature_val = float(line[feature])

                        year_log[player_id][self.year][round_num].append(feature_val)

                    if line[self.G] != 'NA':
                        team_goals[team][0] += float(line[self.G])
                    if line[self.GS] != 'NA':
                        team_goals[team][1] += float(line[self.GS])

                    year_log[player_id][self.year][round_num].append(team)
                    year_log[player_id][self.year][round_num].append(float(line[self.PONTOS]))
                    year_log[player_id][self.year][round_num].append(line[self.POS])
                    year_log[player_id][self.year][round_num].append(float(line[self.PRECO]))

            for team in team_goals:
                if team_log.get(team) is None:
                    team_log[team] = {}
                if team_log[team].get(self.year) is None:
                    team_log[team][self.year] = {}
                if team_log[team][self.year].get(round_num) is None:
                    team_log[team][self.year][round_num] = {'goals_scored': team_goals[team][0],
                                                            'goals_taken': team_goals[team][1]}

            file_handler.close()

        for player_id in year_log:
            for year in year_log[player_id]:
                rounds = list(year_log[player_id][year].keys())
                rounds.sort()
                last_round = 0
                for round_num in rounds:
                    if log.get(player_id) is None:
                        log[player_id] = {}
                    if log[player_id].get(year) is None:
                        log[player_id][year] = {}
                    if log[player_id][year].get(round_num) is None:
                        log[player_id][year][round_num] = []
                    if last_round == 0:
                        log[player_id][year][round_num] = year_log[player_id][year][round_num]
                    else:
                        log[player_id][year][round_num] = \
                            [
                                year_log[player_id][year][round_num][i] -
                                year_log[player_id][year][last_round][i]
                                for i in range(len(year_log[player_id][year][round_num]) - 4)
                            ]
                        for item in year_log[player_id][year][round_num][-4:]:
                            log[player_id][year][round_num].append(item)
                    last_round = round_num

        for team in team_log:
            for year in team_log[team]:
                rounds = list(team_log[team][year].keys())
                rounds.sort()
                last_round = 0
                for round_num in rounds:
                    if teams.get(team) is None:
                        teams[team] = {}
                    if teams[team].get(year) is None:
                        teams[team][year] = {}
                    if teams[team][year].get(round_num) is None:
                        teams[team][year][round_num] = {}
                    if last_round == 0:
                        teams[team][year][round_num] = team_log[team][year][round_num]
                    else:
                        teams[team][year][round_num] = {
                            'goals_scored': team_log[team][year][round_num]['goals_scored'] -
                                            team_log[team][year][last_round]['goals_scored'],
                            'goals_taken': team_log[team][year][round_num]['goals_taken'] -
                                           team_log[team][year][last_round]['goals_taken']
                        }
                    last_round = round_num


def parse_input():
    parser = argparse.ArgumentParser(description='Receive file to extract data')
    parser.add_argument('-d', '--dir', required=True, type=str,
                        help='Directory with data')

    args = parser.parse_args()

    kids = os.listdir(args.dir)
    kids = [args.dir + '/' + k for k in kids]

    file_names = [f for f in kids if os.path.isfile(f)]
    dir_names = [d for d in kids if os.path.isdir(d)]

    return file_names, dir_names


def build_log(file_names, dir_names):
    for d in dir_names:
        d_handler = DirReader(d)
        d_handler.build_log()
    for f in file_names:
        f_handler = FileReader(f)
        f_handler.build_log()


def build_line(player, year, curr_round):
    if scores.get(player) is None:
        scores[player] = {}
    if scores[player].get(year) is None:
        scores[player][year] = {}
        scores[player][year][0] = [0] * (ATTRIBUTES + 1)

    scores[player][year][curr_round] = [0] * (ATTRIBUTES + 1)

    for i in range(ATTRIBUTES):
        if log[player][year].get(curr_round) is not None and len(log[player][year][curr_round]) > 0:
            scores[player][year][curr_round][i] = scores[player][year][curr_round - 1][i] * DECAY + \
                                                  log[player][year][curr_round][i]
        else:
            scores[player][year][curr_round][i] = scores[player][year][curr_round - 1][i] * DECAY

    if log[player][year].get(curr_round) is not None and len(log[player][year][curr_round]) > 0:
        scores[player][year][curr_round][-1] = scores[player][year][curr_round - 1][-1] * DECAY + \
                                               log[player][year][curr_round][-1]
    else:
        scores[player][year][curr_round][-1] = scores[player][year][curr_round - 1][-1] * DECAY


def process_team_logs():
    for team in teams:
        for year in teams[team]:
            if teams[team][year].get(0) is None:
                teams[team][year][0] = {'goals_scored': 0, 'goals_taken': 0}

            teams[team][year][0]['acc_goals'] = 0.0
            teams[team][year][0]['tak_goals'] = 0.0

            for roundNum in range(1, ROUNDS):
                if teams[team][year].get(roundNum) is None:
                    teams[team][year][roundNum] = {'goals_scored': 0, 'goals_taken': 0}

                teams[team][year][roundNum]['acc_goals'] = \
                    DECAY * teams[team][year][roundNum - 1]['acc_goals'] + \
                    teams[team][year][roundNum]['goals_scored']
                teams[team][year][roundNum]['tak_goals'] = \
                    DECAY * teams[team][year][roundNum - 1]['tak_goals'] + \
                    teams[team][year][roundNum]['goals_taken']


def process_player_logs():
    for player in log:
        years_played = list(log[player].keys())
        years_played.sort()
        for year in years_played:
            for roundNum in range(1, ROUNDS):
                build_line(player, year, roundNum)


def get_player_team(player, year_target, roundNum_target):
    player_teams = []
    for year in log[player]:
        for roundNum in log[player][year]:
            if year < year_target or (year == year_target and roundNum <= roundNum_target):
                if log[player][year].get(roundNum) is not None and len(log[player][year][roundNum]) > 0:
                    if log[player][year][roundNum][-4] not in player_teams:
                        player_teams.append((log[player][year][roundNum][-4], year, roundNum))

    if len(player_teams) == 0:
        return None
    else:
        curr_team = player_teams[0]
        for team in player_teams:
            if team[1] > curr_team[1] or (team[1] == curr_team[1] and team[2] > curr_team[2]):
                curr_team = team
        return curr_team[0]


def write_data_to_file():
    out_file = open('scoresExtractedData.csv', 'w')

    out_file.write(
        'PlayerID,Year,Round,Team,A,CA,CV,DD,DP,FC,FD,FF,FS,FT,G,GC,GS,I,PE,PP,RB,SG,PNT,pos,price,proGoals,'
        'consGoals,realScore\n'
    )

    for player in scores:
        for year in log[player]:
            for roundNum in range(ROUNDS):
                out_file.write(str(player) + ',' + str(year) + ',' + str(roundNum))
                if log[player][year].get(roundNum + 1) is not None and len(log[player][year][roundNum + 1]) > 0:
                    team = log[player][year][roundNum + 1][-4]
                elif log[player][year].get(roundNum) is not None and len(log[player][year][roundNum]) > 0:
                    team = log[player][year][roundNum][-4]
                else:
                    team = get_player_team(player, year, roundNum)
                out_file.write(','+str(team))
                for item in scores[player][year][roundNum]:
                    out_file.write(',' + '{:.2f}'.format(item))
                if log[player][year].get(roundNum + 1) is not None and len(log[player][year][roundNum + 1]) > 0:
                    out_file.write(',' + str(log[player][year][roundNum + 1][-2]) + ',' + str(
                        log[player][year][roundNum + 1][-1]) +
                                   ',' + '{:.2f}'.format(teams[team][year][roundNum]['acc_goals']) + ',' +
                                   '{:.2f}'.format(teams[team][year][roundNum]['tak_goals']) + ',' +
                                   str(log[player][year][roundNum + 1][-3]))
                elif log[player][year].get(roundNum) is not None and len(log[player][year][roundNum]) > 0:
                    out_file.write(',NA,NA,{:.2f}'.format(teams[team][year][roundNum]['acc_goals']) + ',' +
                                   '{:.2f}'.format(teams[team][year][roundNum]['tak_goals']) + ',NA')
                else:
                    if team is None or teams[team].get(year) is None:
                        out_file.write(',NA,NA,0.0,0.0,NA')
                    else:
                        out_file.write(',NA,NA,{:.2f}'.format(teams[team][year][roundNum]['acc_goals']) + ',' +
                                       '{:.2f}'.format(teams[team][year][roundNum]['tak_goals']) + ',NA')

                out_file.write('\n')
    out_file.close()


def filter_file():
    in_file = open('scoresExtractedData.csv', 'r')
    out_file = open('scoresExtractedFiltered.csv', 'w')
    for line in in_file.readlines():
        if line.find('NA,') < 0:
            out_file.write(line)
    in_file.close()
    out_file.close()


def split_file():
    in_file = open('scoresExtractedFiltered.csv', 'r')
    gol_file = open('scoresGol.csv', 'w')
    zag_file = open('scoresZag.csv', 'w')
    lat_file = open('scoresLat.csv', 'w')
    mei_file = open('scoresMei.csv', 'w')
    ata_file = open('scoresAta.csv', 'w')

    for out_file in [gol_file, zag_file, lat_file, mei_file, ata_file]:
        out_file.write(
            'PlayerID,Year,Round,Team,A,CA,CV,DD,DP,FC,FD,FF,FS,FT,G,GC,GS,I,PE,PP,RB,SG,PNT,pos,price,proGoals,'
            'consGoals,realScore\n'
        )

    for line in in_file.readlines():
        if line.find('gol') >= 0:
            gol_file.write(line)
        elif line.find('zag') >= 0:
            zag_file.write(line)
        elif line.find('lat') >= 0:
            lat_file.write(line)
        elif line.find('mei') >= 0:
            mei_file.write(line)
        elif line.find('ata') >= 0:
            ata_file.write(line)


def write_nn_file(in_file_path):
    in_file = open(in_file_path, 'r')
    train_file = open('train/' + in_file_path.replace('.csv', '') + '_train.csv', 'w')
    test_file = open('test/' + in_file_path.replace('.csv', '') + '_test.csv', 'w')
    train_percent = 0.7
    first_line = True
    for line in in_file.readlines():
        fourth_comma_pos = line.find(',', line.find(',', line.find(',', line.find(',') + 1) + 1) + 1)
        line = line.replace('zag,', '').replace('mei,', '').replace('lat,', '').replace('gol,', '') \
            .replace('ata,', '').replace('pos,', '')
        if first_line:
            train_file.write(line[fourth_comma_pos + 1:])
            test_file.write(line[fourth_comma_pos + 1:])
            first_line = False
        else:
            if random.random() <= train_percent:
                train_file.write(line[fourth_comma_pos + 1:])
            else:
                test_file.write(line[fourth_comma_pos + 1:])


if __name__ == '__main__':

    print("Parsing input")
    files, dirs = parse_input()
    print("Building log")
    build_log(files, dirs)
    print("Processing team log")
    process_team_logs()
    print("Processing player log")
    process_player_logs()
    print("Writing data to file")
    write_data_to_file()
    print("Filtering file")
    filter_file()
    print("Splitting file")
    split_file()
    for ans_file in ['scoresGol.csv', 'scoresZag.csv', 'scoresLat.csv', 'scoresMei.csv', 'scoresAta.csv']:
        write_nn_file(ans_file)
