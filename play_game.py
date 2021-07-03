from left_right_centre import core
from numpy import random
import csv

no_of_players = 14
no_of_chips = no_of_players * 100

g = core.Game(no_of_players, no_of_chips)
g.play_game()
