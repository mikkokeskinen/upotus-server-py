import uuid

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
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

    def has_started(self):
        return self.started_at is not None

    def has_ended(self):
        return self.ended_at is not None

    def is_hit(self, turn):
        if not self.started_at:
            return False

        other_player = [p for p in self.players.all() if p != turn.player][0]
        for ship in other_player.ships.all():
            if (turn.x, turn.y) in ship.get_coordinates():
                return ship

        return False

    def will_sink(self, turn, ship):
        if not self.started_at:
            return False

        ship_coords = ship.get_coordinates()
        existing_hits = set(
            (t.x, t.y) for t in turn.player.turns.exclude(id=turn.id)
            if (t.x, t.y) in ship_coords
        )

        return ship_coords.difference(existing_hits) == {(turn.x, turn.y)}

    def are_all_ships_placed(self):
        ship_count = 0
        for player in self.players.all():
            ship_count += player.ships.count()

        return ship_count == 10


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
    x = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(9)])
    y = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(9)])
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

    def is_valid_coordinates(self):
        for coordinate in self.get_coordinates():
            if coordinate[0] >= 10 or coordinate[1] >= 10:
                return False

        return True


class Turn(models.Model):
    player = models.ForeignKey(Player, verbose_name=_("Player"), related_name='turns', on_delete=models.CASCADE)
    number = models.IntegerField()
    x = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(9)])
    y = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(9)])
    hit = models.BooleanField(default=False)
    sank_ship = models.OneToOneField(Ship, verbose_name=_("Sank ship"), related_name='sink_turn', null=True,
                                     blank=True, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("player", "number"), ("player", "x", "y"))
