from django.db.models import Max
from django.utils import timezone
from rest_framework import mixins, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from game.models import Game, Player, Ship, Turn
from game.permissions import IsOneOfPlayers, IsOwner, IsPlayer
from game.serializers import (
    GameSerializer, PlayerSerializer, ShipSerializer, TurnSerializer)


class CreateReadViewSet(mixins.CreateModelMixin, ReadOnlyModelViewSet):
    """Viewset where only create and read are allowed"""


class CreateDeleteReadViewSet(mixins.CreateModelMixin,
                              mixins.DestroyModelMixin, ReadOnlyModelViewSet):
    """Viewset where all but update are allowed"""


class GameViewSet(CreateReadViewSet):
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticated, IsOneOfPlayers]

    def get_queryset(self, *args, **kwargs):
        return Game.objects.filter(players__user=self.request.user).distinct()

    def perform_create(self, serializer):
        super().perform_create(serializer)

        Player.objects.create(
            game=serializer.instance,
            user=self.request.user,
        )


class PlayerViewSet(CreateDeleteReadViewSet):
    permission_classes = [IsAuthenticated, IsOwner]
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

    def destroy(self, request, *args, **kwargs):
        player = self.get_object()
        if player.game.has_started():
            raise PermissionDenied(
                detail="Can't remove player after the game has started")

        return super().destroy(request, *args, **kwargs)


class ShipViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsPlayer]
    queryset = Ship.objects.all()
    serializer_class = ShipSerializer

    def perform_create(self, serializer):
        super().perform_create(serializer)

        game = serializer.instance.player.game
        if game.are_all_ships_placed():
            game.started_at = timezone.now()
            game.save()

    def destroy(self, request, *args, **kwargs):
        ship = self.get_object()
        if ship.player.game.has_started():
            raise PermissionDenied(detail="Can't remove ships after the game has started")

        return super().destroy(request, *args, **kwargs)


class TurnViewSet(CreateReadViewSet):
    permission_classes = [IsAuthenticated, IsPlayer]
    queryset = Turn.objects.all()
    serializer_class = TurnSerializer

    def perform_create(self, serializer):
        max_number = Turn.objects.filter(
            player=serializer.validated_data['player']).aggregate(
            Max('number'))['number__max']
        if not max_number:
            max_number = 0
        # TODO: possible race condition
        serializer.validated_data['number'] = max_number + 1
        serializer.save()

        turn = serializer.instance
        game = turn.player.game

        ship = game.is_hit(turn)
        if ship:
            serializer.instance.hit = True

            if game.announce_sinking and game.will_sink(turn=turn, ship=ship):
                serializer.instance.sank_ship = ship

            serializer.instance.save()
