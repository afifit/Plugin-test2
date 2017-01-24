#Full Name:afifit
#E-Mail: <dorafifitcohen@gmail.com>
#Time: Tue Jan 24 22:32:55 2017 +0200
#Full Name:afifit
#E-Mail: <dorafifitcohen@gmail.com>
#Time: Tue Jan 24 22:32:55 2017 +0200
# ===============================================================================
# Imports
# ===============================================================================
from math import sqrt

import abstract
from players import simple_player
from utils import MiniMaxWithAlphaBetaPruning, INFINITY, run_with_limited_time, ExceededTimeError
from checkers.consts import EM, PAWN_COLOR, KING_COLOR, OPPONENT_COLOR, MAX_TURNS_NO_JUMP, BACK_ROW, RP, RK, BK, BP, \
    MY_COLORS
import time
from collections import defaultdict

# ===============================================================================
# Globals
# ===============================================================================

# Simple features
KING_WEIGHT = 15
PAWN_WEIGHT = 10
# Layout features
#   Should encourage more kings for the player
DIST_FROM_CROWNING = 0
#   Should encourage defend the back row. Extra bonus for full back row?
BACK_ROW_BONUS = 5
UNOCCUPIED_LINE = None

# Pattern features - not right now
TRIANGLE_SHAPE = None
CLOSENESS_WEIGHT = 5
CLOSE_END_WEIGHT = 2
CROWN_WEIGHT = 10
PIECES_ADVANTAGE = 0.66
CHARGE_WEIGHT = 35
PIECES_THRESHOLD = 11
LONE_WEIGHT = 2
SIDE_WEIGHT = 1
RAN_BACK_ROW_BONUS = 1


# ===============================================================================
# Helper Functions
# ===============================================================================

def piece_distance_from_crowning(state, player):
    '''

    :param
    state: state of the gameboard
    :return: first return value is player score regarding the distance of each piece from promotion
             line, the second return value is the same, but for OTHER_PLAYER.

             The score for each pawn that is located in (row,col) is |row-promotion_line|.
             Note that promotion line is the back row of the opponent.
    '''
    opponent_color = OPPONENT_COLOR[player]
    score = {player: 0, opponent_color: 0}
    for (row, col), piece in state.board.items():
        if piece == PAWN_COLOR[player]:
            score[player] += DIST_FROM_CROWNING * (abs(BACK_ROW[opponent_color] - row))
        if piece == PAWN_COLOR[opponent_color]:
            score[opponent_color] += DIST_FROM_CROWNING * (abs(BACK_ROW[player] - row))
    return score[player], score[opponent_color]


def score_from_back_row(state, player):
    '''
    Gives bonus for pawns in the back row of the player.
     Extra bonus is given for full back row.
    '''
    score = 0
    for (row, col), piece in state.board.items():
        if row == BACK_ROW[OPPONENT_COLOR[player]] and piece in MY_COLORS[player]:
            score += BACK_ROW_BONUS
    if score == BACK_ROW_BONUS * 4:
        score += BACK_ROW_BONUS
    return score


def dist(square, board, color):
    distances = set([])
    for s in board.keys():
        if board[s] == PAWN_COLOR[color] or board[s] == KING_COLOR[color]:
            distances.add(square[0] - s[0] + square[1] - s[1])
    if len(distances) == 0:
        return 0
    return min(distances)


def distOLD(square, board, color):
    distances = set([])
    for s in board.keys():
        if board[s] == PAWN_COLOR[color] or board[s] == KING_COLOR[color]:
            distances.add(square[0] - s[0] + square[1] - s[1])
    if len(distances) == 0:
        return 0

    return sum(distances) / len(distances)


def closeness_to_start(board, color):
    pieces = 0
    distances = 0
    back_row = BACK_ROW[color]
    for square in board:
        if board[square] == PAWN_COLOR[color] or board[square] == KING_COLOR[color]:
            distances += abs(back_row - square[0])
            pieces += 1
    return distances / pieces


def closeness_to_end(board, color):
    my_pieces, op_pieces = 0, 0
    my_distances, op_distances = 0, 0
    opponent_color = OPPONENT_COLOR[color]
    for square in board:
        if board[square] == PAWN_COLOR[color] or board[square] == KING_COLOR[color]:
            my_distances += abs(BACK_ROW[color] - square[1])
            my_pieces += 1
        if board[square] == PAWN_COLOR[opponent_color] or board[square] == KING_COLOR[opponent_color]:
            op_distances += abs(BACK_ROW[opponent_color] - square[1])
            op_pieces += 1
    return (op_distances / op_pieces) - (my_distances / my_pieces)


def pieces_on_sides(board, color):
    """returns the num of pieces on the last & first columns of the player color - same thing of opponent """
    my_pieces, op_pieces = 0, 0
    opponent_color = OPPONENT_COLOR[color]
    for square in board:
        if square[1] == 7 or square[1] == 0:
            if board[square] == PAWN_COLOR[color] or board[square] == KING_COLOR[color]:
                my_pieces += 1
            if board[square] == PAWN_COLOR[opponent_color] or board[square] == KING_COLOR[opponent_color]:
                op_pieces += 1
    return my_pieces - op_pieces


def lone_pieces(board, color):
    my_pieces, op_pieces = 0, 0
    opponent_color = OPPONENT_COLOR[color]
    for square in board:
        if board[square] == PAWN_COLOR[color] or board[square] == KING_COLOR[color]:
            my_pieces += 1 - is_lonely(board, square, color)
        if board[square] == PAWN_COLOR[opponent_color] or board[square] == KING_COLOR[opponent_color]:
            op_pieces += 1 - is_lonely(board, square, opponent_color)
    return my_pieces - op_pieces


def is_lonely(board, square, color):
    row = square[0]
    col = square[1]
    if (row + 1, col + 1) in board and (board[(row + 1, col + 1)] == PAWN_COLOR[color] or board[(row + 1, col + 1)]) == \
            KING_COLOR[color]:
        return 0
    if (row - 1, col - 1) in board and (board[(row - 1, col - 1)] == PAWN_COLOR[color] or board[(row - 1, col - 1)]) == \
            KING_COLOR[color]:
        return 0
    if (row + 1, col - 1) in board and (board[(row + 1, col - 1)] == PAWN_COLOR[color] or board[(row + 1, col - 1)]) == \
            KING_COLOR[color]:
        return 0
    if (row - 1, col + 1) in board and (board[(row - 1, col + 1)] == PAWN_COLOR[color] or board[(row - 1, col + 1)]) == \
            KING_COLOR[color]:
        return 0
    return 1


def center_deviation(board, color):
    my_pieces = 0
    opponent_color = OPPONENT_COLOR[color]
    center = [0, 0]
    for square in board:
        if board[square] == PAWN_COLOR[color] or board[square] == KING_COLOR[color]:
            my_pieces += 1
            center[0] += square[0]
            center[1] += square[1]
    center[0] /= my_pieces
    center[1] /= my_pieces
    sum = 0
    for square in board:
        if board[square] == PAWN_COLOR[color] or board[square] == KING_COLOR[color]:
            sum += (square[0] - center[0]) ** 2

    return sum / my_pieces


def group_distances(board):
    """returns the euclid distance between the two mass centers of pawns"""
    red_mass = [0, 0]
    black_mass = [0, 0]
    red_pieces, black_pieces = 0, 0
    for square in board:
        if board[square] == RP or board[square] == RK:
            red_mass[0] += square[0]
            red_mass[1] += square[1]
            red_pieces += 1
        if board[square] == BP or board[square] == BK:
            black_mass[0] += square[0]
            black_mass[1] += square[1]
            black_pieces += 1
    red_mass[0] /= red_pieces
    red_mass[1] /= red_pieces
    black_mass[0] /= black_pieces
    black_mass[1] /= black_pieces
    return sqrt((black_mass[0] - red_mass[0]) ** 2 + (black_mass[1] - red_mass[1]) ** 2)


# ===============================================================================
# Player
# ===============================================================================

class Player(simple_player.Player):
    def __init__(self, setup_time, player_color, time_per_k_turns, k):
        simple_player.Player.__init__(self, setup_time, player_color, time_per_k_turns, k)

    def utilityOLD(self, state):
        if len(state.get_possible_moves()) == 0:
            return INFINITY if state.curr_player != self.color else -INFINITY
        if state.turns_since_last_jump >= MAX_TURNS_NO_JUMP:
            return 0

        piece_counts = defaultdict(lambda: 0)
        for loc_val in state.board.values():
            if loc_val != EM:
                piece_counts[loc_val] += 1

        opponent_color = OPPONENT_COLOR[self.color]
        my_u = ((PAWN_WEIGHT * piece_counts[PAWN_COLOR[self.color]]) +
                (KING_WEIGHT * piece_counts[KING_COLOR[self.color]]))
        op_u = ((PAWN_WEIGHT * piece_counts[PAWN_COLOR[opponent_color]]) +
                (KING_WEIGHT * piece_counts[KING_COLOR[opponent_color]]))
        if my_u == 0:
            # I have no tools left
            return -INFINITY
        elif op_u == 0:
            # The opponent has no tools left
            return INFINITY
        else:
            my_back_row_bonus = score_from_back_row(state, self.color)
            distance = group_distances(state.board)
            sides = pieces_on_sides(state.board, self.color)
            back_row_param = 1 if op_u > 3 else -1
            return (my_u - op_u) + back_row_param*my_back_row_bonus - CLOSENESS_WEIGHT * distance + back_row_param*SIDE_WEIGHT * sides

    def utility(self, state):
        if len(state.get_possible_moves()) == 0:
            return INFINITY if state.curr_player != self.color else -INFINITY
        if state.turns_since_last_jump >= MAX_TURNS_NO_JUMP:
            return 0

        piece_counts = defaultdict(lambda: 0)
        for loc_val in state.board.values():
            if loc_val != EM:
                piece_counts[loc_val] += 1

        opponent_color = OPPONENT_COLOR[self.color]
        my_u = ((PAWN_WEIGHT * piece_counts[PAWN_COLOR[self.color]]) +
                (KING_WEIGHT * piece_counts[KING_COLOR[self.color]]))
        op_u = ((PAWN_WEIGHT * piece_counts[PAWN_COLOR[opponent_color]]) +
                (KING_WEIGHT * piece_counts[KING_COLOR[opponent_color]]))
        if my_u == 0:
            # I have no tools left
            return -INFINITY
        elif op_u == 0:
            # The opponent has no tools left
            return INFINITY
        else:

        	# if piece_counts[] < 3:
        	# 	#End-Game
        	# if op_u
            my_back_row_bonus = score_from_back_row(state, self.color)
            distance = group_distances(state.board)
            sides = pieces_on_sides(state.board, self.color)
            back_row_param = 1 if piece_counts[KING_COLOR[opponent_color]]  + piece_counts[PAWN_COLOR[opponent_color]] > 6 else 0
            return (my_u - op_u) + back_row_param*my_back_row_bonus - CLOSENESS_WEIGHT * distance + back_row_param*SIDE_WEIGHT * sides

    def __repr__(self):
        return '{} {}'.format(abstract.AbstractPlayer.__repr__(self), 'better_h')

# c:\python35\python.exe run_game.py 3 3 3 y simple_player random_player
