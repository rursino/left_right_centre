import numpy as np
import pandas as pd


class History:
    def __init__(self, no_of_players):
        self.no_of_players = no_of_players
        self.data = {col: [] for col in self.columns}

    @property
    def columns(self):
        return [f"p{i}" for i in range(1, self.no_of_players + 1)] + ['centre_pile', 'player_in_play', 'dices']
    
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