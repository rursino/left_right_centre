from left_right_centre import core
from numpy import random
import csv
import argparse


parser = argparse.ArgumentParser(description="Play a game of Left, Right and Centre.")
parser.add_argument("-p", "--players", type=int, default=4, metavar="", help="Number of players.")
parser.add_argument("-c", "--chips", type=int, default=100, metavar="", help="Number of chips.")
parser.add_argument("-s", "--show", action="store_true", help="Show game history.")
args = parser.parse_args()


g = core.Game(args.players, args.chips)

g.play_game()
if args.show:
    print(g.history.to_dataframe())
    print('\n' + '='*50 + '\n')
    print(g.history.search(['pd', 'pd', 'pd'], 'dices'))
    print(g.history.iloc(56))