from left_right_centre import core
import ipdb

g = core.Statistics("results/history.csv")

# Chance of getting patterns
# L, R, C, pd happen once
# d happens twice.
def pattern_pr():
    game_length = g.game_length()
    patterns = [
        (['L', 'L', 'R'], (1/6)**3),
        (['pd', 'pd', 'pd'], (1/6)**3),
        (['d', 'd', 'd'], (2/6)**3)
    ]

    results = {}
    for pattern, expected in patterns:
        chance = len(g.search_dice_patterns(*pattern)) / game_length
        results[str(pattern)] = (chance, expected)

    return results

print(f"Pattern\t\t\tChance\tExpected")
pattern_results = pattern_pr()
for pattern in pattern_results:
    result = pattern_results[pattern]
    print(f"{pattern}:\t{result[0]:.3f}\t{result[1]:.3f}")

print("Game length:", g.game_length())

#ipdb.set_trace()
