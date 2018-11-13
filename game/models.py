import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _
from enumfields import EnumField

from game.enums import Orientation, ShipType

SHIP_SIZE = {
    'carrier': 5,
    'battleship': 4,
    'destroyer': 3,
    'submarine': 3,
    'patrol_boat': 2,
}


class Game(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    winner = models.ForeignKey('game.Player', verbose_name=_("Winner"), related_name='won_games', null=True, blank=True,
                               on_delete=models.CASCADE)
    announce_sinking = models.BooleanField(default=True)


class Player(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game = models.ForeignKey(Game, verbose_name=_("Game"), related_name='players', on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), verbose_name=_("User"), related_name='players', on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("game", "user"),)

    def are_ships_placed(self):
        return self.ships.count() == 5


class Ship(models.Model):
    player = models.ForeignKey(Player, verbose_name=_("Player"), related_name='ships', on_delete=models.CASCADE)
    type = EnumField(ShipType, max_length=30)
    x = models.IntegerField()
    y = models.IntegerField()
    orientation = EnumField(Orientation, max_length=30)

    class Meta:
        unique_together = (("player", "type"),)

    def get_coordinates(self):
        coordinates = set()
        x_delta = 0
        y_delta = 0

        for i in range(SHIP_SIZE[self.type.value]):
            coordinates.add((self.x + x_delta, self.y + y_delta))

            if self.orientation == Orientation.HORIZONTAL:
                x_delta += 1

            if self.orientation == Orientation.VERTICAL:
                y_delta += 1

        return coordinates

    def overlaps(self, ship):
        return bool(self.get_coordinates() & ship.get_coordinates())

    def overlaps_values(self, type=None, x=None, y=None,
                        orientation=None, **kwargs):
        ship = Ship(type=type, x=x, y=y, orientation=orientation)

        return self.overlaps(ship)


class Turn(models.Model):
    player = models.ForeignKey(Player, verbose_name=_("Player"), related_name='turns', on_delete=models.CASCADE)
    number = models.IntegerField()
    x = models.IntegerField()
    y = models.IntegerField()
    hit = models.BooleanField(default=False)
    sank_ship = models.OneToOneField(Ship, verbose_name=_("Sank ship"), related_name='sink_turn', null=True,
                                     blank=True, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("player", "number"),)
