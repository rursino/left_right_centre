import numpy as np
import pandas as pd

from typing import List, Dict, Tuple


class History:
    def __init__(self, no_of_players: int):
        self.no_of_players = no_of_players
        self.data = {col: [] for col in self.columns}

    @property
    def columns(self) -> List[str]:
        return [f"p{i}" for i in range(1, self.no_of_players + 1)] + ['centre_pile', 'player_in_play', 'dices']
    
    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self.data)

    def to_csv(self, fname: str) -> pd.DataFrame:
        self.to_dataframe().to_csv(fname)


class Statistics:
    def __init__(self, data: pd.DataFrame):
        self.data = data

    def __getitem__(self, key: int):
        return self.data.iloc[key]
    
    @classmethod
    def from_csv(cls, fname: str):
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
    def final_stats(self) -> Dict[(str, int)]:
        return {
            'winner': str(self.winner),
            'winner_pile': str(self[-1][f"p{self.winner}"]),
            'centre_pile': str(self[-1].centre_pile),
            'game_length': str(self.game_length),
        }
    
    @property
    def no_of_players(self) -> int:
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
    def game_length(self) -> int:
        return len(self.data) - 1
    
    @property
    def winner(self) -> int:
        final_turn = self[-1]
        for id in range(1, self.no_of_players + 1):
            if final_turn[f"p{id}"] != 0:
                return id

    def search_dice_patterns(self, dice_1: str, dice_2: str, dice_3: str) -> List[int]:
        column = self.data['dices']

        target = [dice_1, dice_2, dice_3]
        return [i for i, row in enumerate(column) if row == target] 

    def pattern_pr(self, patterns: List[Tuple]) -> Dict[str, Tuple]:
        """ Returns empirical (actual) and theoritical (expected) probability of each dice pattern passed in from 'patterns'. """

        results = {}
        for pattern, expected in patterns:
            chance = len(self.search_dice_patterns(*pattern)) / self.game_length
            results[str(pattern)] = (chance, expected)

        return results
