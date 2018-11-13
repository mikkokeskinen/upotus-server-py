import argparse
import re

from django.core.management.base import BaseCommand, CommandError
from game.models import Game, Ship, Turn

BOARD_SIDE_LENGTH = 10


def uuid_type(value):
    uuid_pattern = re.compile(
        r'^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z', re.I)

    if not uuid_pattern.match(value):
        raise argparse.ArgumentTypeError('game_id is not an uuid')

    return value


def xy_to_i(x, y):
    return y * BOARD_SIDE_LENGTH + x


def board_as_string(board):
    result = '{}{}{}'.format('╔', '═' * BOARD_SIDE_LENGTH, '╗\n')

    for y in range(0, BOARD_SIDE_LENGTH):
        result += '║'
        for x in range(0, BOARD_SIDE_LENGTH):
            result += board[xy_to_i(x, y)]
        result += '║\n'

    result += '{}{}{}'.format('╚', '═' * BOARD_SIDE_LENGTH, '╝\n')

    return result

class Command(BaseCommand):
    help = 'Print game state'

    def add_arguments(self, parser):
        parser.add_argument('game_id', type=uuid_type)

    def handle(self, *args, **options):
        try:
            game = Game.objects.get(pk=options['game_id'])
        except Game.DoesNotExist:
            raise CommandError('Game "{}" does not exist'.format(
                options['game_id']))

        self.stdout.write('Game: {}'.format(options['game_id']))

        players = list(game.players.all())

        for player in players:
            other_player = [p for p in players if p != player][0]

            self.stdout.write('Player: {} ({})'.format(player.user.username, player.id))
            self.stdout.write(' Ships: {}'.format(', '.join([str(s.type) for s in player.ships.all()])))
            self.stdout.write(' Turns: {}'.format(player.turns.count()))

            board = [' '] * (BOARD_SIDE_LENGTH * BOARD_SIDE_LENGTH)

            for ship in player.ships.all():
                for coord in ship.get_coordinates():
                    ship_char = ship.type.value[0].upper()
                    board[xy_to_i(coord[0], coord[1])] = ship_char

            for turn in other_player.turns.all():
                turn_char = 'X' if turn.hit else 'o'
                board[xy_to_i(turn.x, turn.y)] = turn_char

            self.stdout.write(board_as_string(board))
