import argparse
import random
import os

log = {}
scores = {}
results = {}
matches = {}
teams = {}

ROUNDS = 38
ATTRIBUTES = 18


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
        global log
        lines = [line.split(',') for line in self.file.readlines()]
        for line in lines:

            player_id = line[self.PLAYER_ID]
            year = line[self.YEAR]
            round_num = int(line[self.ROUND])
            played_this_round = line[self.PLAYED_THIS_ROUND].find('True') == 0
            team = line[self.TEAM]

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
        global log
        year_log = {}
        for file in self.files:
            file_handler = open(file, 'r', encoding='utf-8')
            print('Reading file: ' + file)
            self.discover_headers(file_handler)
            lines = [line.replace("\"", '').replace('\n', '').split(',') for line in file_handler.readlines()]
            round_num = int(file[file.rfind('-') + 1:file.rfind('.')])

            for line in lines:

                player_id = line[self.PLAYER_ID]
                played_this_round = line.count(',NA') < 18
                team = line[self.TEAM]

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

                    year_log[player_id][self.year][round_num].append(team)
                    year_log[player_id][self.year][round_num].append(float(line[self.PONTOS]))
                    year_log[player_id][self.year][round_num].append(line[self.POS])
                    year_log[player_id][self.year][round_num].append(float(line[self.PRECO]))

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


def factorial(n):
    if n < 0:
        print('ERROR: attempt to get factorial of negative number')
        exit()
    if n == 1 or n == 0:
        return 1
    else:
        return n * factorial(n - 1)


def combinations(n, k):
    return factorial(n) / (factorial(k) * factorial(n - k))


def round_forecast(attribute_type, team, player, year, round_num, attribute):
    """
        In an attempt to provide a better representation of what is expected from a player in each attribute, the
        following formulation was developed:

        The value won't consider only the previous value and decay it as done previously on nn_input_value function
        the formulation proposed here consider this value to be a weighted sum of previous rounds attributes and the
        weights are determined by the decreasing part of a parabola or by a decreasing line, so these distributions
        are represented by the following constants

            R = Number of previous rounds to consider
            F = first derivative on the initial point of the distribution
            S = second derivative of the distribution (zero if is a line)
            W = initial weight

        These constants may be subject to the following constraints in order to the weights be decreasing

            F < 0                   } Once the weights shall be decreasing
            F + (R-1) * S < 0       } so the newer results are more important
            R >= 1                  Must consider at least one past round

        Considering this, the following equations can be derived:

            * W_i+1 = W_i + F_i                                                     (Eq. 1)
                (where W_i is the weight of previous ith round and F_i is the first derivative associated with W_i)
            * F_i+1 = F_i + S                                                       (Eq. 2)
                (same idea of the above, but S is constant to all rounds)
            * V = Sum(i = 1..R, W_i * x_i)                                          (Eq. 3)
                (where V is the value returned by this function, and x_i is the log of the analised attribute on
                the ith round)
            * W_i+1 = W_i + i * S + F                                               (Eq. 4)
                (from Eq. 1 and Eq. 2)
            * W_i = W + (i-1) * (i-2) / 2 * S + (i - 1) * F                         (Eq. 5)
                (from Eq. 4 recursively expanded)
            * V = Sum(i = 1..R, (W + (i-1) * (i-2) / 2 * S + (i - 1) * F) * x_i)    (Eq. 6)
                (from Eq. 5 and Eq. 3 - This equation is the calculated by this function)

        Although there are 4 constants that determine the distribution, the W may be normalized and here it is proposed
        to use a value to W such that the sum of all weights considered are equal to a constant C, this reduces the
        number of tests once C may be the same for all tests. So W is defined as:

            W = (C - R * (R-1) / 2 * F - combinations(R, R-3) * S) / R               (Eq. 7)
                (from Eq. 6)

        This equation will guarantee that the following is valid:

            Sum(i=1..R, W + (i-1)*(i-2)/2 * S + (i-1) * F) = C                      (Eq. 8)

        And this allows an efficient normalization of the data with minimum memory and cpu time consumption considering
        distribution patterns that can be either, linear, or with positive second derivative (like it was being done
        with the nn_input_value function) and with negative second derivative, allowing more complex and possibly more
        realistic ways to represent the data

        Planned tests:
            Format: (F, S, R)
            Initial Tests:
                (-0.25, 0.04, 5)
                (-0.1, -0.04, 5)
                (-0.1, 0, 5)
                (-0.2, 0, 5)
                (-0.25, 0.04, 3)
                (-0.1, -0.04, 3)
                (-0.1, 0, 3)
                (-0.2, 0, 3)

    """
    R = 5
    F = -0.25
    S = 0.04
    C = 5
    W = (C - R * (R - 1) / 2 * F - combinations(R, R - 3) * S) / R
    X = []
    if attribute_type == 'player':
        for r_i in range(R):
            try:
                x_i = log[player][year][round_num - r_i][attribute]
            except KeyError:
                x_i = 0.0
            X.append(x_i)
    elif attribute_type == 'team':
        for r_i in range(R):
            try:
                x_i = matches[year][round_num][team][attribute]
            except KeyError:
                x_i = 0.0
            X.append(x_i)
    else:
        print("ERROR: invalid attribute type to round forecast")
        exit()
    V = 0
    for i in range(1, R + 1):
        V += ((W + (i - 1) * (i - 2) / 2 * S + (i - 1) * F) * X[i - 1])

    return V


def nn_input_value(current_acc, new_info):
    decay = 0.3
    return current_acc * decay + new_info


def read_matches(file_name):
    file = open(file_name, 'r', encoding='ISO-8859-1')
    first_line = True
    for line in file.readlines():
        if first_line:
            first_line = False
        else:
            args = line.split(',')
            year = args[0]
            round_num = int(args[1])
            home_team = args[2]
            away_team = args[3]
            home_goals = float(args[4])
            away_goals = float(args[5])
            home_pos = int(args[6])
            away_pos = int(args[7])
            if matches.get(year) is None:
                matches[year] = {}
            if matches[year].get(round_num) is None:
                matches[year][round_num] = {}

            matches[year][round_num][home_team] = \
                {
                    'goals_taken': away_goals, 'goals_scored': home_goals, 'adv': away_team,
                    'pos': home_pos, 'home': True
                }
            matches[year][round_num][away_team] = \
                {
                    'goals_taken': home_goals, 'goals_scored': away_goals, 'adv': home_team,
                    'pos': away_pos, 'home': False
                }


def parse_input():
    parser = argparse.ArgumentParser(description='Receive file to extract data')
    parser.add_argument('-d', '--dir', required=True, type=str,
                        help='Directory with data')

    parser.add_argument('-m', '--matches', required=True, type=str,
                        help='File with match history')
    args = parser.parse_args()

    read_matches(args.matches)
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
            scores[player][year][curr_round][i] = nn_input_value(
                scores[player][year][curr_round - 1][i], log[player][year][curr_round][i]
            )
        else:
            scores[player][year][curr_round][i] = nn_input_value(scores[player][year][curr_round - 1][i], 0.0)

    if log[player][year].get(curr_round) is not None and len(log[player][year][curr_round]) > 0:
        scores[player][year][curr_round][-1] = nn_input_value(
            scores[player][year][curr_round - 1][-1], log[player][year][curr_round][-3]
        )
    else:
        scores[player][year][curr_round][-1] = nn_input_value(scores[player][year][curr_round - 1][-1], 0.0)


def process_team_logs():
    prev_round = {}
    prev_year = {}
    for year in matches:
        for round_num in range(1, max(matches[year]) + 1):
            for team in matches[year][round_num]:
                if teams.get(team) is None:
                    teams[team] = {}
                if teams[team].get(year) is None:
                    teams[team][year] = {}
                if teams[team][year].get(round_num) is None:
                    teams[team][year][round_num] = {}
                if round_num > 1:
                    teams[team][year][round_num]['goals_taken'] = nn_input_value(
                        teams[team][prev_year[team]][prev_round[team]]['goals_taken'],
                        matches[year][round_num][team]['goals_taken']
                    )
                    teams[team][year][round_num]['goals_scored'] = nn_input_value(
                        teams[team][prev_year[team]][prev_round[team]]['goals_scored'],
                        matches[year][round_num][team]['goals_scored']
                    )
                else:
                    teams[team][year][round_num]['goals_taken'] = matches[year][round_num][team]['goals_taken']
                    teams[team][year][round_num]['goals_scored'] = matches[year][round_num][team]['goals_scored']

                prev_round[team] = round_num
                prev_year[team] = year


def process_player_logs():
    for player in log:
        years_played = list(log[player].keys())
        years_played.sort()
        for year in years_played:
            for roundNum in range(1, ROUNDS + 1):
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
        return None, None
    else:
        curr_team = player_teams[0]
        for team in player_teams:
            if team[1] > curr_team[1] or (team[1] == curr_team[1] and team[2] > curr_team[2]):
                curr_team = team
        try:
            adv = matches[curr_team[1]][curr_team[2]][curr_team[0]]['adv']
        except KeyError:
            adv = None
        return curr_team[0], adv


def write_data_to_file():
    out_file = open('scoresExtractedData.csv', 'w', encoding='ISO-8859-1')

    out_file.write(
        'PlayerID,Year,Round,Team,A,CA,CV,DD,DP,FC,FD,FF,FS,FT,G,GC,GS,I,PE,PP,RB,SG,PNT,pos,price,proGoals,'
        'consGoals,advPG,advCG,teamPos,advPos,home,realScore\n'
    )

    for player in scores:
        for year in log[player]:
            for roundNum in range(1, max(log[player][year]) + 1):
                out_file.write(str(player) + ',' + str(year) + ',' + str(roundNum))
                if log[player][year].get(roundNum) is not None and len(log[player][year][roundNum]) > 0:
                    team = log[player][year][roundNum][-4]
                    try:
                        adv = matches[year][roundNum][team]['adv']
                    except KeyError:
                        adv = None
                else:
                    team, adv = get_player_team(player, year, roundNum)

                if team == 'Athlético-PR':
                    team = 'Atlético-PR'

                out_file.write(',' + str(team))
                for item in scores[player][year][roundNum]:
                    out_file.write(',' + '{:.2f}'.format(item))
                if log[player][year].get(roundNum) is not None and len(
                        log[player][year][roundNum]) > 0 and adv is not None:
                    out_file.write(',' + str(log[player][year][roundNum][-2]) + ',' + str(
                        log[player][year][roundNum][-1]) +
                                   ',' + '{:.2f}'.format(teams[team][year][roundNum]['goals_scored']) + ',' +
                                   '{:.2f}'.format(teams[team][year][roundNum]['goals_taken']) + ',' +
                                   '{:.2f}'.format(teams[adv][year][roundNum]['goals_scored']) + ',' +
                                   '{:.2f}'.format(teams[adv][year][roundNum]['goals_taken']) + ',' +
                                   str(matches[year][roundNum][team]['pos']) + ',' +
                                   str(matches[year][roundNum][adv]['pos']) + ',' +
                                   str(int(matches[year][roundNum][team]['home'])) + ',' +
                                   str(log[player][year][roundNum][-3]))
                else:
                    out_file.write(',NA,NA,0.0,0.0,0.0,0.0,NA,NA,0,NA')

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
            'consGoals,advPG,advCG,teamPos,advPos,home,realScore\n'
        )

    for line in in_file.readlines():
        if line.find(',gol,') >= 0:
            gol_file.write(line)
        elif line.find(',zag,') >= 0:
            zag_file.write(line)
        elif line.find(',lat,') >= 0:
            lat_file.write(line)
        elif line.find(',mei,') >= 0:
            mei_file.write(line)
        elif line.find(',ata,') >= 0:
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
