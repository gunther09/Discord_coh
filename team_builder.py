from itertools import combinations

def build_balanced_teams(players):
    # Sort players by MaxAxis and MaxAllies
    players_sorted = sorted(players, key=lambda x: (int(x['MaxAxis'].replace(',', '')), int(x['MaxAllies'].replace(',', ''))), reverse=True)
    best_diff = float('inf')
    best_team_1 = best_team_2 = None

    for comb in combinations(players_sorted, len(players_sorted) // 2):
        team_1 = list(comb)
        team_2 = [player for player in players_sorted if player not in team_1]
        sum_team_1 = sum(int(player['MaxAxis'].replace(',', '')) for player in team_1)
        sum_team_2 = sum(int(player['MaxAllies'].replace(',', '')) for player in team_2)
        diff = abs(sum_team_1 - sum_team_2)
        if diff < best_diff:
            best_diff = diff
            best_team_1, best_team_2 = team_1, team_2

    return best_team_1, best_team_2
