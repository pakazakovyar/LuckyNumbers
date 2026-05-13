from game import LuckyNumbersLogic
import os

# with open("params.txt", "r") as f:
#     LOW_COL_PENALTY, LARGE_PENALTY= map(int, f.readline().split())

class BotComparator(LuckyNumbersLogic):
    def __init__(self):
        super().__init__()

    def old_bot_turn(self):
        # if self.game_over: return
        best_move = None

        for idx, val in enumerate(self.opened_numbers):
            moves = self.get_valid_moves(self.player_field, val)
            for i, j in moves:
                score = self.evaluate_placement(i, j, val)

                if self.player_field[i][j] != 0:
                    old_score = self.evaluate_placement(i, j, self.player_field[i][j])
                    if score < old_score - 2:
                        if best_move is None or score < best_move[3]:
                            best_move = (idx, i, j, score)
                elif score < 5:
                    if best_move is None or score < best_move[3]:
                        best_move = (idx, i, j, score)

        if best_move is None and self.closed_numbers:
            drawn_tile = self.closed_numbers.pop(0)
            moves = self.get_valid_moves(self.player_field, drawn_tile)

            if not moves:
                self.opened_numbers.append(drawn_tile)
                self.message = f"Бот взял из колоды {drawn_tile} и сбросил его."
            else:
                best_tile_move = None
                for r, c in moves:
                    score = self.evaluate_placement(r, c, drawn_tile)
                    if self.player_field[r][c] != 0:
                        old_score = self.evaluate_placement(r, c, self.player_field[r][c])
                        if score < old_score:
                            if best_tile_move is None or score < best_tile_move[2]:
                                best_tile_move = (r, c, score)
                    else:
                        if best_tile_move is None or score < best_tile_move[2]:
                            best_tile_move = (r, c, score)

                if best_tile_move:
                    r, c, _ = best_tile_move
                    old_val = self.player_field[r][c]
                    self.player_field[r][c] = drawn_tile
                    if old_val != 0:
                        self.opened_numbers.append(old_val)
                        self.message = f"Бот вытянул {drawn_tile} и заменил им {old_val}."
                    else:
                        self.message = f"Бот вытянул {drawn_tile} и поставил в [{r}, {c}]."
                else:
                    self.opened_numbers.append(drawn_tile)
                    self.message = f"Бот вытянул {drawn_tile} и решил сбросить."
        elif best_move:
            idx, r, c, _ = best_move
            val = self.opened_numbers.pop(idx)
            old_val = self.player_field[r][c]
            self.player_field[r][c] = val
            if old_val != 0:
                self.opened_numbers.append(old_val)
                self.message = f"Бот взял {val} со стола и заменил им {old_val}."
            else:
                self.message = f"Бот взял {val} со стола и поставил в [{r}, {c}]."

        # if self.is_end(self.player_field):
        #     self.game_over = True
        #     self.winner = "bot"
        #     self.message = "БОТ ПОБЕДИЛ!"

    def bot_turn(self):
        # if self.game_over: return
        best_move = None

        for idx, val in enumerate(self.opened_numbers):
            moves = self.get_valid_moves(self.bot_field, val)
            for r, c in moves:
                dist_score = self.evaluate_placement(r, c, val)
                prob_penalty = self.get_probability_penalty(self.bot_field, r, c, val)
                score = dist_score + prob_penalty

                if self.bot_field[r][c] != 0:
                    old_score = self.evaluate_placement(r, c, self.bot_field[r][c])
                    if score < old_score - self.replace_title_diff:
                        if best_move is None or score < best_move[3]:
                            best_move = (idx, r, c, score)
                elif score < self.max_title_diff:
                    if best_move is None or score < best_move[3]:
                        best_move = (idx, r, c, score)

        if best_move is None and self.closed_numbers:
            drawn_tile = self.closed_numbers.pop(0)
            self.cards_count[drawn_tile] -= 1
            moves = self.get_valid_moves(self.bot_field, drawn_tile)

            if not moves:
                self.opened_numbers.append(drawn_tile)
                self.message = f"Бот взял из колоды {drawn_tile} и сбросил его."
            else:
                best_tile_move = None
                for r, c in moves:
                    score = self.evaluate_placement(r, c, drawn_tile)
                    if self.bot_field[r][c] != 0:
                        old_score = self.evaluate_placement(r, c, self.bot_field[r][c])
                        if score < old_score:
                            if best_tile_move is None or score < best_tile_move[2]:
                                best_tile_move = (r, c, score)
                    else:
                        if best_tile_move is None or score < best_tile_move[2]:
                            best_tile_move = (r, c, score)

                if best_tile_move:
                    r, c, _ = best_tile_move
                    old_val = self.bot_field[r][c]
                    self.bot_field[r][c] = drawn_tile
                    if old_val != 0:
                        self.opened_numbers.append(old_val)
                        self.message = f"Бот вытянул {drawn_tile} и заменил им {old_val}."
                    else:
                        self.message = f"Бот вытянул {drawn_tile} и поставил в [{r}, {c}]."
                else:
                    self.opened_numbers.append(drawn_tile)
                    self.message = f"Бот вытянул {drawn_tile} и решил сбросить."
        elif best_move:
            idx, r, c, _ = best_move
            val = self.opened_numbers.pop(idx)
            old_val = self.bot_field[r][c]
            self.bot_field[r][c] = val
            if old_val != 0:
                self.opened_numbers.append(old_val)
                self.message = f"Бот взял {val} со стола и заменил им {old_val}."
            else:
                self.message = f"Бот взял {val} со стола и поставил в [{r}, {c}]."

        # if self.is_end(self.bot_field):
        #     self.game_over = True
        #     self.winner = "bot"
        #     self.message = "БОТ ПОБЕДИЛ!"
        if self.is_end(self.bot_field):
            self.message = "Бот завершил свое поле!"


def run_simulation(low_p, large_p, low_less, high_less, max_title, replace_title, num_games=100):
    new_bot_wins = 0
    old_bot_wins = 0
    draws = 0

    for _ in range(num_games):
        game = BotComparator()
        game.low_penalty = low_p
        game.large_penalty = large_p
        game.low_remaining_less = low_less
        game.high_remaining_less = high_less
        game.max_title_diff = max_title
        game.replace_title_diff = replace_title


        while not game.game_over and game.closed_numbers:
            game.old_bot_turn()
            game.bot_turn()
            old_finished = game.is_end(game.player_field)
            new_finished = game.is_end(game.bot_field)

            if old_finished or new_finished:
                game.game_over = True
                if old_finished and new_finished:
                    draws += 1
                elif new_finished:
                    new_bot_wins += 1
                else:
                    old_bot_wins += 1
                break

    total_rate = (new_bot_wins / num_games) * 100
    return total_rate, (old_bot_wins, new_bot_wins, draws)


import csv


def optimize():
    # Наборы для теста
    low_range = range(6)
    large_range = range(10)
    low_less_range = range(6)
    high_less_range = range(6)
    max_title_diff = range(6)
    replace_title_diff = range(6)
    all_results = []
    c = 0
    for low in low_range:
        for large in large_range:
            for l_less in low_less_range:
                for h_less in high_less_range:
                    for max_title in max_title_diff:
                        for replace_title in replace_title_diff:
                            if large <= low or l_less >= h_less or max_title >= replace_title:
                                continue
                            c+=1
                            print(c)

                            rate, stats = run_simulation(low, large, l_less, h_less, max_title,replace_title , num_games=100)
                            old_w, new_w, drw = stats
                            all_results.append({
                                'low_p': low,
                                'large_p': large,
                                'low_less': l_less,
                                'high_less': h_less,
                                "max_title": max_title,
                                'replace_title': replace_title,
                                'win_rate': rate,
                                'old_wins': old_w,
                                'new_wins': new_w,
                                'draws': drw
                            })

    all_results.sort(key=lambda x: x['win_rate'], reverse=True)

    csv_file = "calibration_results.csv"
    with open(csv_file, mode='w', newline='', encoding='utf-8') as f:
        fieldnames = ['low_p', 'large_p', 'low_less', 'high_less', "max_title", 'replace_title', 'win_rate',
                      'old_wins', 'new_wins', 'draws']
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(all_results)


if __name__ == "__main__":
    optimize()