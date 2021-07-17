from numpy import random
import numpy as np
import csv
import pandas as pd


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

        self.history = History(self.no_of_players)

        for id in self.players:
            self.history.data[id].append(self.players[id].chips)
        
        self.history.data['centre_pile'].append(self.chips_in_centre_pile)
        self.history.data['player_in_play'].append(np.nan)
        self.history.data['dices'].append(np.nan)
    
    def _access_player_ids(self, player_id, movement):
        nop = self.no_of_players
        if player_id + movement == 0:
            return nop
        elif player_id + movement == nop + 1:
            return 1
        else:
            return player_id + movement
    
    def _record_turn(self, player_id, dices):
        for id in self.players:
            self.history.data[id].append(self.players[id].chips)
        
        self.history.data['centre_pile'].append(self.chips_in_centre_pile)
        self.history.data['player_in_play'].append(player_id)
        self.history.data['dices'].append(dices)
    
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

        #fname = "results/history.csv"
        #self.history.to_csv(fname)  
            

class Player:
    def __init__(self, id, chips, name=''):
        self.id = id
        self.chips = chips
        self.name = name
    
    def __repr__(self):
        return f"Player {self.name} ({self.id}) --> Number of chips: {self.chips}"


class History:
    def __init__(self, no_of_players):
        self.columns = list(range(1, no_of_players + 1)) + ['centre_pile', 'player_in_play', 'dices']
        self.data = {col: [] for col in self.columns}

        self.no_of_players = no_of_players
    
    def to_dataframe(self):
        return pd.DataFrame(self.data)

    def to_csv(self, fname):
        pd.DataFrame(self.data).to_csv(fname)


class Statistics:
    def __init__(self, data):
        if type(data) == str and data.endswith(".csv"):
            _data = pd.read_csv(data)
            _data = _data.drop("Unnamed: 0", axis=1)
        elif type(data) == pd.DataFrame:
            _data = data

        self.data = _data
        self._cast_dice_lists() 

        self.no_of_players = self._no_of_players()
        self.final_stats = {
            'winner': self._winner(),
            'winner_pile': self.iloc(-1)[str(self._winner())],
            'centre_pile': self.iloc(-1).centre_pile,
            'game_length': self.game_length()
        }
    
    def _cast_dice_lists(self):
        dice_list = []
        for row in self.data.dices:
            try:
                new_row = row.strip('][').replace("'", "").split(', ')
            except AttributeError:
                new_row = np.nan
            dice_list.append(new_row)

        self.data.dices = dice_list

    def _no_of_players(self):
        players = 0
        for col in self.data.columns:
            try:
                int(col)
                players += 1
            except:
                pass
        return players

    def _winner(self):
        final_turn = self.data.iloc[-1]
        for player in range(1, self.no_of_players + 1):
            if final_turn[str(player)] != 0:
                return player

    def game_length(self):
        return len(self.data) - 1

    def iloc(self, row):
        return self.data.iloc[row]

    def search_dice_patterns(self, dice_1, dice_2, dice_3):
        column = self.data['dices']

        target = [dice_1, dice_2, dice_3]
        return [i for i, row in enumerate(column) if row == target] 