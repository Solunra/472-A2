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
	def __init__(self, recommend=True, game_size=3, blocks=0, win_length=3, max_execution_time=7):
		self.turn_start_time = 0
		self.max_execution_time = max_execution_time
		self.game_size = game_size
		self.game_blocks = blocks
		self.win_length = win_length
		self.logger = open(f'gameTrace-{game_size}{blocks}{win_length}{max_execution_time}.txt', 'w')
		self.initialize_game()
		self.recommend = recommend
		self.alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
		self.logger.write(f'n = {game_size} b = {blocks} s = {win_length} t = {max_execution_time}\n')
		self.depths = []

	def initialize_game(self, is_first_init = True):
		game = []
		for i in range(self.game_size):
			game.append(['.'] * self.game_size)
		self.current_state = game
		# Player X always plays first
		self.player_turn = 'X'

		# Generate each blocks
		list_of_blocks = []
		while len(list_of_blocks) != self.game_blocks:
			new_position = (random.randint(0, self.game_size - 1), random.randint(0, self.game_size - 1))
			if new_position not in list_of_blocks:
				list_of_blocks.append(new_position)
		# Place each blocks
		for x, y in list_of_blocks:
			self.current_state[x][y] = '-'
		
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
						if game_state_clone[height + length][row_value + length] == 'O':
							num_tiles += 1
				else:
					# from right to left
					for length in range(1, win_length):
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
				if symbol == '-' and num_tiles < self.win_length:
					num_tiles = 0
			h_score += math.pow(math.copysign(100, num_tiles), num_tiles - self.win_length)
		# Vertical win
		for col in game_state_vertical_clone:
			num_tiles = 0
			for index, symbol in enumerate(col):
				if symbol == 'O':
					num_tiles += 1
				if symbol == 'X':
					num_tiles -= 1
				if symbol == '-' and num_tiles < self.win_length:
					num_tiles = 0
			h_score += math.pow(math.copysign(100, num_tiles), num_tiles - self.win_length)
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
						if game_state_clone[height + length][row_value + length] == 'O':
							num_tiles += 1
						if game_state_clone[height + length][row_value + length] == 'X':
							num_tiles -= 1
						if game_state_clone[height + length][row_value + length] == '-' and num_tiles < self.win_length:
							num_tiles -= 1
				else:
					# from right to left
					for length in range(1, self.win_length):
						if game_state_clone[height + length][row_value - length] == 'O':
							num_tiles += 1
						if game_state_clone[height + length][row_value + length] == 'X':
							num_tiles -= 1
						if game_state_clone[height + length][row_value + length] == '-' and num_tiles < self.win_length:
							num_tiles -= 1
				h_score += math.pow(math.copysign(100, num_tiles), num_tiles - self.win_length)

	
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
				if symbol == '-' or symbol == '.':
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
				if self.current_state[height][row_value] != '.' and self.current_state[height][row_value] != '-':
					potential_winner = self.current_state[height][row_value]
					same_count = 1
					if row_value < math.floor(self.game_size / 2):
						# from left to right
						for length in range(1, self.win_length):
							if potential_winner == self.current_state[height + length][row_value + length]:
								same_count = same_count + 1
								if same_count == self.win_length:
									return potential_winner
					else:
						# from right to left
						for length in range(1, self.win_length):
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
				print('The winner is X!')
				self.logger.write('The winner is X!')
			elif self.result == 'O':
				print('The winner is O!')
				self.logger.write('The winner is O!')
			elif self.result == '.':
				print("It's a tie!")
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
				return (px,py)
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
		value = Game.INITIAL_HEURISTIC_SCORE
		if max:
			value = -Game.INITIAL_HEURISTIC_SCORE
		x = None
		y = None
		result = self.is_end()
		if result == 'X':
			return -1, x, y
		elif result == 'O':
			return 1, x, y
		elif result == '.':
			return 0, x, y

		for i in range(0, self.game_size):
			for j in range(0, self.game_size):
				if self.current_state[i][j] == '.':
					if max:
						self.current_state[i][j] = 'O'
						if current_depth < max_depth:
							(v, _, _) = self.minimax(heuristic, max_depth, max=False, current_depth=current_depth + 1)
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
							(v, _, _) = self.minimax(heuristic, max_depth, max=True, current_depth=current_depth + 1)
						else:
							# run heuristic on this intermediate state (get score for move at this position)
							v = heuristic()
						if v < value:
							value = v
							x = i
							y = j
					self.depths.append(current_depth)
					self.current_state[i][j] = '.'
		return value, x, y

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
		value = Game.INITIAL_HEURISTIC_SCORE
		if max:
			value = -Game.INITIAL_HEURISTIC_SCORE
		x = None
		y = None
		result = self.is_end()
		if result == 'X':
			return -1, x, y
		elif result == 'O':
			return 1, x, y
		elif result == '.':
			return 0, x, y
		for i in range(0, self.game_size):
			for j in range(0, self.game_size):
				if self.current_state[i][j] == '.':
					if max:
						self.current_state[i][j] = 'O'
						if current_depth < max_depth:
							(v, _, _) = self.alphabeta(heuristic, max_depth, alpha, beta, max=False, current_depth=current_depth+1)
						else:
							v = heuristic()
						if v > value:
							value = v
							x = i
							y = j
					else:
						self.current_state[i][j] = 'X'
						if current_depth < max_depth:
							(v, _, _) = self.alphabeta(heuristic, max_depth, alpha, beta, max=True, current_depth=current_depth+1)
						else:
							v = heuristic()
						if v < value:
							value = v
							x = i
							y = j
					self.depths.append(current_depth)
					self.current_state[i][j] = '.'
					if max:
						if value >= beta:
							return value, x, y
						if value > alpha:
							alpha = value
					else:
						if value <= alpha:
							return value, x, y
						if value < beta:
							beta = value
		return value, x, y

	def play(self, algo=None, player_x=None, player_o=None, player_x_heuristic=None, player_o_heuristic=None, player_x_max_depth=5, player_o_max_depth=5):
		if algo is None:
			algo = self.ALPHABETA
		if player_x is None:
			player_x = self.HUMAN
		if player_o is None:
			player_o = self.HUMAN


		self.logger.write(f'Player 1: {player_x} d={player_x_max_depth} a={algo} e={player_x_heuristic.__name__} \n')
		self.logger.write(f'Player 1: {player_o} d={player_o_max_depth} a={algo} e={player_o_heuristic.__name__} \n')
		
		while True:
			self.draw_board()
			if self.check_end():
				return
			start = time.time()
			try:
				self.turn_start_time = start
				if algo == self.MINIMAX:
					if self.player_turn == 'X':
						(_, x, y) = self.minimax(player_x_heuristic, player_x_max_depth, max=False)
					else:
						(_, x, y) = self.minimax(player_o_heuristic, player_o_max_depth, max=True)
				else: # algo == self.ALPHABETA
					if self.player_turn == 'X':
						(m, x, y) = self.alphabeta(player_x_heuristic, player_x_max_depth, max=False)
					else:
						(m, x, y) = self.alphabeta(player_o_heuristic, player_o_max_depth, max=True)
				end = time.time()

			except TimeoutError:
				print("The current AI player ran out of time!")
				print(self.switch_player() + " wins by default!")
				return

			if (self.player_turn == 'X' and player_x == self.HUMAN) or (self.player_turn == 'O' and player_o == self.HUMAN):
					if self.recommend:
						print(F'Evaluation time: {round(end - start, 7)}s')
						print(F'Recommended move: x = {self.alphabet[x]}, y = {y}')
					(x,y) = self.input_move()
					self.logger.write(f'Real Player {self.player_turn} plays: x = {x}, y = {y}\n')
					self.logger.write(f'i Evaluation time: {round(end - start, 7)}s\n')

			if (self.player_turn == 'X' and player_x == self.AI) or (self.player_turn == 'O' and player_o == self.AI):
						print(F'Evaluation time: {round(end - start, 7)}s')
						print(F'Player {self.player_turn} under AI control plays: x = {self.alphabet[x]}, y = {y}')

						self.logger.write(f'Player {self.player_turn} under AI control plays: x = {self.alphabet[x]}, y = {y}\n')
						self.logger.write(f'i Evaluation time: {round(end - start, 7)}s\n')
			
			# average depth
			avg_depth = sum(self.depths) / len(self.depths)
			self.logger.write(f'iv Average Evaluation Depth (AD) is: {avg_depth}\n')
			self.depths = []

			self.current_state[x][y] = self.player_turn
			self.switch_player()


def main():
	# Uncomment when needed
	# game_size = 0
	# while game_size < 3 or game_size > 10:
	# 	game_size = int(input(f'Please enter the game size: '))
	# 	if game_size < 3 or game_size > 10:
	# 		print(f'Game\'s size must be between 3 and 10')
	#
	# blocks = -1
	# while blocks < 0 or blocks > (game_size * 2):
	# 	blocks = int(input(f'Please enter the block amount: '))
	# 	if blocks < 0 or blocks > (game_size * 2):
	# 		print(f'Number of blocks must be between 0 and {game_size * 2}')
	#
	# win_length = 0
	# while win_length < 3 or win_length > game_size:
	# 	win_length = int(input(f'Please enter the win length: '))
	# 	if win_length < 3 or win_length > game_size:
	# 		print(f'Win length must be between 3 and {game_size}')
	# g = Game(recommend=True, game_size=game_size, blocks=blocks, win_length=win_length)
	try:
		g = Game(recommend=True, blocks=1, game_size=3)
		g.play(algo=Game.ALPHABETA, player_x=Game.AI, player_o=Game.AI, player_o_heuristic=g.h1_num_own_tiles, player_x_heuristic=g.h1_num_own_tiles)
	finally:
		g.logger.close()
	# g.play(algo=Game.MINIMAX, player_x=Game.AI, player_o=Game.HUMAN)
