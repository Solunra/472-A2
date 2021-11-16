# run with pypy main.py
import skeleton_tictactoe as ttt


def main():
    ttt.main(game_size=4, blocks=4, block_positions=[(0, 0), (0, 4), (4, 0), (4, 4)], win_length=3, max_execution_time=5, player_x_max_depth=6, player_o_max_depth=6, algo=ttt.Game.MINIMAX)
    ttt.main(game_size=4, blocks=4, block_positions=[(0, 0), (0, 4), (4, 0), (4, 4)], win_length=3, max_execution_time=5, player_x_max_depth=6, player_o_max_depth=6, algo=ttt.Game.ALPHABETA)
    ttt.main(game_size=5, blocks=4, win_length=4, max_execution_time=1, player_x_max_depth=2, player_o_max_depth=6, algo=ttt.Game.ALPHABETA)
    ttt.main(game_size=5, blocks=4, win_length=4, max_execution_time=5, player_x_max_depth=6, player_o_max_depth=6, algo=ttt.Game.ALPHABETA)
    ttt.main(game_size=8, blocks=5, win_length=5, max_execution_time=1, player_x_max_depth=2, player_o_max_depth=6, algo=ttt.Game.ALPHABETA)
    ttt.main(game_size=8, blocks=5, win_length=5, max_execution_time=5, player_x_max_depth=2, player_o_max_depth=6, algo=ttt.Game.ALPHABETA)
    ttt.main(game_size=8, blocks=6, win_length=5, max_execution_time=1, player_x_max_depth=6, player_o_max_depth=6, algo=ttt.Game.ALPHABETA)
    ttt.main(game_size=8, blocks=6, win_length=5, max_execution_time=5, player_x_max_depth=6, player_o_max_depth=6, algo=ttt.Game.ALPHABETA)


if __name__ == '__main__':
    main()
