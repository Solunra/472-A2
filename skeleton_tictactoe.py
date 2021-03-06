# based on code from https://stackabuse.com/minimax-and-alpha-beta-pruning-in-python
import time
import math
import random


class Game:
    MINIMAX = 0
    ALPHABETA = 1
    HUMAN = 2
    AI = 3
    INITIAL_HEURISTIC_SCORE = 9999999999999

    # n = game_size, b = blocks, s = win_length
    def __init__(self, recommend=True, game_size=3, blocks=0, win_length=3, max_execution_time=7, block_positions=None):
        self.turn_start_time = 0
        self.max_execution_time = max_execution_time
        self.game_size = game_size
        self.game_blocks = blocks
        self.win_length = win_length
        self.logger = open(f'logs\\gameTrace-{game_size}{blocks}{win_length}{max_execution_time}.txt', 'w')
        self.block_positions = block_positions
        self.initialize_game()
        self.recommend = recommend
        self.alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        self.logger.write(f'n = {game_size} b = {blocks} s = {win_length} t = {max_execution_time}\n')
        self.depths = []
        self.depth_dictionary = {}
        self.depths_memory = []
        self.depth_dictionary_memory = []
        self.evaluation_time = []
        self.ard_memory = []

    def initialize_game(self, is_first_init=True):
        game = []
        for i in range(self.game_size):
            game.append(['.'] * self.game_size)
        self.current_state = game
        # Player X always plays first
        self.player_turn = 'X'

        # Generate each blocks
        list_of_blocks = []
        if self.block_positions is None:
            while len(list_of_blocks) != self.game_blocks:
                new_position = (random.randint(0, self.game_size - 1), random.randint(0, self.game_size - 1))
                if new_position not in list_of_blocks:
                    list_of_blocks.append(new_position)
        else:
            list_of_blocks = self.block_positions

        # Place each blocks
        for x, y in list_of_blocks:
            self.current_state[x][y] = '*'

        # Output to file
        if is_first_init:
            self.logger.write(f'Blocks:{list_of_blocks}\n')

    def draw_board(self):

        print()
        row = '  '
        for board in range(0, self.game_size):
            row = row + self.alphabet[board]
        print(row)
        self.logger.write(f'{row}\n')

        game_row = ''
        for y in range(0, self.game_size):
            game_row = game_row + f'{y} '
            for x in range(0, self.game_size):
                game_row = game_row + F'{self.current_state[x][y]}'
            print(game_row)
            self.logger.write(f'{game_row}\n')
            game_row = ''
            print(end="")
        print()
        self.logger.write('\n')

    def is_valid(self, px, py):
        if px < 0 or px > self.game_size - 1 or py < 0 or py > self.game_size - 1:
            return False
        elif self.current_state[px][py] != '.':
            return False
        else:
            return True

    def h1_num_own_tiles(self):
        h_score = 0
        num_tiles = 0
        win_length = self.win_length
        game_state_clone = self.current_state.copy()
        game_state_vertical_clone = list(map(list, zip(*game_state_clone)))

        # Horizontal win
        for row in game_state_clone:
            num_tiles = 0
            for index, symbol in enumerate(row):
                if symbol == 'O':
                    num_tiles += 1
            h_score += win_length - num_tiles

        # Vertical win
        for col in game_state_vertical_clone:
            num_tiles = 0
            for index, symbol in enumerate(col):
                if symbol == 'O':
                    num_tiles += 1
            h_score += win_length - num_tiles

        # Diagonal win
        # height is a check. For diagonals of length 3 with n of 5, the diagonal can start on y = 0, 1, or 2
        skip_middle = False
        skip_number = -1
        if self.game_size % 2 != 0:
            skip_middle = True
            skip_number = self.game_size % 2
        for height in range(self.game_size - win_length + 1):
            num_tiles = 0
            # same logic but with rows
            for row_value in range(self.game_size):
                num_tiles = 0
                if skip_middle and row_value == skip_number:
                    continue
                temp_num_tiles = 0
                if game_state_clone[height][row_value] == 'O':
                    temp_num_tiles = 1
                if row_value < math.floor(self.game_size / 2):
                    # from left to right
                    for length in range(1, win_length):
                        if (row_value + length) >= self.game_size:
                            continue
                        if game_state_clone[height + length][row_value + length] == 'O':
                            num_tiles += 1
                else:
                    # from right to left
                    for length in range(1, win_length):
                        if (row_value + length) < 0:
                            continue
                        if game_state_clone[height + length][row_value - length] == 'O':
                            num_tiles += 1
                h_score += win_length - num_tiles - temp_num_tiles

        # Debugging
        # print('****')
        # for row in game_state_clone:
        # 	print(row)
        # print(h_score)
        # print('****')

        return h_score

    def h2_bunched_symbols(self):
        h_score = 0
        game_state_clone = self.current_state.copy()
        game_state_vertical_clone = list(map(list, zip(*game_state_clone)))

        # Horizontal win
        for row in game_state_clone:
            num_tiles = 0
            for index, symbol in enumerate(row):
                if symbol == 'O':
                    num_tiles += 1
                if symbol == 'X':
                    num_tiles -= 1
                if symbol == '*' and num_tiles < self.win_length:
                    num_tiles = 0
            h_score += math.copysign(math.pow(100, num_tiles - self.win_length), num_tiles)
        # Vertical win
        for col in game_state_vertical_clone:
            num_tiles = 0
            for index, symbol in enumerate(col):
                if symbol == 'O':
                    num_tiles += 1
                if symbol == 'X':
                    num_tiles -= 1
                if symbol == '*' and num_tiles < self.win_length:
                    num_tiles = 0
            h_score += math.copysign(math.pow(100, num_tiles - self.win_length), num_tiles)
        # Diagonal win
        skip_middle = False
        skip_number = -1
        if self.game_size % 2 != 0:
            skip_middle = True
            skip_number = self.game_size % 2
        for height in range(self.game_size - self.win_length + 1):
            num_tiles = 0
            # same logic but with rows
            for row_value in range(self.game_size):
                num_tiles = 0
                if skip_middle and row_value == skip_number:
                    continue
                temp_num_tiles = 0
                if game_state_clone[height][row_value] == 'O':
                    temp_num_tiles = 1
                elif game_state_clone[height][row_value] == 'X':
                    temp_num_tiles = -1
                if row_value < math.floor(self.game_size / 2):
                    # from left to right
                    for length in range(1, self.win_length):
                        if (row_value + length) >= self.game_size:
                            continue
                        if game_state_clone[height + length][row_value + length] == 'O':
                            num_tiles += 1
                        if game_state_clone[height + length][row_value + length] == 'X':
                            num_tiles -= 1
                        if game_state_clone[height + length][row_value + length] == '*' and num_tiles < self.win_length:
                            num_tiles -= 1
                else:
                    # from right to left
                    for length in range(1, self.win_length):
                        if (row_value + length) < 0:
                            continue
                        if game_state_clone[height + length][row_value - length] == 'O':
                            num_tiles += 1
                        if game_state_clone[height + length][row_value - length] == 'X':
                            num_tiles -= 1
                        if game_state_clone[height + length][row_value - length] == '*' and num_tiles < self.win_length:
                            num_tiles -= 1
                h_score += math.copysign(math.pow(100, num_tiles - self.win_length), num_tiles)
        return h_score

    def is_end(self):
        """Returns the name of the player that won, . for a tie or None if the game hasn't ended"""
        # Vertical win
        potential_winner = self.verify_vertical()
        if potential_winner != '.':
            return potential_winner
        # Horizontal win
        potential_winner = self.verify_horizontal()
        if potential_winner != '.':
            return potential_winner
        # Verify diagonal win
        potential_winner = self.verify_diagonals()
        if potential_winner != '.':
            return potential_winner
        # Is whole board full?
        for i in range(0, self.game_size):
            for j in range(0, self.game_size):
                # There's an empty field, we continue the game
                if self.current_state[i][j] == '.':
                    return None
        # It's a tie!
        return '.'

    def verify_horizontal(self):
        game_state_clone = self.current_state.copy()
        return self.verify_per_row(game_state_clone)

    def verify_vertical(self):
        # transposing the game state, then using verify horizontal
        game_state_clone = self.current_state.copy()
        # transposing the game state 2D list: https://stackoverflow.com/questions/6473679/transpose-list-of-lists
        game_state_clone = list(map(list, zip(*game_state_clone)))
        return self.verify_per_row(game_state_clone)

    def verify_per_row(self, game_state):
        same_symbol_count = 0
        current_player = ''
        for row in game_state:
            for index, symbol in enumerate(row):
                if self.win_length - same_symbol_count > self.game_size - index:
                    break
                if symbol == '*' or symbol == '.':
                    current_player = ''
                    same_symbol_count = 0
                elif symbol == current_player:
                    same_symbol_count += 1
                else:
                    current_player = symbol
                    same_symbol_count = 1

                if same_symbol_count == self.win_length:
                    return current_player
            same_symbol_count = 0
        return '.'

    # programmatically verify diagonals and count with relation to self.win_length
    # [[X X X],
    #  [O O O],
    #  [X X X]]
    def verify_diagonals(self):
        # height is a check. For diagonals of length 3 with n of 5, the diagonal can start on y = 0, 1, or 2
        same_count = 0
        potential_winner = '.'
        skip_middle = False
        skip_number = -1
        if self.game_size % 2 != 0:
            skip_middle = True
            skip_number = self.game_size % 2
        for height in range(self.game_size - self.win_length + 1):
            # same logic but with rows
            for row_value in range(self.game_size):
                if skip_middle and row_value == skip_number:
                    continue
                if self.current_state[height][row_value] != '.' and self.current_state[height][row_value] != '*':
                    potential_winner = self.current_state[height][row_value]
                    same_count = 1
                    if row_value < math.floor(self.game_size / 2):
                        # from left to right
                        for length in range(1, self.win_length):
                            if (row_value + length) >= self.game_size:
                                continue
                            if potential_winner == self.current_state[height + length][row_value + length]:
                                same_count = same_count + 1
                                if same_count == self.win_length:
                                    return potential_winner
                    else:
                        # from right to left
                        for length in range(1, self.win_length):
                            if (row_value - length) < 0:
                                continue
                            if potential_winner == self.current_state[height + length][row_value - length]:
                                same_count = same_count + 1
                                if same_count == self.win_length:
                                    return potential_winner
        return '.'

    def check_end(self):
        self.result = self.is_end()
        # Printing the appropriate message if the game has ended
        if self.result != None:
            if self.result == 'X':
                print('The winner is X! :v')
                self.logger.write('The winner is X!')
            elif self.result == 'O':
                print('The winner is O! :v')
                self.logger.write('The winner is O!')
            elif self.result == '.':
                print("It's a tie! :v")
                self.logger.write('It\'s a tie!')
            self.initialize_game(False)
        return self.result

    def input_move(self):
        while True:
            print(F'Player {self.player_turn}, enter your move:')
            x_char = input('enter the x coordinate: ')
            py = int(input('enter the y coordinate: '))
            px = self.alphabet.index(x_char)
            print(str(px))
            if self.is_valid(px, py):
                return (px, py)
            else:
                print('The move is not valid! Try again.')

    def switch_player(self):
        if self.player_turn == 'X':
            self.player_turn = 'O'
        elif self.player_turn == 'O':
            self.player_turn = 'X'
        return self.player_turn

    def minimax(self, heuristic, max_depth, max=False, current_depth=0):
        # if you've exceeded the time limit, the AI loses
        if time.time() - self.turn_start_time > self.max_execution_time:
            raise TimeoutError
        # Minimizing for 'X' and maximizing for 'O'
        # Possible values are:
        # -1 - win for 'X'
        # 0  - a tie
        # 1  - loss for 'X'
        # We're initially setting it to 2 or -2 as worse than the worst case:

        # list for ARD
        depths_list = []

        value = Game.INITIAL_HEURISTIC_SCORE
        if max:
            value = -Game.INITIAL_HEURISTIC_SCORE
        x = None
        y = None
        result = self.is_end()
        if result == 'X':
            return -1, x, y, current_depth
        elif result == 'O':
            return 1, x, y, current_depth
        elif result == '.':
            return 0, x, y, current_depth

        for i in range(0, self.game_size):
            for j in range(0, self.game_size):
                if self.current_state[i][j] == '.':
                    if max:
                        self.current_state[i][j] = 'O'
                        if current_depth < max_depth:
                            (v, _, _, d) = self.minimax(heuristic, max_depth, max=False,
                                                        current_depth=current_depth + 1)
                            if d is not None:
                                depths_list.append(d)
                        else:
                            # run heuristic on this intermediate state (get score for move at this position)
                            v = heuristic()
                        if v > value:
                            value = v
                            x = i
                            y = j
                    else:
                        self.current_state[i][j] = 'X'
                        if current_depth < max_depth:
                            (v, _, _, d) = self.minimax(heuristic, max_depth, max=True, current_depth=current_depth + 1)
                            if d is not None:
                                depths_list.append(d)
                        else:
                            # run heuristic on this intermediate state (get score for move at this position)
                            v = heuristic()
                        if v < value:
                            value = v
                            x = i
                            y = j
                    true_depth = current_depth + 1
                    self.depths.append(true_depth)

                    if true_depth not in self.depth_dictionary.keys():
                        self.depth_dictionary[true_depth] = 1
                    else:
                        self.depth_dictionary[true_depth] += 1

                    self.current_state[i][j] = '.'

        if len(depths_list) == 0:
            return value, x, y, current_depth

        avg_depth_for_node = sum(depths_list) / len(depths_list)
        return value, x, y, avg_depth_for_node

    def alphabeta(self, heuristic, max_depth, alpha=-2, beta=2, max=False, current_depth=0):
        # if you've exceeded the time limit, the AI loses
        if time.time() - self.turn_start_time > self.max_execution_time:
            raise TimeoutError
        # Minimizing for 'X' and maximizing for 'O'
        # Possible values are:
        # -1 - win for 'X'
        # 0  - a tie
        # 1  - loss for 'X'
        # We're initially setting it to 2 or -2 as worse than the worst case:

        # list for ARD
        depths_list = []

        value = Game.INITIAL_HEURISTIC_SCORE
        if max:
            value = -Game.INITIAL_HEURISTIC_SCORE
        x = None
        y = None
        result = self.is_end()
        if result == 'X':
            return -1, x, y, current_depth
        elif result == 'O':
            return 1, x, y, current_depth
        elif result == '.':
            return 0, x, y, current_depth
        for i in range(0, self.game_size):
            for j in range(0, self.game_size):
                if self.current_state[i][j] == '.':
                    d_value = 0
                    if max:
                        self.current_state[i][j] = 'O'
                        if current_depth < max_depth:
                            (v, _, _, d) = self.alphabeta(heuristic, max_depth, alpha, beta, max=False,
                                                          current_depth=current_depth + 1)
                            d_value = d
                            if d != 0:
                                depths_list.append(d)
                        else:
                            v = heuristic()
                        if v > value:
                            value = v
                            x = i
                            y = j
                    else:
                        self.current_state[i][j] = 'X'
                        if current_depth < max_depth:
                            (v, _, _, d) = self.alphabeta(heuristic, max_depth, alpha, beta, max=True,
                                                          current_depth=current_depth + 1)
                            d_value = d
                            if d != 0:
                                depths_list.append(d)
                        else:
                            v = heuristic()
                        if v < value:
                            value = v
                            x = i
                            y = j
                    true_depth = current_depth + 1
                    self.depths.append(true_depth)

                    if (true_depth not in self.depth_dictionary.keys()):
                        self.depth_dictionary[true_depth] = 1
                    else:
                        self.depth_dictionary[true_depth] += 1

                    self.current_state[i][j] = '.'
                    if max:
                        if value >= beta:
                            return value, x, y, d_value
                        if value > alpha:
                            alpha = value
                    else:
                        if value <= alpha:
                            return value, x, y, d_value
                        if value < beta:
                            beta = value

        if len(depths_list) == 0:
            return value, x, y, current_depth

        avg_depth_for_node = sum(depths_list) / len(depths_list)
        return value, x, y, avg_depth_for_node

    def play(self, algo=None, player_x=None, player_o=None, player_x_heuristic='h1', player_o_heuristic='h1',
             player_x_max_depth=5, player_o_max_depth=5):
        game_metrics = {}
        if algo is None:
            algo = self.ALPHABETA
        if player_x is None:
            player_x = self.HUMAN
        if player_o is None:
            player_o = self.HUMAN

        if player_x_heuristic == 'h1':
            player_x_heuristic = self.h1_num_own_tiles
        else:
            player_x_heuristic = self.h2_bunched_symbols
        if player_o_heuristic == 'h1':
            player_o_heuristic = self.h1_num_own_tiles
        else:
            player_o_heuristic = self.h2_bunched_symbols

        self.logger.write(f'Player 1: {player_x} d={player_x_max_depth} a={algo} e={player_x_heuristic.__name__} \n')
        self.logger.write(f'Player 2: {player_o} d={player_o_max_depth} a={algo} e={player_o_heuristic.__name__} \n')

        moves_counter = 0

        while True:
            self.draw_board()
            winner = self.check_end()
            if winner:
                if winner == 'O':
                    game_metrics["o_wins"] = 1
                    game_metrics["x_wins"] = 0
                    if player_o_heuristic.__name__ == self.h1_num_own_tiles.__name__:
                        game_metrics['h1_wins'] = 1
                        game_metrics['h2_wins'] = 0
                    else:
                        game_metrics['h1_wins'] = 0
                        game_metrics['h2_wins'] = 1
                elif winner == 'X':
                    game_metrics["o_wins"] = 0
                    game_metrics["x_wins"] = 1
                    if player_x_heuristic.__name__ == self.h1_num_own_tiles.__name__:
                        game_metrics['h1_wins'] = 1
                        game_metrics['h2_wins'] = 0
                    else:
                        game_metrics['h1_wins'] = 0
                        game_metrics['h2_wins'] = 1
                else:
                    game_metrics["o_wins"] = 0
                    game_metrics["x_wins"] = 0
                    game_metrics['h1_wins'] = 0
                    game_metrics['h2_wins'] = 0
                break
            start = time.time()
            try:
                self.turn_start_time = start
                if algo == self.MINIMAX:
                    if self.player_turn == 'X':
                        (_, x, y, ard) = self.minimax(player_x_heuristic, player_x_max_depth, max=False)
                    else:
                        (_, x, y, ard) = self.minimax(player_o_heuristic, player_o_max_depth, max=True)
                else:  # algo == self.ALPHABETA
                    if self.player_turn == 'X':
                        (m, x, y, ard) = self.alphabeta(player_x_heuristic, player_x_max_depth, max=False)
                    else:
                        (m, x, y, ard) = self.alphabeta(player_o_heuristic, player_o_max_depth, max=True)
                end = time.time()

            except TimeoutError:
                print("The current AI player ran out of time!")
                winner = self.switch_player()
                print(winner + " wins by default!")
                if winner == 'O':
                    game_metrics["o_wins"] = 1
                    game_metrics["x_wins"] = 0
                    if player_o_heuristic.__name__ == self.h1_num_own_tiles.__name__:
                        game_metrics['h1_wins'] = 1
                        game_metrics['h2_wins'] = 0
                    else:
                        game_metrics['h1_wins'] = 0
                        game_metrics['h2_wins'] = 1
                elif winner == 'X':
                    game_metrics["o_wins"] = 0
                    game_metrics["x_wins"] = 1
                    if player_x_heuristic.__name__ == self.h1_num_own_tiles.__name__:
                        game_metrics['h1_wins'] = 1
                        game_metrics['h2_wins'] = 0
                    else:
                        game_metrics['h1_wins'] = 0
                        game_metrics['h2_wins'] = 1
                else:
                    game_metrics["o_wins"] = 0
                    game_metrics["x_wins"] = 0
                    game_metrics['h1_wins'] = 0
                    game_metrics['h2_wins'] = 0
                break

            moves_counter += 1

            self.evaluation_time.append(end - start)

            if (self.player_turn == 'X' and player_x == self.HUMAN) or (
                    self.player_turn == 'O' and player_o == self.HUMAN):
                if self.recommend:
                    print(F'Evaluation time: {round(end - start, 7)}s')
                    print(F'Recommended move: x = {self.alphabet[x]}, y = {y}')
                (x, y) = self.input_move()
                self.logger.write(f'Real Player {self.player_turn} plays: x = {x}, y = {y}\n')
                self.logger.write(f'i Evaluation time: {round(end - start, 7)}s\n')

            if (self.player_turn == 'X' and player_x == self.AI) or (self.player_turn == 'O' and player_o == self.AI):
                print(F'Evaluation time: {round(end - start, 7)}s')
                print(F'Player {self.player_turn} under AI control plays: x = {self.alphabet[x]}, y = {y}')

                self.logger.write(
                    f'Player {self.player_turn} under AI control plays: x = {self.alphabet[x]}, y = {y}\n')
                self.logger.write(f'i Evaluation time: {round(end - start, 7)}s\n')

            # total num states / num states for each depth
            sum_states = sum(self.depth_dictionary.values())
            self.logger.write(f'ii Heuristics evaluations: {sum_states}\n')
            self.logger.write(f'iii Evaluations by depth: {self.depth_dictionary}\n')
            self.depth_dictionary_memory.append(self.depth_dictionary)
            self.depth_dictionary = {}

            # average depth
            avg_depth = sum(self.depths) / len(self.depths)
            self.logger.write(f'iv Average Evaluation Depth (AD) is: {avg_depth}\n')
            self.depths_memory.append(avg_depth)
            self.depths = []

            # average recursive depth
            self.logger.write(f'v Average Evaluation Recursive Depth (ARD) is: {ard}\n')
            self.ard_memory.append(ard)

            self.current_state[x][y] = self.player_turn
            self.switch_player()
        # 6 End-Game Heuristics

        self.logger.write(f'\n')
        if len(self.evaluation_time) == 0:
            self.evaluation_time.append(0)
        avg_eval_time = sum(self.evaluation_time) / len(self.evaluation_time)
        self.logger.write(f'6(b)i   Average evaluation time: {avg_eval_time}\n')
        game_metrics['avg_eval_time'] = avg_eval_time
        sum_of_all_searched_state = 0
        for depth_dict in self.depth_dictionary_memory:
            sum_of_all_searched_state += sum(depth_dict.values())
        game_metrics['sum_of_all_searched_state'] = sum_of_all_searched_state
        self.logger.write(f'6(b)ii  Total heuristic evaluations: {sum_of_all_searched_state}\n')
        total_depth = {}
        for depth_dict in self.depth_dictionary_memory:
            for depth, count in depth_dict.items():
                if depth not in total_depth.keys():
                    total_depth[depth] = count
                else:
                    total_depth[depth] += count
        game_metrics['total_depth'] = total_depth
        self.logger.write(f'6(b)iii Evaluations by depth: {total_depth}\n')
        if len(self.depths_memory) == 0:
            self.depths_memory.append(0)
        average_eval_depth = sum(self.depths_memory) / len(self.depths_memory)
        game_metrics['average_eval_depth'] = average_eval_depth
        self.logger.write(f'6(b)iv  Average evaluation depth: {average_eval_depth}\n')
        if len(self.ard_memory) == 0:
            self.ard_memory.append(0)
        average_recursion_depth = sum(self.ard_memory) / len(self.ard_memory)
        game_metrics['average_recursion_depth'] = average_recursion_depth
        self.logger.write(f'6(b)v   Average recursion depth: {average_recursion_depth}\n')
        game_metrics['moves_counter'] = moves_counter
        self.logger.write(f'6(b)vi  Total moves: {moves_counter}\n')
        return game_metrics


def main(choose_options=False, num_rounds=10, game_size=4, blocks=1, win_length=3, max_execution_time=20,
         player_o_heuristic='h1', player_x_heuristic='h2', player_x_max_depth=7, player_o_max_depth=7,
         algo=Game.ALPHABETA, block_positions=None):
    if choose_options:
        game_size = 0
        while game_size < 3 or game_size > 10:
            game_size = int(input(f'Please enter the game size: '))
            if game_size < 3 or game_size > 10:
                print(f'Game\'s size must be between 3 and 10')

        blocks = -1
        while blocks < 0 or blocks > (game_size * 2):
            blocks = int(input(f'Please enter the block amount: '))
            if blocks < 0 or blocks > (game_size * 2):
                print(f'Number of blocks must be between 0 and {game_size * 2}')

        win_length = 0
        while win_length < 3 or win_length > game_size:
            win_length = int(input(f'Please enter the win length: '))
            if win_length < 3 or win_length > game_size:
                print(f'Win length must be between 3 and {game_size}')
        try:
            g = Game(recommend=True, game_size=game_size, blocks=blocks, win_length=win_length)
            g.play(algo=Game.ALPHABETA, player_x=Game.HUMAN, player_o=Game.HUMAN, player_o_heuristic='h1',
                   player_x_heuristic='h2')
        finally:
            g.logger.close()
    else:
        game_metrics_list = []
        with open(f'logs\\scoreboard-{game_size}{blocks}{win_length}{max_execution_time}.txt', 'w') as round_file:
            round_file.write(
                f'Round parameters: game_size: {game_size} blocks: {blocks} win_length: {win_length} max_execution_time: {max_execution_time}\n')
            if algo == Game.ALPHABETA:
                algostr = 'AlphaBeta'
            else:
                algostr = 'Minimax'
            round_file.write(
                f'Player parameters: player_x_max_depth: {player_x_max_depth} player_o_max_depth: {player_o_max_depth} algo: {algostr} player_o_heuristic: {player_o_heuristic} player_x_heuristic: {player_x_heuristic}\n')
            round_file.write(f'Number of rounds: {num_rounds}\n')
            try:
                g = Game(recommend=True, blocks=blocks, block_positions=block_positions, game_size=game_size,
                         win_length=win_length,
                         max_execution_time=max_execution_time)
                for round in range(num_rounds):
                    bucket = player_o_heuristic
                    player_o_heuristic = player_x_heuristic
                    player_x_heuristic = bucket

                    game_metrics_list.append(
                        g.play(algo=algo, player_x=Game.AI, player_o=Game.AI, player_o_heuristic=player_o_heuristic,
                                player_x_heuristic=player_o_heuristic, player_o_max_depth=player_o_max_depth,
                                player_x_max_depth=player_x_max_depth))
            finally:
                g.logger.close()

            average_metrics = game_metrics_list[0]
            # averaging the entries in the dicts
            for metrics_index in range(1, len(game_metrics_list)):
                for key, value in game_metrics_list[metrics_index].items():
                    if type(value) is dict:
                        for inner_key, inner_value in value.items():
                            try:
                                average_metrics[key][inner_key] += inner_value
                            except KeyError:
                                average_metrics[key][inner_key] = inner_value
                    else:
                        average_metrics[key] += value

            for key, value in average_metrics.items():
                if type(value) is dict:
                    round_file.write(f'{key}:\n')
                    for inner_key, inner_value in value.items():
                        avg_inner_value = inner_value / len(average_metrics)
                        round_file.write(f'{inner_key}: {avg_inner_value}\n')
                else:
                    average_metric = value / len(game_metrics_list)
                    if key.endswith('wins'):
                        average_metric = str(average_metric * 100) + '%'
                    round_file.write(f'{key}: {average_metric}\n')
