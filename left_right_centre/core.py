import numpy as np
from numpy import random

from typing import List
from dataclasses import dataclass

from .statistics import History, Statistics


def play_lrc_game(players: int = 3, chips: int = 100):
    """ Play a game of Left, Right, and Centre."""
    g = Game(players, chips)
    g.play_game()
    
    return g


# @dataclass
# class GameSetup:

#     no_of_players: int = 3
#     no_of_chips: int = 100
#     chips_in_centre_pile: int = 0
    
#     # Config settings
#     take_chips_on_pd: bool = True


# @dataclass
# class GameState:

#     chips_in_centre_pile: int = 0


class Game:
    """ Contains the setup and process of the Left, Right & Centre game. """

    dice: List[str] = ['L', 'R', 'C', 'd', 'd', 'pd']
    end_of_game: bool = False

    no_of_players: int = 3
    no_of_chips: int = 100
    chips_in_centre_pile: int = 0
    
    # Config settings
    take_chips_on_pd: bool = True


    def __init__(self, no_of_players: int, no_of_chips: int):
        self.no_of_players = no_of_players
        self.no_of_chips = no_of_chips

        self.setup_game()
    
    def setup_game(self) -> None:
        self.players = {
            i : Player(
                    id = i,
                    chips = self.no_of_chips // self.no_of_players,
                    no_of_players = self.no_of_players
                )
                for i in range(1, self.no_of_players + 1)
            }
        self.history = History(self.no_of_players)

        for id in self.players:
            self.history.data[f"p{id}"].append(self.players[id].chips)
        
        self.history.data['centre_pile'].append(self.chips_in_centre_pile)
        self.history.data['player_in_play'].append(np.nan)
        self.history.data['dices'].append(np.nan)

        self.winner = None
    
    def record_turn(self, player_id: int, dices: List[str]) -> None:
        for id in self.players:
            self.history.data[f"p{id}"].append(self.players[id].chips)
        
        self.history.data['centre_pile'].append(self.chips_in_centre_pile)
        self.history.data['player_in_play'].append(player_id)
        self.history.data['dices'].append(dices)
    
    def roll_dice(self) -> str:
        return random.choice(self.dice)
    
    def distribute_chips(self, dices: List[str], player_id: int) -> None:
        player = self.players[player_id]

        if dices == ['pd', 'pd', 'pd'] and self.take_chips_on_pd:
            player.chips += self.chips_in_centre_pile
            self.chips_in_centre_pile = 0
        else:
            for d in dices:
                if d == 'L':
                    player.chips -= 1
                    self.players[player.left_player].chips += 1
                elif d == 'R':
                    player.chips -= 1
                    self.players[player.right_player].chips += 1
                elif d == 'C':
                    player.chips -= 1
                    self.chips_in_centre_pile += 1
                elif d == 'pd':
                    players_to_steal_from = self.players_to_steal_from(player_id)
                    if players_to_steal_from:
                        self.players[random.choice(players_to_steal_from)].chips -= 1
                        player.chips += 1

    def check_for_winner(self) -> None:
        for p in self.players:
            if self.players[p].chips == self.no_of_chips - self.chips_in_centre_pile:
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
            player_in_play = player_in_play + 1 if player_in_play != self.no_of_players else 1
            if self.end_of_game:
                break
        print("="*20)
        print("END OF GAME")
        print("="*20)
    
    def players_to_steal_from(self, player_id: int) -> List[int]:
        player = self.players[player_id]

        if player.aggression_level == 1:
            players_to_steal_from = [player.left_player, player.right_player]
        elif player.aggression_level == 3:
            players_to_steal_from = [p for p in range(1, self.no_of_players + 1) if (p != player.left_player and p != player.right_player)] 
        else:
            players_to_steal_from = [p for p in range(1, self.no_of_players + 1)]

        final_list = []
        for p in players_to_steal_from:
            if self.players[p].chips > 0:
                final_list.append(p)
        
        return final_list


@dataclass
class Player:
    
    id: int
    chips: int 
    no_of_players: int
    name: str = ''
    aggression_level: int = 1

    def access_player_ids(self, movement: int) -> int:
        nop = self.no_of_players
        if self.id + movement == 0:
            return nop
        elif self.id + movement == nop + 1:
            return 1
        else:
            return self.id + movement
    
    @property
    def left_player(self) -> int:
        return self.access_player_ids(-1)

    @property
    def right_player(self) -> int:
        return self.access_player_ids(1)
