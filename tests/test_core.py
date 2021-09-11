from left_right_centre import Game, Player, History
import pytest
import numpy as np


@pytest.fixture
def input_data():
    return {
        (5, 20): 4,
        (6, 19): 3,
        (3, 16.5): 5
    }

@pytest.fixture
def player_setup_data():
    historical = History(3).data

    historical['p1'] = [100, 100, 101, 102, 100, 100]
    historical['p2'] = [100, 100, 97, 98, 99, 101]
    historical['p3'] = [100, 100, 101, 98, 99, 99]
    historical['centre_pile'] = [0, 0, 1, 2, 2, 0]
    historical['player_in_play'] = [np.nan, 1, 2, 3, 1, 2]
    historical['dices'] = [
            np.nan,
            ['d', 'd', 'd'],
            ['L', 'R', 'C'],
            ['L', 'C', 'R'],
            ['L', 'R', 'd'],
            ['pd', 'pd', 'pd'],
        ]

    return 3, 3*100, historical

@pytest.fixture
def winner_player_setup():
    # players, chips_list, centre_pile, winner_id, pass_result, end_of_game
    return [
        (5, [0,0,400,0,0], 100, 3, True, True),
        (3, [0,34,0], 65, 2, True, True),
        (3, [0,34,0], 65, 3, False, True),
        (4, [0,34,0,26], 140, 2, False, False),
        (4, [0,34,0,26], 140, 4, False, False),
    ]

def test_setup(input_data):

    for setup in input_data:
        no_of_players, no_of_chips = setup
        g = Game(no_of_players, no_of_chips)

        assert g.end_of_game == False
        assert g.dice == ['L', 'R', 'C', 'd', 'd', 'pd']
        assert g.chips_in_centre_pile == 0

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
    
def test_play_turn(input_data):
    for setup in input_data.keys():
        no_of_players, no_of_chips = setup
        g = Game(no_of_players, no_of_chips)

        player_id = 1
        for i, no_of_chips in enumerate(range(1, 5)):
            g.players[player_id].chips = no_of_chips
            g.play_turn(player_id)

            historical = g.history.data
            print(historical)
            assert len(historical["dices"][i+1]) == min(no_of_chips, 3)
            assert historical['player_in_play'][i+1] == player_id

def test_chip_distribution(player_setup_data):
    no_of_players, no_of_chips, historical = player_setup_data

    g = Game(no_of_players, no_of_chips)
    for i in range(1, len(historical['player_in_play'])):

        g._distribute_chips(
            historical['dices'][i],
            historical['player_in_play'][i]
        )

        assert historical['p1'][i] == g.players[1].chips
        assert historical['p2'][i] == g.players[2].chips
        assert historical['p3'][i] == g.players[3].chips
        assert historical['centre_pile'][i] == g.chips_in_centre_pile

def test_check_for_winner(winner_player_setup):
    for setup in winner_player_setup:
        no_of_players, chips_list, chips_in_centre_pile, winner_id, pass_result, end_of_game = setup
        no_of_chips = sum(chips_list) + chips_in_centre_pile
        g = Game(no_of_players, no_of_chips)

        for i in range(1, no_of_players + 1):
            g.players[i].chips = chips_list[i-1]
        g.chips_in_centre_pile = chips_in_centre_pile
        
        # Run target func.
        g._check_for_winner()
        if pass_result:
            assert g.winner == winner_id
        else:
            assert g.winner != winner_id
        assert g.end_of_game == end_of_game

def test_players_to_steal_from():
    expected_results = [
        (1, 5, )
    ]

