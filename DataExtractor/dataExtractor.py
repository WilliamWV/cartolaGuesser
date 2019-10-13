import argparse

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


outFile = open('extractedData.csv', 'w')


file = open(args.file, 'r', encoding='utf-8')
headers = file.readline().replace('\"', '').split(',')

log = {}

lines = [line.split(',') for line in file.readlines()]
for line in lines:

    playerID = line[2]
    year = line[30]
    roundNum = line[27]
    playedThisRound = line[20]

    if log.get(playerID) is None:
        log[playerID] = {}
    if log[playerID].get(year) is None:
        log[playerID][year] = {}
    if log[playerID][year].get(roundNum) is None:
        log[playerID][year][roundNum] = []

    if playedThisRound:
        log[playerID][year][roundNum].append(line[A])
        log[playerID][year][roundNum].append(line[CA])
        log[playerID][year][roundNum].append(line[CV])
        log[playerID][year][roundNum].append(line[DD])
        log[playerID][year][roundNum].append(line[DP])
        log[playerID][year][roundNum].append(line[FC])
        log[playerID][year][roundNum].append(line[FD])
        log[playerID][year][roundNum].append(line[FF])
        log[playerID][year][roundNum].append(line[FS])
        log[playerID][year][roundNum].append(line[FT])
        log[playerID][year][roundNum].append(line[G])
        log[playerID][year][roundNum].append(line[GC])
        log[playerID][year][roundNum].append(line[GS])
        log[playerID][year][roundNum].append(line[I])
        log[playerID][year][roundNum].append(line[PE])
        log[playerID][year][roundNum].append(line[PP])
        log[playerID][year][roundNum].append(line[RB])
        log[playerID][year][roundNum].append(line[SG])

        log[playerID][year][roundNum].append(line[23])
        log[playerID][year][roundNum].append(line[24])

outFile.write('PlayerID,Year,Round,A,CA,CV,DD,DP,FC,FD,FF,FS,FT,G,GC,GS,I,PE,PP,RB,SG,pos,price\n')

for player in log:
    for year in log[player]:
        for roundNum in log[player][year]:
            outFile.write(str(player) + ',' + str(year) + ',' + str(roundNum))
            if len(log[player][year][roundNum]) > 0:
                for i in range(len(log[player][year][roundNum])):
                    outFile.write(',' + str(log[player][year][roundNum][i]))

            outFile.write('\n')
