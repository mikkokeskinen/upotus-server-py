import random

from django.core.management.base import BaseCommand, CommandError

from game.enums import Orientation, ShipType
from game.management.commands.utils import uuid_type
from game.models import Game, Ship

BOARD_SIDE_LENGTH = 10


class Command(BaseCommand):
    help = 'Place remaining ships for all of the players in a game'

    def add_arguments(self, parser):
        parser.add_argument('game_id', type=uuid_type)

    def handle(self, *args, **options):
        try:
            game = Game.objects.get(pk=options['game_id'])
        except Game.DoesNotExist:
            raise CommandError('Game "{}" does not exist'.format(
                options['game_id']))

        self.stdout.write('Game: id: {}'.format(game.id))

        players = list(game.players.all())

        for player in players:

            existing_types = {s.type for s in player.ships.all()}
            missing_types = set(ShipType).difference(existing_types)

            self.stdout.write(' Player: {} ({})'.format(player.user.username, player.id))
            self.stdout.write('  Existing ships: {}'.format(', '.join([str(s.type) for s in player.ships.all()])))
            self.stdout.write('  Missing ships: {}'.format(', '.join([str(st) for st in missing_types])))

            for missing_type in missing_types:
                x = random.randint(0, BOARD_SIDE_LENGTH - 1)
                y = random.randint(0, BOARD_SIDE_LENGTH - 1)
                orientation = random.choice(list(Orientation))

                new_ship = Ship(player=player, type=missing_type, x=x, y=y, orientation=orientation)

                while not new_ship.is_valid_ship_position():
                    x = random.randint(0, BOARD_SIDE_LENGTH - 1)
                    y = random.randint(0, BOARD_SIDE_LENGTH - 1)
                    orientation = random.choice(list(Orientation))

                    new_ship.x = x
                    new_ship.y = y
                    new_ship.orientation = orientation

                new_ship.save()
                self.stdout.write('   {}'.format(new_ship))

            self.stdout.write('\n')
