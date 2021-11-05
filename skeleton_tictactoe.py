# based on code from https://stackabuse.com/minimax-and-alpha-beta-pruning-in-python
import time
import math


class Game:
	MINIMAX = 0
	ALPHABETA = 1
	HUMAN = 2
	AI = 3

	# n = game_size, b = blocks, s = win_length
	def __init__(self, recommend = True, game_size = 3, blocks = 0, win_length = 3):
		self.game_size = game_size
		self.game_blocks = blocks
		self.win_length = win_length
		self.initialize_game()
		self.recommend = recommend

	def initialize_game(self):
		game = []
		for i in range(self.game_size):
			game.append(['.'] * self.game_size)
		self.current_state = game
		# Player X always plays first
		self.player_turn = 'X'

	def draw_board(self):
		print()
		for y in range(0, self.game_size):
			for x in range(0, self.game_size):
				print(F'{self.current_state[x][y]}', end="")
			print()
		print()
		
	def is_valid(self, px, py):
		if px < 0 or px > self.game_size - 1 or py < 0 or py > self.game_size - 1:
			return False
		elif self.current_state[px][py] != '.':
			return False
		else:
			return True

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

				if symbol == 'block' or symbol == '.':
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
				if skip_number and row_value == skip_number:
					continue
				if self.current_state[height][row_value] != '.' and self.current_state[height][row_value] != 'break':
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
			elif self.result == 'O':
				print('The winner is O!')
			elif self.result == '.':
				print("It's a tie!")
			self.initialize_game()
		return self.result

	def input_move(self):
		while True:
			print(F'Player {self.player_turn}, enter your move:')
			px = int(input('enter the x coordinate: '))
			py = int(input('enter the y coordinate: '))
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

	def minimax(self, max=False):
		# Minimizing for 'X' and maximizing for 'O'
		# Possible values are:
		# -1 - win for 'X'
		# 0  - a tie
		# 1  - loss for 'X'
		# We're initially setting it to 2 or -2 as worse than the worst case:
		value = 2
		if max:
			value = -2
		x = None
		y = None
		result = self.is_end()
		if result == 'X':
			return (-1, x, y)
		elif result == 'O':
			return (1, x, y)
		elif result == '.':
			return (0, x, y)
		for i in range(0, self.game_size):
			for j in range(0, self.game_size):
				if self.current_state[i][j] == '.':
					if max:
						self.current_state[i][j] = 'O'
						(v, _, _) = self.minimax(max=False)
						if v > value:
							value = v
							x = i
							y = j
					else:
						self.current_state[i][j] = 'X'
						(v, _, _) = self.minimax(max=True)
						if v < value:
							value = v
							x = i
							y = j
					self.current_state[i][j] = '.'
		return (value, x, y)

	def alphabeta(self, alpha=-2, beta=2, max=False):
		# Minimizing for 'X' and maximizing for 'O'
		# Possible values are:
		# -1 - win for 'X'
		# 0  - a tie
		# 1  - loss for 'X'
		# We're initially setting it to 2 or -2 as worse than the worst case:
		value = 2
		if max:
			value = -2
		x = None
		y = None
		result = self.is_end()
		if result == 'X':
			return (-1, x, y)
		elif result == 'O':
			return (1, x, y)
		elif result == '.':
			return (0, x, y)
		for i in range(0, self.game_size):
			for j in range(0, self.game_size):
				if self.current_state[i][j] == '.':
					if max:
						self.current_state[i][j] = 'O'
						(v, _, _) = self.alphabeta(alpha, beta, max=False)
						if v > value:
							value = v
							x = i
							y = j
					else:
						self.current_state[i][j] = 'X'
						(v, _, _) = self.alphabeta(alpha, beta, max=True)
						if v < value:
							value = v
							x = i
							y = j
					self.current_state[i][j] = '.'
					if max: 
						if value >= beta:
							return (value, x, y)
						if value > alpha:
							alpha = value
					else:
						if value <= alpha:
							return (value, x, y)
						if value < beta:
							beta = value
		return (value, x, y)

	def play(self, algo=None, player_x=None, player_o=None):
		if algo == None:
			algo = self.ALPHABETA
		if player_x == None:
			player_x = self.HUMAN
		if player_o == None:
			player_o = self.HUMAN
		while True:
			self.draw_board()
			if self.check_end():
				return
			start = time.time()
			if algo == self.MINIMAX:
				if self.player_turn == 'X':
					(_, x, y) = self.minimax(max=False)
				else:
					(_, x, y) = self.minimax(max=True)
			else: # algo == self.ALPHABETA
				if self.player_turn == 'X':
					(m, x, y) = self.alphabeta(max=False)
				else:
					(m, x, y) = self.alphabeta(max=True)
			end = time.time()
			if (self.player_turn == 'X' and player_x == self.HUMAN) or (self.player_turn == 'O' and player_o == self.HUMAN):
					if self.recommend:
						print(F'Evaluation time: {round(end - start, 7)}s')
						print(F'Recommended move: x = {x}, y = {y}')
					(x,y) = self.input_move()
			if (self.player_turn == 'X' and player_x == self.AI) or (self.player_turn == 'O' and player_o == self.AI):
						print(F'Evaluation time: {round(end - start, 7)}s')
						print(F'Player {self.player_turn} under AI control plays: x = {x}, y = {y}')
			self.current_state[x][y] = self.player_turn
			self.switch_player()


def main():
	# g = Game(recommend=True, game_size=5, blocks=6, win_length=4)
	g = Game(recommend=True)
	g.play(algo=Game.ALPHABETA, player_x=Game.HUMAN, player_o=Game.HUMAN)
	# g.play(algo=Game.MINIMAX, player_x=Game.AI, player_o=Game.HUMAN)
