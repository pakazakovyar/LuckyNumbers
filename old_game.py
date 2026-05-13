from random import shuffle, choice


class LuckyNumbersLogic:
    def __init__(self):
        self.closed_numbers = self.generate_closed_numbers()
        self.player_field = [[0] * 4 for _ in range(4)]
        self.bot_field = [[0] * 4 for _ in range(4)]
        self.fill_diagonal(self.player_field)
        self.fill_diagonal(self.bot_field)

        self.opened_numbers = []
        self.opened_numbers.append(self.closed_numbers.pop(0))

        self.current_tile = None
        self.game_over = False
        self.winner = None
        self.message = "Игра началась! Сделайте первый ход."



    def generate_closed_numbers(self):
        numbers = list(range(1, 21)) * 2
        shuffle(numbers)
        return numbers

    def fill_diagonal(self, field):
        start_numbers = []
        for _ in range(4):
            start_numbers.append(self.closed_numbers.pop(0))
        start_numbers.sort()
        for i in range(4):
            field[i][i] = start_numbers[i]

    def is_valid_placement(self, field, row, col, value):
        for j in range(4):
            if j == col:
                continue
            cur_value = field[row][j]
            if cur_value == 0:
                continue
            if j < col and cur_value >= value:
                return False
            if j > col and cur_value <= value:
                return False

        for i in range(4):
            if i == row:
                continue
            cur_value = field[i][col]
            if cur_value == 0:
                continue
            if i < row and cur_value >= value:
                return False
            if i > row and cur_value <= value:
                return False
        return True

    def get_valid_moves(self, field, tile_value):
        moves = []
        for i in range(4):
            for j in range(4):
                if self.is_valid_placement(field, i, j, tile_value):
                    moves.append((i, j))
        return moves

    def is_end(self, field):
        for row in field:
            if 0 in row:
                return False
        return True


    def evaluate_placement(self, row, col, val):
        target = 1 + (row + col) * (19 / 6)
        return abs(val - target)

    def bot_turn(self):
        if self.game_over: return
        best_move = None

        for idx, val in enumerate(self.opened_numbers):
            moves = self.get_valid_moves(self.bot_field, val)
            for i, j in moves:
                score = self.evaluate_placement(i, j, val)

                if self.bot_field[i][j] != 0:
                    old_score = self.evaluate_placement(i, j, self.bot_field[i][j])
                    if score < old_score - 2:
                        if best_move is None or score < best_move[3]:
                            best_move = (idx, i, j, score)
                elif score < 5:
                    if best_move is None or score < best_move[3]:
                        best_move = (idx, i, j, score)

        if best_move is None and self.closed_numbers:
            drawn_tile = self.closed_numbers.pop(0)
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

        if self.is_end(self.bot_field):
            self.game_over = True
            self.winner = "bot"
            self.message = "БОТ ПОБЕДИЛ!"

    def take_tile_from_deck(self):
        if self.game_over:
            self.message = "Игра окончена!"
            return False
        if self.current_tile is not None:
            self.message = "У вас уже есть число в руках!"
            return False
        if not self.closed_numbers:
            self.message = "Колода пуста!"
            return False

        self.current_tile = self.closed_numbers.pop(0)
        self.message = f"Вы взяли число: {self.current_tile}"
        return True

    def take_tile_from_table(self, index):
        if self.game_over:
            self.message = "Игра окончена!"
            return False
        if self.current_tile is not None:
            self.message = "Сначала поставьте или сбросьте текущее число!"
            return False
        if not (0 <= index < len(self.opened_numbers)):
            self.message = "Этого числа больше нет на столе."
            return False

        self.current_tile = self.opened_numbers.pop(index)
        self.message = f"Вы взяли число со стола: {self.current_tile}"
        return True

    def place_tile(self, row, col):
        if self.game_over:
            self.message = "Игра окончена!"
            return False
        if self.current_tile is None:
            self.message = "Сначала возьмите число!"
            return False

        valid_moves = self.get_valid_moves(self.player_field, self.current_tile)
        if (row, col) not in valid_moves:
            self.message = "Сюда нельзя поставить это число!"
            return False

        old_val = self.player_field[row][col]
        self.player_field[row][col] = self.current_tile
        placed_tile = self.current_tile

        if old_val != 0:
            self.opened_numbers.append(old_val)
            self.message = f"Вы заменили {old_val} на {placed_tile}."
        else:
            self.message = f"Вы поставили {placed_tile}."

        self.current_tile = None

        if self.is_end(self.player_field):
            self.game_over = True
            self.winner = "player"
            self.message = "ПОЗДРАВЛЯЮ! Вы победили!"
        else:
            self.bot_turn()

        return True

    def pass_tile(self):
        if self.game_over:
            self.message = "Игра окончена!"
            return False
        if self.current_tile is None:
            self.message = "У вас нет числа, которое можно сбросить."
            return False

        passed_tile = self.current_tile
        self.opened_numbers.append(self.current_tile)
        self.message = f"Вы сбросили {passed_tile} на стол."
        self.current_tile = None

        self.bot_turn()
        return True

    def get_state(self):
        return {
            "player_field": self.player_field,
            "bot_field": self.bot_field,
            "opened_numbers": self.opened_numbers,
            "closed_count": len(self.closed_numbers),
            "current_tile": self.current_tile,
            "game_over": self.game_over,
            "winner": self.winner,
            "message": self.message
        }