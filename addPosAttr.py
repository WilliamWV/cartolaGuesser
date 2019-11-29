import functools
import cartolafc

logs = {}
classifications = {}


class Match:
    def __init__(self, home, away, hg, ag):
        self.home = home
        self.away = away
        self.hg = hg
        self.ag = ag


class TeamClassification:

    def __init__(self, year, round_num, name):
        self.points = 0
        self.wins = 0
        self.draws = 0
        self.loses = 0
        self.gp = 0
        self.gc = 0
        self.sg = 0
        self.year = year
        self.round_num = round_num
        self.name = name

    def __eq__(self, other):
        return self.points == other.points and self.wins == other.wins and self.sg == other.sg and self.gp == other.gp

    def __lt__(self, other):
        if self.points < other.points:
            return True
        elif self.points > other.points:
            return False
        elif self.wins < other.wins:
            return True
        elif self.wins > other.wins:
            return False
        elif self.sg < other.sg:
            return True
        elif self.sg > other.sg:
            return False
        elif self.gp < other.gp:
            return True
        elif self.gp > other.gp:
            return False
        return False

    '''def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return not (self < other)

    def __gt__(self, other):
        return not (self <= other)

    def __ne__(self, other):
        return not (self == other)
'''
    def __repr__(self):
        return "Pnt: %d\tW: %d\tD: %d\tL: %d\tGP: %d\tGC: %d\tSG:%d\t%s\n" % (self.points, self.wins, self.draws, self.loses, self.gp, self.gc, self.sg, self.name)


def copy_classification(old):
    new = TeamClassification(old.year, old.round_num, old.name)
    new.points = old.points
    new.wins = old.wins
    new.draws = old.draws
    new.loses = old.loses
    new.gp = old.gp
    new.gc = old.gc
    new.sg = old.sg
    new.year = old.year
    new.round_num = old.round_num
    new.name = old.name
    return new


def update_classification(team_classification, match):
    goals_pro = 0
    goals_cons = 0
    new_class = copy_classification(team_classification)
    if team_classification.name == match.home:
        goals_pro = match.hg
        goals_cons = match.ag
    elif team_classification.name == match.away:
        goals_pro = match.ag
        goals_cons = match.hg

    new_class.gp += goals_pro
    new_class.gc += goals_cons
    new_class.sg += (goals_pro - goals_cons)
    if goals_pro > goals_cons:
        new_class.wins += 1
        new_class.points += 3
    elif goals_pro < goals_cons:
        new_class.loses += 1
    else:
        new_class.draws += 1
        new_class.points += 1

    return new_class


def init_objs():
    file_name = 'matches.csv'
    out_file = 'matches_with_pos.csv'
    file = open(file_name, 'r')
    out = open(out_file, 'w')
    return file, out


def get_last_class(year, round_num, team):
    current_attempt = round_num - 1
    while current_attempt > 0:
        try:
            return logs[year][current_attempt][team]
        except KeyError:
            current_attempt -= 1

    return TeamClassification(year, round_num, team)


def read_data(file):
    header = file.readline()
    for line in file.readlines():
        items = line.split(',')
        year = int(items[0])
        round_num = int(items[1])
        match = Match(items[2], items[3], float(items[4]), float(items[5]))
        if logs.get(year) is None:
            logs[year] = {}
        if logs[year].get(round_num) is None:
            logs[year][round_num] = {}

        last_classification = get_last_class(year, round_num, items[2])
        logs[year][round_num][items[2]] = update_classification(last_classification, match)
        last_classification = get_last_class(year, round_num, items[3])
        logs[year][round_num][items[3]] = update_classification(last_classification, match)


def classify_teams(teams_features):
    return sorted(teams_features, reverse=True)


def mount_classifications():
    years = list(logs.keys())
    mercado = cartolafc.Api().mercado()
    current_year = mercado.fechamento.year
    current_round = mercado.rodada_atual
    for year in years:
        classifications[year] = {}
        max_range = 39
        if current_year == year:
            max_range = current_round
        for round_num in range(1, max_range):
            teams = list(logs[year][round_num].values())
            classifications[year][round_num] = classify_teams(teams)


def get_pos(year, round_num, team):
    current_pos = 1
    teams = classifications[int(year)][int(round_num)]
    while teams[current_pos-1].name != team:
        current_pos += 1

    return current_pos


def write_new_file(file, out):
    file.seek(0)
    _ = file.readline()
    out.write('Year,Round,Home,Away,HG,AG,Hpos,Apos\n')

    for line in file.readlines():
        items = line.replace('\n', '').split(',')
        out.write(items[0] + ',' + items[1] + ',' + items[2] + ',' + items[3] + ',' + items[4] + ',' + items[5] + ',')
        out.write(str(get_pos(items[0], items[1], items[2])) + ',' + str(get_pos(items[0], items[1], items[3])) + '\n')


if __name__ == '__main__':
    file, out = init_objs()
    read_data(file)
    mount_classifications()
    write_new_file(file, out)

