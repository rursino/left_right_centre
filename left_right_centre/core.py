from numpy import random
import numpy as np

class Game:
    def __init__(self, no_of_players=3, no_of_chips=100):
        self.no_of_players = no_of_players
        self.no_of_chips = no_of_chips
        self.dice = ['L', 'L', 'R', 'R', 'd', 'pd']
        self.players = {i : Player(i, self._distribute_chips()) for i in range(1, no_of_players + 1)}

    def _distribute_chips(self):
        return no_of_chips // no_of_players


class Player:
    def __init__(self, id, chips):
        self.id = id
        self.chips = chips