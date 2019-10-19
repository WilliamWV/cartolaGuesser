import argparse
import random

parser = argparse.ArgumentParser(description='Receive file to extract data')

parser.add_argument('-f', '--file', required=True, type=str,
                    help='File from which the data may be extracted')

args = parser.parse_args()

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

ROUNDS = 38
ATTRIBUTES = 18
DECAY = 0.5

file = open(args.file, 'r', encoding='utf-8')
headers = file.readline().replace('\"', '').split(',')

log = {}
scores = {}
results = {}
teams = {}


def build_log():
    lines = [line.split(',') for line in file.readlines()]
    for line in lines:

        player_id = line[PLAYER_ID]
        year = line[YEAR]
        round_num = int(line[ROUND])
        played_this_round = line[PLAYED_THIS_ROUND]
        team = line[TEAM]
        player_team = line[-1]
        home_score = float(line[HOME_SCORE])
        away_score = float(line[AWAY_SCORE])

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

        if played_this_round:
            for feature in [A, CA, CV, DD, DP, FC, FD, FF, FS, FT, G, GC, GS, IMP, PE, PP, RB, SG]:
                log[player_id][year][round_num].append(float(line[feature]))
            log[player_id][year][round_num].append(team)
            log[player_id][year][round_num].append(float(line[21]))
            log[player_id][year][round_num].append(line[23])
            log[player_id][year][round_num].append(float(line[24]))


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


def write_data_to_file():
    out_file = open('scoresExtractedData.csv', 'w')

    out_file.write(
        'PlayerID,Year,Round,A,CA,CV,DD,DP,FC,FD,FF,FS,FT,G,GC,GS,I,PE,PP,RB,SG,PNT,pos,price,proGoals,'
        'consGoals,realScore\n'
    )

    for player in scores:
        for year in log[player]:
            for roundNum in range(ROUNDS):
                out_file.write(str(player) + ',' + str(year) + ',' + str(roundNum))
                for item in scores[player][year][roundNum]:
                    out_file.write(',' + '{:.2f}'.format(item))
                if log[player][year].get(roundNum + 1) is not None and len(log[player][year][roundNum + 1]) > 0:
                    team = log[player][year][roundNum + 1][-4]
                    out_file.write(',' + str(log[player][year][roundNum + 1][-2]) + ',' + str(
                        log[player][year][roundNum + 1][-1]) +
                                   ',' + '{:.2f}'.format(teams[team][year][roundNum]['acc_goals']) + ',' +
                                   '{:.2f}'.format(teams[team][year][roundNum]['tak_goals']) + ',' +
                                   str(log[player][year][roundNum + 1][-3]))
                else:
                    out_file.write(',NA,NA,NA,NA,NA')

                out_file.write('\n')
    out_file.close()


def filter_file():
    in_file = open('scoresExtractedData.csv', 'r')
    out_file = open('scoresExtractedFiltered.csv', 'w')
    for line in in_file.readlines():
        if line.find('NA') < 0:
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
            'PlayerID,Year,Round,A,CA,CV,DD,DP,FC,FD,FF,FS,FT,G,GC,GS,I,PE,PP,RB,SG,PNT,pos,price,proGoals,'
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
            mei_file.write('mei')
        elif line.find('ata') >= 0:
            ata_file.write(line)


def write_nn_file(in_file_path):
    in_file = open(in_file_path, 'r')
    train_file = open('train/' + in_file_path.replace('.csv', '') + '_train.csv', 'w')
    test_file = open('test/' + in_file_path.replace('.csv', '') + '_test.csv', 'w')
    train_percent = 0.7
    first_line = True
    for line in in_file.readlines():
        third_comma_pos = line.find(',', line.find(',', line.find(',')+1)+1)
        line = line.replace('zag,', '').replace('mei,', '').replace('lat,', '').replace('gol,', '')\
            .replace('ata,', '').replace('pos,', '')
        if first_line:
            train_file.write(line[third_comma_pos+1:])
            test_file.write(line[third_comma_pos+1:])
            first_line = False
        else:
            if random.random() <= train_percent:
                train_file.write(line[third_comma_pos+1:])
            else:
                test_file.write(line[third_comma_pos+1:])


if __name__ == '__main__':
    build_log()
    process_team_logs()
    process_player_logs()
    write_data_to_file()
    filter_file()
    split_file()
    for ans_file in ['scoresGol.csv', 'scoresZag.csv', 'scoresLat.csv', 'scoresMei.csv', 'scoresAta.csv']:
        write_nn_file(ans_file)
