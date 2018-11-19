from enumfields.drf import EnumSupportSerializerMixin
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Game, Player, Ship, Turn


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ('id', 'created_at', 'started_at', 'ended_at', 'winner', 'announce_sinking', 'players')
        read_only_fields = ('created_at', 'started_at', 'ended_at', 'winner', 'players')


class PlayerSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Player
        fields = '__all__'
        read_only_fields = ('joined_at',)

    def validate(self, data):
        user = self.context['request'].user
        game = data['game']

        if game.players.count() > 1:
            raise ValidationError('There can be only two players per game')

        if user in [p.user for p in game.players.all()]:
            raise ValidationError('The two players must be different')

        data['user'] = user

        return data


class ShipSerializer(EnumSupportSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Ship
        fields = ('id', 'player', 'type', 'x', 'y', 'orientation', 'sink_turn')
        read_only_fields = ('sink_turn', )

    def validate(self, data):
        user = self.context['request'].user
        if user != data['player'].user:
            raise ValidationError("Can't add another players ships")

        if data['player'].ships.filter(type=data['type']).exists():
            raise ValidationError("Only one ship per type allowed")

        ship = Ship(**data)

        if not ship.is_valid_coordinates():
            raise ValidationError("Ship cordinates are not valid")

        for existing_ship in data['player'].ships.all():
            if existing_ship.overlaps(ship):
                raise ValidationError("Ships can't overlap")

        if data['player'].game.has_started():
            raise ValidationError("Can't add ships after the game has started")

        return data


class TurnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Turn
        fields = '__all__'
        read_only_fields = ('number', 'hit', 'sank_ship')

    def validate(self, data):
        user = self.context['request'].user
        if user != data['player'].user:
            raise ValidationError("Can't take another players turn")

        game = data['player'].game
        if not game.has_started():
            raise ValidationError("Can't take turns before the game has started")

        if game.has_ended():
            raise ValidationError("Game has already ended")

        latest_turn = game.get_latest_turn()

        if not latest_turn and game.starting_player != data['player']:
            raise ValidationError("The other player is the starting player")

        if latest_turn and latest_turn.player == data['player']:
            raise ValidationError("It's the other players turn")

        if Turn.objects.filter(player=data['player'], x=data['x'], y=data['y']).count():
            raise ValidationError("Can't use same coordinates twice")

        return data
