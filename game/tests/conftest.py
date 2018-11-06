import pytest

from game.models import Game, Player


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
