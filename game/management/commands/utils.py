import argparse
import re


def uuid_type(value):
    uuid_pattern = re.compile(
        r'^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z', re.I)

    if not uuid_pattern.match(value):
        raise argparse.ArgumentTypeError('game_id is not an uuid')

    return value


def xy_to_i(x, y, side_length):
    return y * side_length + x


def board_as_string(board, side_length):
    result = '{}{}{}'.format('╔', '═' * side_length, '╗\n')

    for y in range(0, side_length):
        result += '║'
        for x in range(0, side_length):
            result += board[xy_to_i(x, y, side_length)]
        result += '║\n'

    result += '{}{}{}'.format('╚', '═' * side_length, '╝\n')

    return result
