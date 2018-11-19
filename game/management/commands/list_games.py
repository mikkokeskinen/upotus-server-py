from django.core.management.base import BaseCommand

from game.models import Game


class Command(BaseCommand):
    help = 'List games'

    def handle(self, *args, **options):
        games = Game.objects.order_by('created_at')

        if not games.count():
            self.stdout.write('No games found.')

        for game in games:
            self.stdout.write('Game:')
            self.stdout.write(' Id: {}'.format(game.id))
            self.stdout.write(' Created at: {}'.format(game.created_at))
            self.stdout.write(' Started at: {}'.format(game.started_at))
            self.stdout.write(' Ended at: {}\n\n'.format(game.ended_at))

            players = list(game.players.all())

            for player in players:
                self.stdout.write(' Player: {} ({})'.format(player.user.username, player.id))
                self.stdout.write('  Joined at: {}'.format(player.joined_at))
                self.stdout.write('  Ships: {}'.format(', '.join([str(s.type) for s in player.ships.all()])))
                self.stdout.write('  Turns: {}'.format(player.turns.count()))

            self.stdout.write('*' * 20)
