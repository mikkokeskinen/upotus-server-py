from django.core.management.base import BaseCommand, CommandError

from game.management.commands.utils import board_as_string, uuid_type, xy_to_i
from game.models import Game

BOARD_SIDE_LENGTH = 10


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

        self.stdout.write('Game:')
        self.stdout.write(' Id: {}'.format(game.id))
        self.stdout.write(' Announce sinking: {}'.format(game.announce_sinking))
        self.stdout.write(' Allow draw: {}'.format(game.allow_draw))
        self.stdout.write(' Created at: {}'.format(game.created_at))
        self.stdout.write(' Started at: {}'.format(game.started_at))
        self.stdout.write(' Ended at: {}'.format(game.ended_at))
        self.stdout.write(' Starting player: {} ({})'.format(
            game.starting_player.user if game.starting_player else '-',
            game.starting_player.id if game.starting_player else '-'
        ))
        if game.winner:
            self.stdout.write(' Winner: {} ({})'.format(game.winner.user, game.winner.id))

        self.stdout.write('\n')

        players = list(game.players.all())

        for player in players:
            try:
                other_player = [p for p in players if p != player][0]
            except IndexError:
                other_player = None

            self.stdout.write('Player: {} ({})'.format(player.user.username, player.id))
            self.stdout.write(' Ships: {}'.format(', '.join([str(s.type) for s in player.ships.all()])))
            self.stdout.write(' Turns: {}'.format(player.turns.count()))

            board = [' '] * (BOARD_SIDE_LENGTH * BOARD_SIDE_LENGTH)

            if player:
                for ship in player.ships.all():
                    for coord in ship.get_coordinates():
                        ship_char = ship.type.value[0].upper()
                        board[xy_to_i(coord[0], coord[1], BOARD_SIDE_LENGTH)] = ship_char

            if other_player:
                for turn in other_player.turns.all():
                    turn_char = 'X' if turn.hit else 'o'
                    board[xy_to_i(turn.x, turn.y, BOARD_SIDE_LENGTH)] = turn_char

            self.stdout.write(board_as_string(board, BOARD_SIDE_LENGTH))
