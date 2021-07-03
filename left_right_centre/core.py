from numpy import random
import numpy as np
import csv


class Game:
    def __init__(self, no_of_players=3, no_of_chips=100):
        self.no_of_players = no_of_players
        self.no_of_chips = no_of_chips
        self.dice = ['L', 'R', 'C', 'd', 'd', 'pd']
        self.chips_in_centre_pile = 0
        
        self.end_of_game = False
        
        self._setup_game()
    
    def _setup_game(self):
        self.players = {
            i : Player(i, self.no_of_chips // self.no_of_players) for i in range(1, self.no_of_players + 1)
        }

        self.history = [{i : self.players[i].chips for i in range(1, self.no_of_players + 1)}]
        self.history[0]['centre_pile'] = self.chips_in_centre_pile
    
    def _access_player_ids(self, player_id, movement):
        nop = self.no_of_players
        if player_id + movement == 0:
            return nop
        elif player_id + movement == nop + 1:
            return 1
        else:
            return player_id + movement
    
    def _record_turn(self, player_id, dices):
        turn_info = {
            i : self.players[i].chips for i in range(1, self.no_of_players + 1)
        }
        turn_info['centre_pile'] = self.chips_in_centre_pile
        turn_info['player_in_play'] = player_id
        turn_info['dices'] = dices
        self.history.append(turn_info)
    
    def _roll_dice(self):
        return random.choice(self.dice)
    
    def _distribute_chips(self, dices, player_id):
        player = self.players[player_id]
        left_player = self._access_player_ids(player_id, -1)
        right_player = self._access_player_ids(player_id, 1)

        for d in dices:
            if d == 'L':
                player.chips -= 1
                self.players[left_player].chips += 1
            elif d == 'R':
                player.chips -= 1
                self.players[right_player].chips += 1
            elif d == 'C':
                player.chips -= 1
                self.chips_in_centre_pile += 1
            elif d == 'pd':
                # Disable taking chips from players if also get L and R, or a player has no chips.
                players_to_steal_from = []
                for p in self.players:
                    if self.players[p].chips > 0 and p != left_player and p != right_player and p != player_id:
                        players_to_steal_from.append(p)
                if players_to_steal_from:
                    self.players[random.choice(players_to_steal_from)].chips -= 1
                    player.chips += 1

    def _check_for_winner(self):
        for p in self.players:
            if self.players[p].chips == self.no_of_chips - self.chips_in_centre_pile:
                self.winner = p
                self.end_of_game = True
                print(f"GAME OVER!!! Player {p} has won!!")

    def play_turn(self, player_id):
        player = self.players[player_id]

        if player.chips > 0:
            if player.chips >= 3:
                dices = [random.choice(self.dice) for _ in range(3)]
                if dices == ['pd', 'pd', 'pd']:
                    player.chips += self.chips_in_centre_pile
                    self.chips_in_centre_pile = 0
                else:
                    self._distribute_chips(dices, player_id)
            else:
                dices = [random.choice(self.dice) for _ in range(player.chips)]
                self._distribute_chips(dices, player_id)
        else:
            dices = []

        self._record_turn(player_id, dices)
        self._check_for_winner()
    
    def play_game(self):
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

        toCSV = self.history[1:]
        with open('results/history.csv', 'w+', newline ='') as file:    
            writer = csv.DictWriter(file , toCSV[0].keys())
            writer.writeheader()
            writer.writerows(toCSV)

class Player:
    def __init__(self, id, chips):
        self.id = id
        self.chips = chips
    
    def __repr__(self):
        return f"Player {self.id} --> Number of chips: {self.chips}"
