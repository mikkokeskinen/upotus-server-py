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


class TurnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Turn
        fields = '__all__'
        read_only_fields = ('number', 'hit', 'sank_ship')
