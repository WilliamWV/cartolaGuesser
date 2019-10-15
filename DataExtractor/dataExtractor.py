import argparse
import os

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
I = 16
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

def build_results():
    files = os.listdir('data/results')
    for file_name in files:
        file = open(file_name, 'r', encoding='utf-8')


def build_log():

    lines = [line.split(',') for line in file.readlines()]
    for line in lines:

        playerID = line[PLAYER_ID]
        year = line[YEAR]
        roundNum = int(line[ROUND])
        playedThisRound = line[PLAYED_THIS_ROUND]
        team = line[TEAM]
        playerTeam = line[-1]
        homeScore = float(line[HOME_SCORE])
        awayScore = float(line[AWAY_SCORE])
        teamScore = 0
        advScore = 0

        if playerTeam.find('home') >= 0:
            teamScore = homeScore
            advScore = awayScore
        else:
            teamScore = awayScore
            advScore = homeScore

        if teams.get(team) == None:
            teams[team] = {}
        if teams[team].get(year) == None:
            teams[team][year] = {}
        if teams[team][year].get(roundNum) == None:
            teams[team][year][roundNum] = {'goals_scored': teamScore, 'goals_taken': advScore}


        if log.get(playerID) is None:
            log[playerID] = {}
        if log[playerID].get(year) is None:
            log[playerID][year] = {}
        if log[playerID][year].get(roundNum) is None:
            log[playerID][year][roundNum] = []

        if playedThisRound:
            log[playerID][year][roundNum].append(float(line[A]))
            log[playerID][year][roundNum].append(float(line[CA]))
            log[playerID][year][roundNum].append(float(line[CV]))

            log[playerID][year][roundNum].append(float(line[DD]))
            log[playerID][year][roundNum].append(float(line[DP]))
            log[playerID][year][roundNum].append(float(line[FC]))

            log[playerID][year][roundNum].append(float(line[FD]))
            log[playerID][year][roundNum].append(float(line[FF]))
            log[playerID][year][roundNum].append(float(line[FS]))

            log[playerID][year][roundNum].append(float(line[FT]))
            log[playerID][year][roundNum].append(float(line[G]))
            log[playerID][year][roundNum].append(float(line[GC]))

            log[playerID][year][roundNum].append(float(line[GS]))
            log[playerID][year][roundNum].append(float(line[I]))
            log[playerID][year][roundNum].append(float(line[PE]))

            log[playerID][year][roundNum].append(float(line[PP]))
            log[playerID][year][roundNum].append(float(line[RB]))
            log[playerID][year][roundNum].append(float(line[SG]))

            log[playerID][year][roundNum].append(team)
            log[playerID][year][roundNum].append(float(line[21]))
            log[playerID][year][roundNum].append(line[23])
            log[playerID][year][roundNum].append(float(line[24]))


def build_line(player, year, currRound):


    if scores.get(player) is None:
        scores[player] = {}
    if scores[player].get(year) is None:
        scores[player][year] = {}
        scores[player][year][0] = [0] * ATTRIBUTES

    scores[player][year][currRound] = [0] * ATTRIBUTES

    for i in range(ATTRIBUTES):
        if log[player][year].get(currRound) is not None and len(log[player][year][currRound]) > 0:
            scores[player][year][currRound][i] = scores[player][year][currRound - 1][i] * DECAY + log[player][year][currRound][i]
        else:
            scores[player][year][currRound][i] = scores[player][year][currRound - 1][i] * DECAY


def main():

    build_log()

    for team in teams:
        for year in teams[team]:
            if teams[team][year].get(0) is None:
                teams[team][year][0] = {'goals_scored': 0, 'goals_taken': 0}

            teams[team][year][0]['acc_goals'] = 0.0
            teams[team][year][0]['tak_goals'] = 0.0

            for roundNum in range(1, ROUNDS):
                if teams[team][year].get(roundNum) is None:
                    teams[team][year][roundNum] = {'goals_scored': 0, 'goals_taken': 0}

                teams[team][year][roundNum]['acc_goals'] = DECAY * teams[team][year][roundNum-1]['acc_goals'] + teams[team][year][roundNum]['goals_scored']
                teams[team][year][roundNum]['tak_goals'] = DECAY * teams[team][year][roundNum-1]['tak_goals'] + teams[team][year][roundNum]['goals_taken']

    for player in log:
        years_played = list(log[player].keys())
        years_played.sort()
        player_scores = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for year in years_played:
            for roundNum in range(1, ROUNDS):
                build_line(player, year, roundNum)

    outFile = open('scoresExtractedData.csv', 'w')

    outFile.write('PlayerID,Year,Round,A,CA,CV,DD,DP,FC,FD,FF,FS,FT,G,GC,GS,I,PE,PP,RB,SG,PNT,pos,price,team,proGoals,consGoals,realScore\n')

    for player in scores:
        for year in log[player]:
            for roundNum in range(ROUNDS):
                outFile.write(str(player) + ',' + str(year) + ',' + str(roundNum))
                for item in scores[player][year][roundNum]:
                    outFile.write(',' + '{:.2f}'.format(item))
                if log[player][year].get(roundNum+1) is not None and len(log[player][year][roundNum+1]) > 0:
                    team = log[player][year][roundNum + 1][-4]
                    outFile.write(',' + str(log[player][year][roundNum+1][-2]) + ',' + str(log[player][year][roundNum+1][-1]) +
                                  ',' + str(team) + ',' + str(teams[team][year][roundNum]['acc_goals']) + ',' +
                                  str(teams[team][year][roundNum]['tak_goals']) + ',' +
                                  str(log[player][year][roundNum+1][-3]))
                else:
                    outFile.write(',NA,NA,NA,NA,NA,NA')

                outFile.write('\n')
    outFile.close()


def filter_file():
    file = open('scoresExtractedData.csv', 'r')
    outFile = open('scoresExtractedFiltered.csv', 'w')
    for line in file.readlines():
        if line.find('NA') < 0:
            outFile.write(line)

def split_file():
    file = open('scoresExtractedFiltered.csv', 'r')
    golFile = open('scoresGol.csv', 'w')
    zagFile = open('scoresZag.csv', 'w')
    latFile = open('scoresLat.csv', 'w')
    meiFile = open('scoresMei.csv', 'w')
    ataFile = open('scoresAta.csv', 'w')

    for line in file.readlines():
        if line.find('gol') >= 0:
            golFile.write(line)
        elif line.find('zag') >= 0:
            zagFile.write(line)
        elif line.find('lat') >= 0:
            latFile.write(line)
        elif line.find('mei') >= 0:
            meiFile.write('mei')
        elif line.find('ata') >= 0:
            ataFile.write(line)

if __name__ == '__main__':
    main()
    filter_file()
    split_file()
