from numpy import random
import numpy as np
import pandas as pd


class Game:

    dice = ['L', 'R', 'C', 'd', 'd', 'pd']
    chips_in_centre_pile = 0    
    end_of_game = False
    take_chips_on_pd = True

    def __init__(self, no_of_players=3, no_of_chips=100):
        self.no_of_players = no_of_players
        self.no_of_chips = no_of_chips

        self._setup_game()
        self.play_game()
    
    def _setup_game(self):
        self.players = {
            i : Player(i, self.no_of_chips // self.no_of_players) for i in range(1, self.no_of_players + 1)
        }

        self.history = History(self.no_of_players)

        for id in self.players:
            self.history.data[f"p{id}"].append(self.players[id].chips)
        
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
            self.history.data[f"p{id}"].append(self.players[id].chips)
        
        self.history.data['centre_pile'].append(self.chips_in_centre_pile)
        self.history.data['player_in_play'].append(player_id)
        self.history.data['dices'].append(dices)
    
    def _roll_dice(self):
        return random.choice(self.dice)
    
    def _distribute_chips(self, dices, player_id):
        player = self.players[player_id]

        if dices == ['pd', 'pd', 'pd'] and self.take_chips_on_pd:
            player.chips += self.chips_in_centre_pile
            self.chips_in_centre_pile = 0
        else:
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
                    players_to_steal_from = self._players_to_steal_from(player_id)
                    if players_to_steal_from:
                        self.players[random.choice(players_to_steal_from)].chips -= 1
                        player.chips += 1
    
    def _players_to_steal_from(self, player_id):
        player = self.players[player_id]
        left_player = self._access_player_ids(player_id, -1)
        right_player = self._access_player_ids(player_id, 1)

        if player.aggression_level == 1:
            players_to_steal_from = [left_player, right_player]
        elif player.aggression_level == 3:
            players_to_steal_from = [p for p in range(1, self.no_of_players + 1) if (p != left_player and p != right_player)] 
        else:
            players_to_steal_from = [p for p in range(1, self.no_of_players + 1)]

        final_list = []
        for p in players_to_steal_from:
            if self.players[p].chips > 0:
                final_list.append(p)
        
        return final_list

    def _check_for_winner(self):
        for p in self.players:
            if self.players[p].chips == self.no_of_chips - self.chips_in_centre_pile:
                self.winner = p
                self.end_of_game = True
                print(f"GAME OVER!!! Player {p} has won!!")

    def play_turn(self, player_id):
        player = self.players[player_id]
        if player.chips > 0:
            dices = [random.choice(self.dice) for _ in range(max(player.chips, 3))]
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


class Player:
    def __init__(self, id, chips, name='', aggression_level=1):
        self.id = id
        self.chips = chips
        self.name = name
        self.aggression_level = aggression_level
        # 1 = Only take from neighbouring opposition.
        # 2 = Take from any oppositon.
        # 3 = Only take from non-neighbouring opposition.
    
    def __repr__(self):
        return f"Player {self.name} ({self.id}) --> Number of chips: {self.chips}"


class History:
    def __init__(self, no_of_players):
        self.no_of_players = no_of_players

    @property
    def columns(self):
        return [f"p{i}" for i in range(1, self.no_of_players + 1)] + ['centre_pile', 'player_in_play', 'dices']
    
    @property
    def data(self):
        return {col: [] for col in self.columns}
    
    def to_dataframe(self):
        return pd.DataFrame(self.data)

    def to_csv(self, fname):
        self.to_dataframe().to_csv(fname)


class Statistics:
    def __init__(self, data):
        self.data = data

    def __getitem__(self, key):
        return self.data.iloc[key]
    
    @classmethod
    def from_csv(cls, fname):
        _data = pd.read_csv(fname)
        _data = _data.drop("Unnamed: 0", axis=1)
        
        dice_list = []
        for row in _data.dices:
            try:
                new_row = row.strip('][').replace("'", "").split(', ')
            except AttributeError:
                new_row = np.nan
            dice_list.append(new_row)

        _data.dices = dice_list

        return cls(_data)
    
    @property
    def final_stats(self):
        return {
            'winner': self.winner,
            'winner_pile': self[-1][f"p{self.winner}"],
            'centre_pile': self[-1].centre_pile,
            'game_length': self.game_length
        }
    
    @property
    def no_of_players(self):
        players = 0
        for col in self.data.columns:
            if col.startswith('p'):
                try:
                    int(col[-1])
                    players += 1
                except:
                    pass
        return players

    @property
    def game_length(self):
        return len(self.data) - 1
    
    @property
    def winner(self):
        final_turn = self[-1]
        for id in range(1, self.no_of_players + 1):
            if final_turn[f"p{id}"] != 0:
                return id

    def search_dice_patterns(self, dice_1, dice_2, dice_3):
        column = self.data['dices']

        target = [dice_1, dice_2, dice_3]
        return [i for i, row in enumerate(column) if row == target] 
