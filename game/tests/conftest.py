import pytest

from game.models import Game, Player, Ship


@pytest.fixture
def create_game():
    def do_create(**kwargs):
        return Game.objects.create(**kwargs)

    return do_create


@pytest.fixture
def create_player():
    def do_create(**kwargs):

        return Player.objects.create(**kwargs)

    return do_create


@pytest.fixture
def create_ship():
    def do_create(**kwargs):

        return Ship.objects.create(**kwargs)

    return do_create
