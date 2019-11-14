import cartolafc

api = cartolafc.Api()
mercado = api.mercado()

previous_scout = []


def read_previous_scout(current_round):
    pass


def get_round_diff(player_id, new_scout):
    pass

def update_data(player_id):
    atletas = api.mercado_atletas()
    player = [atleta for atleta in atletas if atleta.id == player_id]
    if len(player) != 1:
        return None
    player = player[0]
    scouts = player.scout


if __name__ == '__main__':
    current_round = mercado.rodada_atual
    read_previous_scout(current_round)
