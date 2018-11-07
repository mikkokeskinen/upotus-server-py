import pytest

from game.enums import ShipType, Orientation


@pytest.mark.django_db
def test_are_ships_placed_no_ships(django_user_model, create_game,
                                   create_player):
    user1 = django_user_model.objects.create_user(
        username='test1', password='test1')
    game = create_game()
    player1 = create_player(
        game=game,
        user=user1,
    )

    assert player1.are_ships_placed() is False


@pytest.mark.django_db
def test_are_ships_placed_two_ships(django_user_model, create_game,
                                    create_player, create_ship):
    user1 = django_user_model.objects.create_user(
        username='test1', password='test1')
    game = create_game()
    player1 = create_player(
        game=game,
        user=user1,
    )
    create_ship(player=player1, x=0, y=0, orientation=Orientation.HORIZONTAL,
                type=ShipType.CARRIER)
    create_ship(player=player1, x=0, y=1, orientation=Orientation.HORIZONTAL,
                type=ShipType.BATTLESHIP)

    assert player1.are_ships_placed() is False


@pytest.mark.django_db
def test_are_ships_placed_all_ships(django_user_model, create_game,
                                    create_player, create_ship):
    user1 = django_user_model.objects.create_user(
        username='test1', password='test1')
    game = create_game()
    player1 = create_player(
        game=game,
        user=user1,
    )
    create_ship(player=player1, x=0, y=0, orientation=Orientation.HORIZONTAL,
                type=ShipType.CARRIER)
    create_ship(player=player1, x=0, y=1, orientation=Orientation.HORIZONTAL,
                type=ShipType.BATTLESHIP)
    create_ship(player=player1, x=0, y=2, orientation=Orientation.HORIZONTAL,
                type=ShipType.DESTROYER)
    create_ship(player=player1, x=0, y=3, orientation=Orientation.HORIZONTAL,
                type=ShipType.SUBMARINE)
    create_ship(player=player1, x=0, y=4, orientation=Orientation.HORIZONTAL,
                type=ShipType.PATROL_BOAT)

    assert player1.are_ships_placed() is True
