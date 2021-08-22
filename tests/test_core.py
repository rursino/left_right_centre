from left_right_centre import Game, Player


@pytest.fixture
def input_data():
    return {
        (5, 20): 4,
        (6, 19): 3,
        (3, 16.5): 5
    }

def test_setup(input_data):

    for setup in input_data:
        no_of_players, no_of_chips = setup
        g = Game(no_of_players, no_of_chips)

        expected_chips_per_player = input_data[setup]
        for player in g.players:
            assert g.players[player].chips == expected_chips_per_player

def test_access_ids():
    no_of_players = 5
    no_of_chips = 200
    g = Game(no_of_players, no_of_chips)

    player_ids = {
        1: (no_of_players, 2),
        no_of_players: (no_of_players - 1, 1),
        no_of_players // 2: (no_of_players // 2 - 1, no_of_players // 2 + 1)
    }

    for id in player_ids:
        expected_results = player_ids[id]
        assert g._access_player_ids(id, -1) == expected_results[0]
        assert g._access_player_ids(id, 1) == expected_results[1]