import random

from django.contrib.auth import get_user_model
from django.db import connection, transaction
from django.utils import timezone
from rest_framework import mixins, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
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
            game.starting_player = random.choice(game.players.all())
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

    @transaction.atomic
    def perform_create(self, serializer):
        with connection.cursor() as cursor:
            cursor.execute('LOCK TABLE {}'.format(Turn._meta.db_table))

        max_number = serializer.validated_data['player'].game.get_max_turn_number()

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

        game.check_for_winner()


def generate_guest_username():
    username = 'guest{:06d}'.format(random.randrange(0, 999999))
    user_class = get_user_model()

    while user_class.objects.filter(username=username).exists():
        username = 'guest{:06d}'.format(random.randrange(0, 999999))

    return username


class CreateUser(APIView):
    @transaction.atomic
    def post(self, request, format=None):
        user_class = get_user_model()

        with connection.cursor() as cursor:
            cursor.execute('LOCK TABLE {}'.format(user_class._meta.db_table))

        username = request.data.get('username')
        if not username:
            username = generate_guest_username()

        password = request.data.get('password')
        if not password:
            password = user_class.objects.make_random_password()

        user = user_class.objects.create_user(username=username, password=password, email=None)

        result = {
            "username": user.username,
            "password": password,
        }

        return Response(result)
