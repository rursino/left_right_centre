import numpy as np
from numpy import random

from typing import List, Dict
from dataclasses import dataclass

from .statistics import History, Statistics


def play_lrc_game(players: int = 3, chips: int = 100):
    """ Play a game of Left, Right, and Centre."""
    setup = GameSetup(players, chips)
    g = Game(setup)
    g.play_game()
    
    return g


@dataclass
class GameSetup:

    no_of_players: int = 3
    no_of_chips: int = 100
    chips_in_centre_pile: int = 0
    
    # Parameter settings
    take_chips_on_pd: bool = True


class Game:
    """ Contains the setup and process of the Left, Right & Centre game. """

    dice: List[str] = ['L', 'R', 'C', 'd', 'd', 'pd']
    end_of_game: bool = False

    def __init__(self, setup: GameSetup):
        self.setup = setup
        self.setup_game()
 
    def setup_game(self) -> None:
        self.chips_in_centre_pile = self.setup.chips_in_centre_pile

        self.players = {
            i : Player(
                    player_id = i,
                    chips = self.setup.no_of_chips // self.setup.no_of_players,
                    no_of_players = self.setup.no_of_players
                )
                for i in range(1, self.setup.no_of_players + 1)
            }
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
        nop = self.no_of_players
        if self.player_id + movement == 0:
            return nop
        elif self.player_id + movement == nop + 1:
            return 1
        else:
            return self.player_id + movement
    
    @property
    def left_player(self) -> int:
        return self.access_player_ids(-1)

    @property
    def right_player(self) -> int:
        return self.access_player_ids(1)
    
    def players_to_steal_from(self, all_player_chips: Dict) -> List[int]:
        if self.aggression_level == 1:
            players_to_steal_from = [self.left_player, self.right_player]
        elif self.aggression_level == 3:
            players_to_steal_from = [p for p in range(1, self.no_of_players + 1) if (p != self.left_player and p != self.right_player)] 
        else:
            players_to_steal_from = [p for p in range(1, self.no_of_players + 1)]

        final_list = []
        for p in players_to_steal_from:
            if all_player_chips[p] > 0:
                final_list.append(p)
        
        return final_list
