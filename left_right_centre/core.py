import numpy as np
from numpy import random

from typing import List, Dict
from dataclasses import dataclass

from .statistics import History

from collections import namedtuple



CreatePlayer = namedtuple("CreatePlayer", ["chips", "name", "aggression_level"])


def play_lrc_game(players_dict, take_chips_on_pd: bool = True):
    """ Play a game of Left, Right, and Centre."""

    setup = GameSetup(players_dict, take_chips_on_pd)
    g = Game(setup)
    g.play_game()
    
    return g


@dataclass
class GameSetup:
    
    players_input: List[CreatePlayer]
    chips_in_centre_pile: int = 0
    
    # Parameter settings
    take_chips_on_pd: bool = True

    @property
    def players(self):
        return {
            i + 1: Player(i + 1, player.chips, len(self.players_input), player.name, player.aggression_level)
            for i, player
            in enumerate(self.players_input)
        }

    @property
    def no_of_players(self):
        return len(self.players)
    
    @property
    def no_of_chips(self):
        return sum(self.players[player_id].chips for player_id in self.players)


class Game:
    """ Contains the setup and process of the Left, Right & Centre game. """

    dice: List[str] = ['L', 'R', 'C', 'd', 'd', 'pd']
    end_of_game: bool = False

    def __init__(self, setup: GameSetup):
        self.setup = setup
        self.players = setup.players
        self.setup_game()
 
    def setup_game(self) -> None:
        self.chips_in_centre_pile = self.setup.chips_in_centre_pile
        self.history = History(self.setup.no_of_players)

        for player_id in self.players:
            self.history.data[f"p{player_id}"].append(self.players[player_id].chips)
 
        self.history.data['centre_pile'].append(self.chips_in_centre_pile)
        self.history.data['player_in_play'].append(np.nan)
        self.history.data['dices'].append(np.nan)

        self.winner = None
    
    def record_turn(self, player_id: int, dices: List[str]) -> None:
        for pid in self.players:
            self.history.data[f"p{pid}"].append(self.players[pid].chips)
        
        self.history.data['centre_pile'].append(self.chips_in_centre_pile)
        self.history.data['player_in_play'].append(player_id)
        self.history.data['dices'].append(dices)
    
    def roll_dice(self) -> str:
        return random.choice(self.dice)
    
    def distribute_chips(self, dices: List[str], player_id: int) -> None:
        player = self.players[player_id]
        left_player = self.players[player.left_player]
        right_player = self.players[player.right_player]

        if dices == ['pd', 'pd', 'pd'] and self.setup.take_chips_on_pd:
            player.chips += self.chips_in_centre_pile
            self.chips_in_centre_pile = 0
        else:
            for d in dices:
                if d == 'L':
                    player.chips -= 1
                    left_player.chips += 1
                elif d == 'R':
                    player.chips -= 1
                    right_player.chips += 1
                elif d == 'C':
                    player.chips -= 1
                    self.chips_in_centre_pile += 1
                elif d == 'pd':
                    players_to_steal_from = player.players_to_steal_from(self.get_all_player_chips())
                    if players_to_steal_from:
                        self.players[random.choice(players_to_steal_from)].chips -= 1
                        player.chips += 1

    def check_for_winner(self) -> None:
        for p in self.players:
            if self.players[p].chips == self.setup.no_of_chips - self.chips_in_centre_pile:
                self.winner = p
                self.end_of_game = True
                print(f"GAME OVER!!! Player {p} has won!!")

    def play_turn(self, player_id: int) -> None:
        player = self.players[player_id]
        dices = [random.choice(self.dice) for _ in range(min(player.chips, 3))]

        self.distribute_chips(dices, player_id)
        self.record_turn(player_id, dices)
        self.check_for_winner()
    
    def play_game(self) -> None:
        print("WELCOME")
        print("="*20)
        player_in_play = 1
        while True:
            self.play_turn(player_in_play)
            player_in_play = player_in_play + 1 if player_in_play != self.setup.no_of_players else 1
            if self.end_of_game:
                break
        print("="*20)
        print("END OF GAME")
        print("="*20)
    
    def get_all_player_chips(self) -> Dict[(int, int)]:
        return {i: self.players[i].chips for i in self.players}


@dataclass
class Player:
    
    player_id: int
    chips: int

    no_of_players: int

    # Properties
    name: str = ''
    aggression_level: int = 1

    def access_player_ids(self, movement: int) -> int:
        if self.player_id + movement == 0:
            return self.no_of_players
        elif self.player_id + movement == self.no_of_players + 1:
            return 1
        else:
            return self.player_id + movement

    @property
    def left_player(self):
        return self.access_player_ids(-1)
    
    @property
    def right_player(self):
        return self.access_player_ids(1)

    def players_to_steal_from(self, all_player_chips: Dict) -> List[int]:
        if self.aggression_level == 1:
            players_to_steal_from = [self.left_player, self.right_player]
        elif self.aggression_level == 3:
            players_to_steal_from = [p for p in range(1, self.no_of_players + 1) if (p != self.left_player and p != self.right_player and p != self.player_id)] 
        else:
            players_to_steal_from = [p for p in range(1, self.no_of_players + 1) if p != self.player_id]

        final_list = []
        for p in players_to_steal_from:
            if all_player_chips[p] > 0:
                final_list.append(p)
        
        return final_list
